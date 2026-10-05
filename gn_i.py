import os
J="android/app/src/main/java/online/mytempmail/app"
F={}
def W(p,c): F[p]=c

W(J+"/Config.java","""package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.view.View;
import android.view.ViewGroup;
import android.widget.TextView;
import org.json.JSONObject;
public class Config {
    public static JSONObject j=new JSONObject();
    private static SharedPreferences sp(Context c){ return c.getSharedPreferences("offex",Context.MODE_PRIVATE); }
    private static int lastTs(Context c){ return sp(c).getInt("push_ts",0); }
    private static void setLastTs(Context c,int t){ sp(c).edit().putInt("push_ts",t).apply(); }
    private static boolean shownBanner=false;

    public static void refresh(){
        try { j=new JSONObject(ApiClient.get("/api/app-config")); } catch(Exception e){}
    }

    public static void push(Context c){
        try {
            JSONObject p=j.optJSONObject("push");
            if(p==null) return;
            int ts=p.optInt("ts");
            String body=p.optString("body");
            if(ts<=0||body.isEmpty()) return;
            if(ts<=lastTs(c)) return;
            setLastTs(c,ts);
            Notifier.mail(c, p.optString("title"), body);
        } catch(Exception e){}
    }

    public static void apply(final Activity a){
        refresh();
        push(a);
        updateCheck(a);
        banner(a);
    }

    private static void updateCheck(final Activity a){
        try {
            JSONObject up=j.optJSONObject("update");
            if(up==null) return;
            final String latest=up.optString("latest");
            if(latest.isEmpty()) return;
            if(latest.equals("__VER__")) return;
            final String url=up.optString("url");
            boolean force=up.optBoolean("force");
            AlertDialog.Builder b=new AlertDialog.Builder(a);
            b.setTitle("Update available");
            b.setMessage("Offex Mail "+latest+" aa gaya hai. Naye features ke liye update karo.");
            b.setCancelable(!force);
            b.setPositiveButton("Update now", (d,w)->{ try{ a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }catch(Exception e){} });
            if(!force) b.setNegativeButton("Later", (d,w)->{});
            b.show();
        } catch(Exception e){}
    }

    private static void banner(Activity a){
        try {
            if(shownBanner) return;
            JSONObject an=j.optJSONObject("announcement");
            if(an==null||!an.optBoolean("on")) return;
            String text=an.optString("text");
            if(text.isEmpty()) return;
            View root=a.findViewById(android.R.id.content);
            if(!(root instanceof ViewGroup)) return;
            ViewGroup vg=(ViewGroup)root;
            if(vg.getChildCount()==0) return;
            View first=vg.getChildAt(0);
            if(!(first instanceof ViewGroup)) return;
            TextView tv=new TextView(a);
            tv.setText(text);
            tv.setTextSize(13);
            tv.setTextColor(Color.parseColor("#4B2FD6"));
            tv.setBackgroundColor(Color.parseColor("#EDE8FF"));
            tv.setPadding(36,30,36,30);
            ((ViewGroup)first).addView(tv,0);
            shownBanner=true;
        } catch(Exception e){}
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
            h.postDelayed(task,6000);
        }
        return START_STICKY;
    }
    private void tick(){
        new Thread(()->{
            try { Config.refresh(); Config.push(this); } catch(Exception e){}
            final String addr=Prefs.address();
            if(addr.isEmpty()) return;
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

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("I:",len(F))
