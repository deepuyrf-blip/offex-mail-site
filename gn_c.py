import os
J="android/app/src/main/java/online/mytempmail/app"
os.makedirs(J,exist_ok=True)
MAIN="""package online.mytempmail.app;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import androidx.recyclerview.widget.LinearLayoutManager;
import androidx.recyclerview.widget.RecyclerView;
import org.json.JSONArray;
import org.json.JSONObject;
import java.util.ArrayList;
import java.util.List;
public class MainActivity extends Activity {
    private final Handler ui=new Handler(Looper.getMainLooper());
    private final Handler poll=new Handler(Looper.getMainLooper());
    private EditText nameBox; private Spinner domainBox; private Button createBtn;
    private LinearLayout activeCard; private TextView addrText,countdownText,emptyText;
    private MailAdapter adapter; private final List<Mail> mails=new ArrayList<>();
    private final List<String> domains=new ArrayList<>();
    private Runnable pollTask;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        if(!Prefs.onboarded()){ startActivity(new Intent(this,OnboardingActivity.class)); finish(); return; }
        setContentView(R.layout.activity_main);
        nameBox=findViewById(R.id.nameBox); domainBox=findViewById(R.id.domainBox); createBtn=findViewById(R.id.createBtn);
        activeCard=findViewById(R.id.activeCard); addrText=findViewById(R.id.addrText);
        countdownText=findViewById(R.id.countdownText); emptyText=findViewById(R.id.emptyText);
        RecyclerView list=findViewById(R.id.msgList);
        list.setLayoutManager(new LinearLayoutManager(this));
        adapter=new MailAdapter(mails,this::openMail);
        list.setAdapter(adapter);
        domains.add("Random (auto)");
        domainBox.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,domains));
        createBtn.setOnClickListener(v->createInbox());
        findViewById(R.id.copyBtn).setOnClickListener(v->copyAddr());
        findViewById(R.id.refreshBtn).setOnClickListener(v->loadMessages());
        findViewById(R.id.deleteBtn).setOnClickListener(v->deleteInbox());
        findViewById(R.id.settingsBtn).setOnClickListener(v->startActivity(new Intent(this,AdminActivity.class)));
        loadDomains();
        if(!Prefs.address().isEmpty()){ activeCard.setVisibility(View.VISIBLE); addrText.setText(Prefs.address()); loadMessages(); startPolling(); }
    }
    private void loadDomains(){
        new Thread(()->{
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/status")).optJSONArray("domains");
                if(a!=null){ for(int i=0;i<a.length();i++) domains.add(a.getString(i));
                    ui.post(()->((ArrayAdapter<String>)domainBox.getAdapter()).notifyDataSetChanged()); }
            } catch(Exception e){}
        }).start();
    }
    private void createInbox(){
        createBtn.setEnabled(false); createBtn.setText(R.string.creating);
        final String nm=nameBox.getText().toString().trim();
        final String dm=domainBox.getSelectedItemPosition()==0?"":String.valueOf(domainBox.getSelectedItem());
        new Thread(()->{
            try {
                JSONObject body=new JSONObject(); body.put("custom",nm); body.put("domain",dm);
                JSONObject j=new JSONObject(ApiClient.post("/api/inbox",body.toString()));
                Prefs.setAddress(j.getString("address"));
                Prefs.setExpiresAt(j.optLong("expires_at",0L));
                Prefs.setLastMsgId(0);
                ui.post(()->{
                    createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    activeCard.setVisibility(View.VISIBLE); addrText.setText(Prefs.address()); nameBox.setText("");
                    Toast.makeText(this,"Inbox ready",Toast.LENGTH_SHORT).show();
                    loadMessages(); startPolling();
                });
            } catch(final Exception e){
                ui.post(()->{ createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show(); });
            }
        }).start();
    }
    private void loadMessages(){
        final String addr=Prefs.address();
        if(addr.isEmpty()) return;
        new Thread(()->{
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/inbox/"+addr+"/messages")).optJSONArray("messages");
                final List<Mail> fresh=new ArrayList<>(); int maxId=0;
                if(a!=null) for(int i=0;i<a.length();i++){
                    JSONObject o=a.getJSONObject(i); Mail m=new Mail();
                    m.id=o.optInt("id"); m.sender=o.optString("sender"); m.subject=o.optString("subject");
                    m.receivedAt=o.optString("received_at"); m.otp=o.optString("otp"); m.service=o.optString("service");
                    fresh.add(m); if(m.id>maxId) maxId=m.id;
                }
                final int nm=maxId;
                ui.post(()->{
                    mails.clear(); mails.addAll(fresh); adapter.notifyDataSetChanged();
                    emptyText.setVisibility(mails.isEmpty()?View.VISIBLE:View.GONE);
                    int last=Prefs.lastMsgId();
                    if(nm>last&&last>0&&!mails.isEmpty()) Notifier.mail(this,mails.get(0).sender,mails.get(0).subject);
                    if(nm>last) Prefs.setLastMsgId(nm);
                });
            } catch(Exception e){}
        }).start();
    }
    private void deleteInbox(){
        final String addr=Prefs.address();
        if(addr.isEmpty()) return;
        new Thread(()->{
            try { ApiClient.delete("/api/inbox/"+addr); } catch(Exception e){}
            Prefs.setAddress(""); Prefs.setLastMsgId(0);
            ui.post(()->{ activeCard.setVisibility(View.GONE); mails.clear(); adapter.notifyDataSetChanged();
                emptyText.setVisibility(View.VISIBLE); Toast.makeText(this,"Inbox deleted",Toast.LENGTH_SHORT).show(); });
        }).start();
    }
    private void copyAddr(){
        String a=Prefs.address(); if(a.isEmpty()) return;
        ClipboardManager cm=(ClipboardManager)getSystemService(Context.CLIPBOARD_SERVICE);
        cm.setPrimaryClip(ClipData.newPlainText("address",a));
        Toast.makeText(this,R.string.copied,Toast.LENGTH_SHORT).show();
    }
    private void openMail(Mail m){
        Intent i=new Intent(this,ReaderActivity.class); i.putExtra("id",m.id); startActivity(i);
    }
    private void startPolling(){
        if(pollTask!=null) return;
        pollTask=new Runnable(){ @Override public void run(){ loadMessages(); tick(); poll.postDelayed(this,10000); } };
        poll.postDelayed(pollTask,10000);
    }
    private void tick(){
        long exp=Prefs.expiresAt();
        if(exp<=0){ countdownText.setText(""); return; }
        long left=exp-System.currentTimeMillis()/1000; if(left<0) left=0;
        countdownText.setText(getString(R.string.expires_in)+" "+(left/3600)+"h "+((left%3600)/60)+"m "+(left%60)+"s");
    }
    @Override protected void onResume(){
        super.onResume();
        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); }
    }
}
"""
open(J+"/MainActivity.java","w",encoding="utf-8").write(MAIN)
print("MainActivity written", len(MAIN))
