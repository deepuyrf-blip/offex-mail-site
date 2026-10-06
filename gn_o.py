import os
J="android/app/src/main/java/online/mytempmail/app"
F={}
def W(p,c): F[p]=c

W(J+"/Ads.java","""package online.mytempmail.app;
import android.app.Activity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import org.json.JSONObject;
public class Ads {
    public static final String TEST_BANNER="ca-app-pub-3940256099942544/6300978111";
    public static final String TEST_REWARDED="ca-app-pub-3940256099942544/5224354917";
    private static boolean started=false;
    private static boolean placed=false;
    private static Activity act;

    public static void init(final Activity a){
        try {
            act=a;
            if(started) return;
            JSONObject ad=Config.j.optJSONObject("ads");
            if(ad==null||!ad.optBoolean("on")) return;
            started=true;
            MobileAds.initialize(a, s->{
                try { a.runOnUiThread(()->banner()); } catch(Exception e){}
            });
        } catch(Exception e){}
    }

    private static String unit(String key,String fallback){
        try {
            JSONObject ad=Config.j.optJSONObject("ads");
            String u=ad==null?"":ad.optString(key).trim();
            if(!valid(u)) u=fallback;
            return u;
        } catch(Exception e){ return fallback; }
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

    private static void banner(){
        try {
            if(placed||act==null) return;
            JSONObject ad=Config.j.optJSONObject("ads");
            if(ad==null||!ad.optBoolean("on")) return;
            ViewGroup g=host(act);
            if(g==null) return;
            AdView av=new AdView(act);
            av.setAdSize(AdSize.BANNER);
            av.setAdUnitId(unit("banner",TEST_BANNER));
            g.addView(av,0);
            av.loadAd(new AdRequest.Builder().build());
            placed=true;
        } catch(Exception e){}
    }

    public static void rewarded(final Activity a, final Runnable after){
        final boolean[] ran={false};
        final Runnable go=()->{ if(!ran[0]){ ran[0]=true; try{ after.run(); }catch(Exception e){} } };
        try {
            JSONObject ad=Config.j.optJSONObject("ads");
            if(ad==null||!ad.optBoolean("on")){ go.run(); return; }
            String u=unit("rewarded",TEST_REWARDED);
            RewardedAd.load(a, u, new AdRequest.Builder().build(), new RewardedAdLoadCallback(){
                @Override public void onAdLoaded(RewardedAd r){
                    try {
                        r.setFullScreenContentCallback(new FullScreenContentCallback(){
                            @Override public void onAdDismissedFullScreenContent(){ go.run(); }
                            @Override public void onAdFailedToShowFullScreenContent(AdError e){ go.run(); }
                        });
                        r.show(a, reward->{});
                    } catch(Exception e){ go.run(); }
                }
                @Override public void onAdFailedToLoad(LoadAdError e){ go.run(); }
            });
        } catch(Exception e){ go.run(); }
    }
}
""")

W("android/app/src/main/AndroidManifest.xml","""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <application
        android:name=".App"
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:usesCleartextTraffic="false"
        android:theme="@style/Theme.Offex">
        <meta-data
            android:name="com.google.android.gms.ads.APPLICATION_ID"
            android:value="ca-app-pub-7802179098119853~8006460361" />
        <activity android:name=".OnboardingActivity" android:exported="false" />
        <activity android:name=".MainActivity" android:exported="true" android:launchMode="singleTop" android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ReaderActivity" android:exported="false" />
        <activity android:name=".AdminActivity" android:exported="false" />
        <activity android:name=".AboutActivity" android:exported="false" />
        <activity android:name=".ContactActivity" android:exported="false" />
        <service android:name=".MailService" android:exported="false" android:foregroundServiceType="dataSync" />
    </application>
</manifest>
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("O:",len(F))
