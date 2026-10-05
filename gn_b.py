import os
J="android/app/src/main/java/online/mytempmail/app"
F={}
def W(n,c): F[J+"/"+n]=c

W("App.java","""package online.mytempmail.app;
import android.app.Application;
public class App extends Application {
    @Override public void onCreate(){ super.onCreate(); Prefs.init(this); }
}
""")

W("Prefs.java","""package online.mytempmail.app;
import android.content.Context;
import android.content.SharedPreferences;
public class Prefs {
    private static SharedPreferences sp;
    public static void init(Context c){ sp=c.getSharedPreferences("offex",Context.MODE_PRIVATE); }
    public static boolean onboarded(){ return sp.getBoolean("onboarded",false); }
    public static void setOnboarded(){ sp.edit().putBoolean("onboarded",true).apply(); }
    public static boolean notify(){ return sp.getBoolean("notify",true); }
    public static void setNotify(boolean v){ sp.edit().putBoolean("notify",v).apply(); }
    public static String address(){ return sp.getString("address",""); }
    public static void setAddress(String a){ sp.edit().putString("address",a).apply(); }
    public static long expiresAt(){ return sp.getLong("expires_at",0L); }
    public static void setExpiresAt(long t){ sp.edit().putLong("expires_at",t).apply(); }
    public static int lastMsgId(){ return sp.getInt("last_msg",0); }
    public static void setLastMsgId(int i){ sp.edit().putInt("last_msg",i).apply(); }
}
""")

W("ApiClient.java","""package online.mytempmail.app;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
public class ApiClient {
    public static final String BASE="https://api.mytemp-mail.online";
    public static String get(String p) throws Exception { return call("GET",p,null); }
    public static String post(String p,String b) throws Exception { return call("POST",p,b); }
    public static String delete(String p) throws Exception { return call("DELETE",p,null); }
    private static String call(String m,String p,String body) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL(BASE+p).openConnection();
        c.setRequestMethod(m);
        c.setConnectTimeout(20000);
        c.setReadTimeout(20000);
        c.setRequestProperty("Accept","application/json");
        c.setRequestProperty("Origin","https://mytemp-mail.online");
        c.setRequestProperty("Referer","https://mytemp-mail.online/");
        c.setRequestProperty("User-Agent","OffexMail-Android/2.0");
        if(body!=null){
            c.setDoOutput(true);
            c.setRequestProperty("Content-Type","application/json");
            OutputStream os=c.getOutputStream();
            os.write(body.getBytes(StandardCharsets.UTF_8));
            os.flush(); os.close();
        }
        int code=c.getResponseCode();
        BufferedReader r=new BufferedReader(new InputStreamReader(code>=400?c.getErrorStream():c.getInputStream(),StandardCharsets.UTF_8));
        StringBuilder sb=new StringBuilder(); String l;
        while((l=r.readLine())!=null) sb.append(l);
        r.close();
        String out=sb.toString();
        if(code>=400){
            String msg="HTTP "+code;
            int i=out.indexOf("\\\"error\\\"");
            if(i>=0){ int a=out.indexOf('"',i+7)+1; int b=out.indexOf('"',a); if(a>0&&b>a) msg=out.substring(a,b); }
            throw new Exception(msg);
        }
        return out;
    }
}
""")

W("Mail.java","""package online.mytempmail.app;
public class Mail {
    public int id;
    public String sender="", subject="", receivedAt="", otp="", service="";
}
""")

W("MailAdapter.java","""package online.mytempmail.app;
import android.view.LayoutInflater;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import androidx.annotation.NonNull;
import androidx.recyclerview.widget.RecyclerView;
import java.util.List;
public class MailAdapter extends RecyclerView.Adapter<MailAdapter.VH> {
    public interface OnClick { void click(Mail m); }
    private final List<Mail> data; private final OnClick cb;
    public MailAdapter(List<Mail> d, OnClick c){ data=d; cb=c; }
    @NonNull @Override public VH onCreateViewHolder(@NonNull ViewGroup p,int t){
        return new VH(LayoutInflater.from(p.getContext()).inflate(R.layout.item_message,p,false));
    }
    @Override public void onBindViewHolder(@NonNull VH h,int pos){
        Mail m=data.get(pos);
        h.service.setText(m.service==null||m.service.isEmpty()?"MAIL":m.service.toUpperCase());
        h.sender.setText(m.sender);
        h.subject.setText(m.subject);
        h.time.setText(m.receivedAt);
        boolean has=m.otp!=null&&!m.otp.isEmpty();
        h.otp.setVisibility(has?View.VISIBLE:View.GONE);
        h.otp.setText(m.otp);
        h.itemView.setOnClickListener(v->cb.click(m));
    }
    @Override public int getItemCount(){ return data.size(); }
    static class VH extends RecyclerView.ViewHolder {
        TextView service,sender,subject,time,otp;
        VH(View v){ super(v);
            service=v.findViewById(R.id.mService); sender=v.findViewById(R.id.mSender);
            subject=v.findViewById(R.id.mSubject); time=v.findViewById(R.id.mTime);
            otp=v.findViewById(R.id.mOtp); }
    }
}
""")

W("Notifier.java","""package online.mytempmail.app;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.content.Context;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
public class Notifier {
    public static final String CH="offex_mail";
    public static void ensure(Context c){
        if(Build.VERSION.SDK_INT>=Build.VERSION_CODES.O){
            NotificationChannel ch=new NotificationChannel(CH,c.getString(R.string.notif_channel),NotificationManager.IMPORTANCE_HIGH);
            NotificationManager nm=c.getSystemService(NotificationManager.class);
            if(nm!=null) nm.createNotificationChannel(ch);
        }
    }
    public static void mail(Context c,String from,String subject){
        if(!Prefs.notify()) return;
        ensure(c);
        NotificationCompat.Builder b=new NotificationCompat.Builder(c,CH)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle(from==null||from.isEmpty()?"New mail":from)
            .setContentText(subject==null?"":subject)
            .setAutoCancel(true)
            .setPriority(NotificationCompat.PRIORITY_HIGH);
        try { NotificationManagerCompat.from(c).notify(1001,b.build()); } catch(SecurityException e){}
    }
}
""")

W("OnboardingActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.widget.Button;
import android.widget.TextView;
public class OnboardingActivity extends Activity {
    private int step=0;
    private final int[] titles={R.string.ob1_title,R.string.ob2_title,R.string.ob3_title};
    private final int[] bodies={R.string.ob1_body,R.string.ob2_body,R.string.ob3_body};
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_onboarding);
        final TextView title=findViewById(R.id.obTitle), body=findViewById(R.id.obBody), dots=findViewById(R.id.obDots);
        final Button next=findViewById(R.id.obNext);
        findViewById(R.id.obSkip).setOnClickListener(v->{ Prefs.setOnboarded(); go(); });
        render(title,body,dots,next);
        next.setOnClickListener(v->{ step++; if(step>=titles.length){ Prefs.setOnboarded(); go(); } else render(title,body,dots,next); });
    }
    private void go(){ startActivity(new Intent(this,MainActivity.class)); finish(); }
    private void render(TextView t,TextView b,TextView d,Button n){
        t.setText(titles[step]); b.setText(bodies[step]);
        StringBuilder sb=new StringBuilder();
        for(int i=0;i<titles.length;i++) sb.append(i==step?"\\u25CF ":"\\u25CB ");
        d.setText(sb.toString());
        n.setText(step==titles.length-1?R.string.ob_start:R.string.ob_next);
    }
}
""")

W("ReaderActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.text.Html;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
public class ReaderActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_reader);
        final int id=getIntent().getIntExtra("id",0);
        final TextView subject=findViewById(R.id.rSubject), from=findViewById(R.id.rFrom), bodyBox=findViewById(R.id.rBody);
        final Handler ui=new Handler(Looper.getMainLooper());
        new Thread(()->{
            try {
                JSONObject j=new JSONObject(ApiClient.get("/api/message/"+id));
                final String s=j.optString("subject"), f=j.optString("sender"), html=j.optString("html"), txt=j.optString("body");
                ui.post(()->{ subject.setText(s); from.setText(f);
                    if(html!=null&&!html.isEmpty()) bodyBox.setText(Html.fromHtml(html,Html.FROM_HTML_MODE_LEGACY));
                    else bodyBox.setText(txt); });
            } catch(final Exception e){
                ui.post(()->Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show());
            }
        }).start();
    }
}
""")

W("AdminActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.os.Bundle;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
public class AdminActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_admin);
        final EditText code=findViewById(R.id.codeBox);
        final Button unlock=findViewById(R.id.unlockBtn);
        final View panel=findViewById(R.id.panel);
        final Switch notify=findViewById(R.id.notifySwitch);
        final TextView ver=findViewById(R.id.versionText);
        notify.setChecked(Prefs.notify());
        notify.setOnCheckedChangeListener((v,c)->Prefs.setNotify(c));
        ver.setText(getString(R.string.version)+" 2.0");
        unlock.setOnClickListener(v->{
            final String entered=code.getText().toString().trim();
            if(entered.isEmpty()){ Toast.makeText(this,R.string.admin_hint,Toast.LENGTH_SHORT).show(); return; }
            new Thread(()->{
                try {
                    JSONObject body=new JSONObject(); body.put("code",entered);
                    ApiClient.post("/api/auth",body.toString());
                    runOnUiThread(()->{ panel.setVisibility(View.VISIBLE); code.setVisibility(View.GONE); unlock.setVisibility(View.GONE); });
                } catch(final Exception e){
                    runOnUiThread(()->Toast.makeText(this,R.string.wrong_code,Toast.LENGTH_SHORT).show());
                }
            }).start();
        });
    }
}
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("B:",len(F))
