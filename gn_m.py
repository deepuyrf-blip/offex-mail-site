import os
J="android/app/src/main/java/online/mytempmail/app"
os.makedirs(J,exist_ok=True)
CFG = """package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;
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
        try {
            new Thread(()->{
                refresh();
                try {
                    a.runOnUiThread(()->{
                        try { push(a); } catch(Exception e){}
                        try { updateCheck(a); } catch(Exception e){}
                        try { banner(a); } catch(Exception e){}
                        try { Ads.init(a); } catch(Exception e){}
                    });
                } catch(Exception e){}
            }).start();
        } catch(Exception e){}
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

    private static ViewGroup host(Activity a){
        try {
            View root=a.findViewById(android.R.id.content);
            if(!(root instanceof ViewGroup)) return null;
            ViewGroup vg=(ViewGroup)root;
            if(vg.getChildCount()==0) return null;
            View first=vg.getChildAt(0);
            if(!(first instanceof ViewGroup)) return null;
            ViewGroup g=(ViewGroup)first;
            if(g instanceof ScrollView && g.getChildCount()>0 && g.getChildAt(0) instanceof ViewGroup){
                g=(ViewGroup)g.getChildAt(0);
            }
            return g;
        } catch(Exception e){ return null; }
    }

    private static void banner(Activity a){
        try {
            if(shownBanner) return;
            JSONObject an=j.optJSONObject("announcement");
            if(an==null||!an.optBoolean("on")) return;
            String text=an.optString("text");
            if(text.isEmpty()) return;
            ViewGroup g=host(a);
            if(g==null) return;
            TextView tv=new TextView(a);
            tv.setText(text);
            tv.setTextSize(13);
            tv.setTextColor(Color.parseColor("#4B2FD6"));
            tv.setBackgroundColor(Color.parseColor("#EDE8FF"));
            tv.setPadding(36,30,36,30);
            g.addView(tv,0);
            shownBanner=true;
        } catch(Exception e){}
    }
}
"""
open(J+"/Config.java","w",encoding="utf-8").write(CFG)
print("M Config.java written", len(CFG))
