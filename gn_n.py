import os
J="android/app/src/main/java/online/mytempmail/app"
os.makedirs(J,exist_ok=True)
SVC = """package online.mytempmail.app;
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
    private static final long MAIL_MS = 30000L;
    private static final long CONFIG_MS = 180000L;
    private final Handler h=new Handler(Looper.getMainLooper());
    private Runnable task;
    private long lastConfig=0;
    @Override public int onStartCommand(Intent i,int f,int s){
        Notifier.ensure(this);
        Notification n=new NotificationCompat.Builder(this,Notifier.CH)
            .setSmallIcon(R.mipmap.ic_launcher)
            .setContentTitle("Offex Mail")
            .setContentText("Watching your inbox for new mail")
            .setOngoing(true).setPriority(NotificationCompat.PRIORITY_MIN).build();
        try { startForeground(2,n); } catch(Exception e){}
        if(task==null){
            task=new Runnable(){ @Override public void run(){ tick(); h.postDelayed(this,MAIL_MS); } };
            h.postDelayed(task,10000);
        }
        return START_STICKY;
    }
    private void tick(){
        new Thread(()->{
            try {
                long now=System.currentTimeMillis();
                if(now-lastConfig>CONFIG_MS){
                    lastConfig=now;
                    Config.refresh();
                    Config.push(this);
                }
            } catch(Exception e){}
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
"""
open(J+"/MailService.java","w",encoding="utf-8").write(SVC)
print("N MailService written", len(SVC))
