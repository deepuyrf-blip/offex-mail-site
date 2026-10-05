import os
J="android/app/src/main/java/online/mytempmail/app"
F={}
def W(p,c): F[p]=c

W(J+"/Prefs.java","""package online.mytempmail.app;
import android.content.Context;
import android.content.SharedPreferences;
public class Prefs {
    private static SharedPreferences sp;
    public static void init(Context c){ sp=c.getSharedPreferences("offex",Context.MODE_PRIVATE); }
    public static boolean onboarded(){ return sp.getBoolean("onboarded",false); }
    public static void setOnboarded(){ sp.edit().putBoolean("onboarded",true).apply(); }
    public static boolean notifyOn(){ return sp.getBoolean("notify",true); }
    public static void setNotify(boolean v){ sp.edit().putBoolean("notify",v).apply(); }
    public static String address(){ return sp.getString("address",""); }
    public static void setAddress(String a){ sp.edit().putString("address",a).apply(); }
    public static long expiresAt(){ return sp.getLong("expires_at",0L); }
    public static void setExpiresAt(long t){ sp.edit().putLong("expires_at",t).apply(); }
    public static int lastMsgId(){ return sp.getInt("last_msg",0); }
    public static void setLastMsgId(int i){ sp.edit().putInt("last_msg",i).apply(); }
    public static String history(){ return sp.getString("history","[]"); }
    public static void setHistory(String j){ sp.edit().putString("history",j).apply(); }
}
""")

W(J+"/Notifier.java","""package online.mytempmail.app;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.media.AudioAttributes;
import android.media.RingtoneManager;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
public class Notifier {
    public static final String CH="offex_mail";
    public static void ensure(Context c){
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.O){
            NotificationChannel ch=new NotificationChannel(CH,c.getString(R.string.notif_channel),NotificationManager.IMPORTANCE_HIGH);
            ch.enableVibration(true);
            ch.setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION),
                new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).build());
            NotificationManager nm=c.getSystemService(NotificationManager.class);
            if(nm!=null) nm.createNotificationChannel(ch);
        }
    }
    public static void mail(Context c,String from,String subject){
        if(!Prefs.notifyOn()) return;
        ensure(c);
        NotificationCompat.Builder b=new NotificationCompat.Builder(c,CH)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(from==null||from.isEmpty()?"New mail":from)
            .setContentText(subject==null?"":subject)
            .setStyle(new NotificationCompat.BigTextStyle().bigText(subject==null?"":subject))
            .setAutoCancel(true)
            .setDefaults(NotificationCompat.DEFAULT_ALL)
            .setSound(RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION))
            .setPriority(NotificationCompat.PRIORITY_HIGH)
            .setCategory(NotificationCompat.CATEGORY_MESSAGE);
        try { NotificationManagerCompat.from(c).notify(1001,b.build()); } catch(SecurityException e){}
    }
}
""")

W(J+"/MailService.java","""package online.mytempmail.app;
import android.app.Notification;
import android.app.Service;
import android.content.Intent;
import android.os.Handler;
import android.os.IBinder;
import android.os.Looper;
import androidx.core.app.NotificationCompat;
import org.json.JSONArray;
import org.json.JSONObject;
public class MailService extends Service {
    private final Handler h=new Handler(Looper.getMainLooper());
    private Runnable task;
    @Override public int onStartCommand(Intent i,int f,int s){
        Notifier.ensure(this);
        Notification n=new NotificationCompat.Builder(this,Notifier.CH)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("Offex Mail")
            .setContentText("Watching your inbox for new mail")
            .setOngoing(true).setPriority(NotificationCompat.PRIORITY_MIN).build();
        try { startForeground(2,n); } catch(Exception e){}
        if(task==null){
            task=new Runnable(){ @Override public void run(){ tick(); h.postDelayed(this,12000); } };
            h.postDelayed(task,8000);
        }
        return START_STICKY;
    }
    private void tick(){
        final String addr=Prefs.address();
        if(addr.isEmpty()) return;
        new Thread(()->{
            try {
                JSONArray a=new JSONObject(ApiClient.get("/api/inbox/"+addr+"/messages")).optJSONArray("messages");
                if(a==null) return;
                int max=0; JSONObject top=null;
                for(int k=0;k<a.length();k++){ JSONObject o=a.getJSONObject(k); int id=o.optInt("id"); if(id>max){ max=id; top=o; } }
                int last=Prefs.lastMsgId();
                if(max>last&&last>0&&top!=null) Notifier.mail(this,top.optString("sender"),top.optString("subject"));
                if(max>last) Prefs.setLastMsgId(max);
            } catch(Exception e){}
        }).start();
    }
    @Override public IBinder onBind(Intent i){ return null; }
}
""")

W(J+"/MainActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.content.ClipData;
import android.content.ClipboardManager;
import android.content.Context;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Color;
import android.graphics.Typeface;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
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
    private LinearLayout activeCard, historyBox; private TextView addrText,countdownText,emptyText,historyEmpty;
    private MailAdapter adapter; private final List<Mail> mails=new ArrayList<>();
    private final List<String> domains=new ArrayList<>();
    private Runnable pollTask;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        if(!Prefs.onboarded()){ startActivity(new Intent(this,OnboardingActivity.class)); finish(); return; }
        setContentView(R.layout.activity_main);
        askNotify();
        nameBox=findViewById(R.id.nameBox); domainBox=findViewById(R.id.domainBox); createBtn=findViewById(R.id.createBtn);
        activeCard=findViewById(R.id.activeCard); addrText=findViewById(R.id.addrText);
        countdownText=findViewById(R.id.countdownText); emptyText=findViewById(R.id.emptyText);
        historyBox=findViewById(R.id.historyBox); historyEmpty=findViewById(R.id.historyEmpty);
        RecyclerView list=findViewById(R.id.msgList);
        list.setLayoutManager(new LinearLayoutManager(this));
        adapter=new MailAdapter(mails,this::openMail);
        list.setAdapter(adapter);
        domains.add("Random (auto)");
        domainBox.setAdapter(new ArrayAdapter<>(this,android.R.layout.simple_spinner_dropdown_item,domains));
        createBtn.setOnClickListener(v->createInbox());
        findViewById(R.id.copyBtn).setOnClickListener(v->copyAddr());
        findViewById(R.id.refreshBtn).setOnClickListener(v->loadMessages());
        findViewById(R.id.deleteBtn).setOnClickListener(v->deleteActive());
        findViewById(R.id.settingsBtn).setOnClickListener(v->startActivity(new Intent(this,AdminActivity.class)));
        loadDomains();
        renderHistory();
        if(!Prefs.address().isEmpty()){ activeCard.setVisibility(View.VISIBLE); addrText.setText(Prefs.address()); loadMessages(); startPolling(); }
    }
    private void askNotify(){
        if(Build.VERSION.SDK_INT>=33 && checkSelfPermission("android.permission.POST_NOTIFICATIONS")!=PackageManager.PERMISSION_GRANTED){
            requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"},77);
        }
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
                final String addr=j.getString("address");
                final long exp=j.optLong("expires_at",0L);
                addHistory(addr,exp);
                Prefs.setAddress(addr); Prefs.setExpiresAt(exp); Prefs.setLastMsgId(0);
                ui.post(()->{
                    createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    activeCard.setVisibility(View.VISIBLE); addrText.setText(addr); nameBox.setText("");
                    mails.clear(); adapter.notifyDataSetChanged();
                    Toast.makeText(this,"Inbox ready",Toast.LENGTH_SHORT).show();
                    renderHistory(); loadMessages(); startPolling(); startService();
                });
            } catch(final Exception e){
                ui.post(()->{ createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);
                    Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show(); });
            }
        }).start();
    }
    private void addHistory(String addr,long exp){
        try {
            JSONArray a=new JSONArray(Prefs.history());
            JSONArray out=new JSONArray();
            JSONObject o=new JSONObject(); o.put("a",addr); o.put("e",exp); out.put(o);
            for(int i=0;i<a.length();i++){ JSONObject x=a.getJSONObject(i); if(!addr.equals(x.optString("a"))&&out.length()<20) out.put(x); }
            Prefs.setHistory(out.toString());
        } catch(Exception e){}
    }
    private void removeHistory(String addr){
        try {
            JSONArray a=new JSONArray(Prefs.history()); JSONArray out=new JSONArray();
            for(int i=0;i<a.length();i++){ JSONObject x=a.getJSONObject(i); if(!addr.equals(x.optString("a"))) out.put(x); }
            Prefs.setHistory(out.toString());
        } catch(Exception e){}
    }
    private void renderHistory(){
        historyBox.removeAllViews();
        try {
            JSONArray a=new JSONArray(Prefs.history());
            historyEmpty.setVisibility(a.length()==0?View.VISIBLE:View.GONE);
            String cur=Prefs.address();
            for(int i=0;i<a.length();i++){
                final JSONObject o=a.getJSONObject(i);
                final String addr=o.optString("a");
                LinearLayout row=new LinearLayout(this);
                row.setOrientation(LinearLayout.HORIZONTAL);
                row.setGravity(Gravity.CENTER_VERTICAL);
                row.setBackgroundResource(R.drawable.bg_card);
                row.setElevation(2f);
                LinearLayout.LayoutParams lp=new LinearLayout.LayoutParams(LinearLayout.LayoutParams.MATCH_PARENT,LinearLayout.LayoutParams.WRAP_CONTENT);
                lp.topMargin=10; row.setLayoutParams(lp);
                row.setPadding(28,26,28,26);
                TextView t=new TextView(this);
                t.setText(addr+(addr.equals(cur)?"  \u2022 active":""));
                t.setTextSize(14); t.setTextColor(Color.parseColor(addr.equals(cur)?"#4B2FD6":"#101227"));
                t.setTypeface(null,Typeface.BOLD);
                LinearLayout.LayoutParams tp=new LinearLayout.LayoutParams(0,LinearLayout.LayoutParams.WRAP_CONTENT,1f);
                t.setLayoutParams(tp);
                TextView del=new TextView(this);
                del.setText("\u2715"); del.setTextSize(16); del.setTextColor(Color.parseColor("#E5484D"));
                del.setPadding(24,0,0,0);
                del.setOnClickListener(v->{ removeHistory(addr); if(addr.equals(Prefs.address())){ Prefs.setAddress(""); Prefs.setLastMsgId(0); activeCard.setVisibility(View.GONE); mails.clear(); adapter.notifyDataSetChanged(); emptyText.setVisibility(View.VISIBLE); } renderHistory(); });
                row.addView(t); row.addView(del);
                row.setOnClickListener(v->{ Prefs.setAddress(addr); Prefs.setExpiresAt(o.optLong("e",0L)); Prefs.setLastMsgId(0);
                    activeCard.setVisibility(View.VISIBLE); addrText.setText(addr); mails.clear(); adapter.notifyDataSetChanged();
                    renderHistory(); loadMessages(); startPolling(); startService(); });
                historyBox.addView(row);
            }
        } catch(Exception e){}
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
    private void deleteActive(){
        final String addr=Prefs.address();
        if(addr.isEmpty()) return;
        new Thread(()->{
            try { ApiClient.delete("/api/inbox/"+addr); } catch(Exception e){}
            removeHistory(addr);
            Prefs.setAddress(""); Prefs.setLastMsgId(0);
            ui.post(()->{ activeCard.setVisibility(View.GONE); mails.clear(); adapter.notifyDataSetChanged();
                emptyText.setVisibility(View.VISIBLE); renderHistory(); Toast.makeText(this,"Inbox deleted",Toast.LENGTH_SHORT).show(); });
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
    private void startService(){
        try { startForegroundService(new Intent(this,MailService.class)); } catch(Exception e){}
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
        countdownText.setText(getString(R.string.expires_in)+"  "+(left/3600)+"h "+((left%3600)/60)+"m "+(left%60)+"s");
    }
    @Override protected void onResume(){
        super.onResume();
        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }
    }
}
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("F java:",len(F))
