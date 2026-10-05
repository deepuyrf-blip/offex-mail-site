import os
J="android/app/src/main/java/online/mytempmail/app"
os.makedirs(J,exist_ok=True)
ADS = """package online.mytempmail.app;
import android.app.Activity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.MobileAds;
import org.json.JSONObject;
public class Ads {
    public static final String TEST_BANNER="ca-app-pub-3940256099942544/6300978111";
    public static final String TEST_INTER="ca-app-pub-3940256099942544/1033173712";
    private static boolean started=false;
    private static boolean placed=false;
    private static Activity act;

    public static void init(final Activity a){
        try {
            act=a;
            JSONObject ad=Config.j.optJSONObject("ads");
            if(ad==null||!ad.optBoolean("on")) return;
            if(placed) return;
            if(started) return;
            started=true;
            MobileAds.initialize(a, s->{
                try { a.runOnUiThread(()->load()); } catch(Exception e){}
            });
        } catch(Exception e){}
    }

    private static void load(){
        try {
            if(placed||act==null) return;
            JSONObject ad=Config.j.optJSONObject("ads");
            String unit=ad==null?"":ad.optString("banner").trim();
            if(!valid(unit)) unit=TEST_BANNER;
            ViewGroup g=host(act);
            if(g==null) return;
            AdView av=new AdView(act);
            av.setAdSize(AdSize.BANNER);
            av.setAdUnitId(unit);
            g.addView(av,0);
            av.loadAd(new AdRequest.Builder().build());
            placed=true;
        } catch(Exception e){}
    }

    private static boolean valid(String u){
        if(u==null) return false;
        int i=u.indexOf('/');
        if(i<0) return false;
        String tail=u.substring(i+1).trim();
        return tail.length()>=9 && u.startsWith("ca-app-pub-");
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
}
"""
open(J+"/Ads.java","w",encoding="utf-8").write(ADS)
print("L Ads.java written", len(ADS))
