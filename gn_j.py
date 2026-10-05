import os
J="android/app/src/main/java/online/mytempmail/app"
F={}
def W(p,c): F[p]=c

W("android/app/build.gradle","""plugins { id 'com.android.application' }
android {
    namespace 'online.mytempmail.app'
    compileSdk 34
    defaultConfig {
        applicationId "online.mytempmail.app"
        minSdk 24
        targetSdk 34
        versionCode 8
        versionName "2.6"
    }
    buildTypes { release { minifyEnabled false; signingConfig signingConfigs.debug } }
    compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:1.12.0'
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    implementation 'androidx.core:core:1.13.1'
    implementation 'com.google.android.gms:play-services-ads:23.2.0'
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
            android:value="ca-app-pub-3940256099942544~3347511713" />
        <activity android:name=".OnboardingActivity" android:exported="false" />
        <activity android:name=".MainActivity" android:exported="true" android:launchMode="singleTop" android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ReaderActivity" android:exported="false" />
        <activity android:name=".AdminActivity" android:exported="false" />
        <service android:name=".MailService" android:exported="false" android:foregroundServiceType="dataSync" />
    </application>
</manifest>
""")

W(J+"/Ads.java","""package online.mytempmail.app;
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
    private static boolean inited=false;
    private static boolean placed=false;

    public static void init(final Activity a){
        try {
            if(!inited){ MobileAds.initialize(a, s->{}); inited=true; }
            JSONObject ad=Config.j.optJSONObject("ads");
            if(ad==null||!ad.optBoolean("on")) return;
            if(placed) return;
            String unit=ad.optString("banner");
            if(unit.isEmpty()) unit=TEST_BANNER;
            showBanner(a, unit);
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

    private static void showBanner(Activity a,String unit){
        try {
            ViewGroup g=host(a);
            if(g==null) return;
            AdView av=new AdView(a);
            av.setAdUnitId(unit);
            av.setAdSize(AdSize.BANNER);
            g.addView(av);
            av.loadAd(new AdRequest.Builder().build());
            placed=true;
        } catch(Exception e){}
    }
}
""")

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
        refresh();
        push(a);
        updateCheck(a);
        banner(a);
        Ads.init(a);
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
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("J:",len(F))
