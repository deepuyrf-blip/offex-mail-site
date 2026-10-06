import os
J="android/app/src/main/java/online/mytempmail/app"
RES="android/app/src/main/res"
F={}
def W(p,c): F[p]=c

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
            String unit=ad.optString("banner").trim();
            if(!valid(unit)) unit=TEST_BANNER;
            showBanner(a, unit);
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

    private static void showBanner(Activity a,String unit){
        try {
            ViewGroup g=host(a);
            if(g==null) return;
            AdView av=new AdView(a);
            av.setAdUnitId(unit);
            av.setAdSize(AdSize.BANNER);
            g.addView(av,0);
            av.loadAd(new AdRequest.Builder().build());
            placed=true;
        } catch(Exception e){}
    }
}
""")

W(J+"/Menu.java","""package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
public class Menu {
    public static void open(final Activity a){
        final String[] items={"About Offex Mail","Contact us","Admin panel"};
        new AlertDialog.Builder(a)
            .setTitle("Menu")
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a,AboutActivity.class));
                    else if(w==1) a.startActivity(new Intent(a,ContactActivity.class));
                    else a.startActivity(new Intent(a,AdminActivity.class));
                } catch(Exception e){}
            })
            .setNegativeButton("Close", (d,w)->{})
            .show();
    }
}
""")

W(J+"/AboutActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.os.Bundle;
public class AboutActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_about);
    }
}
""")

W(J+"/ContactActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
public class ContactActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_contact);
        findViewById(R.id.mailBtn).setOnClickListener(v->{
            try { startActivity(new Intent(Intent.ACTION_SENDTO, Uri.parse("mailto:support@offexmail.online"))); } catch(Exception e){}
        });
        findViewById(R.id.siteBtn).setOnClickListener(v->{
            try { startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse("https://mytemp-mail.online"))); } catch(Exception e){}
        });
    }
}
""")

W(RES+"/layout/activity_about.xml","""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg" android:scrollbars="none">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="20dp">

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:background="@drawable/bg_header" android:orientation="vertical"
            android:paddingStart="22dp" android:paddingEnd="22dp"
            android:paddingTop="26dp" android:paddingBottom="26dp">
            <TextView android:layout_width="76dp" android:layout_height="76dp"
                android:background="@drawable/bg_logo" android:gravity="center" android:elevation="10dp"
                android:text="@string/glyph_mail" android:textColor="@color/offex_white" android:textSize="32sp" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="16dp" android:text="@string/app_name"
                android:textColor="@color/offex_white" android:textSize="22sp" android:textStyle="bold"
                android:fontFamily="sans-serif-black" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tagline" android:textColor="@color/offex_white_dim" android:textSize="13sp" />
        </LinearLayout>

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="16dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">
            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                android:lineSpacingExtra="6dp" android:textColor="@color/offex_text" android:textSize="14sp"
                android:text="Offex Mail is a free temporary email service. Create a disposable inbox in one tap for OTPs, verification links and test emails - no signup, no password." />
            <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="16dp" android:lineSpacingExtra="6dp"
                android:textColor="@color/offex_text_dim" android:textSize="13sp"
                android:text="Every inbox expires automatically after a while. Nothing is kept forever, and you never have to share your real email address." />
        </LinearLayout>

        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:layout_marginTop="18dp" android:background="@drawable/bg_chip"
            android:paddingStart="14dp" android:paddingEnd="14dp" android:paddingTop="6dp" android:paddingBottom="6dp"
            android:textColor="@color/offex_purple2" android:textSize="12sp" android:textStyle="bold"
            android:text="Version 3.1" />
    </LinearLayout>
</ScrollView>
""")

W(RES+"/layout/activity_contact.xml","""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg" android:scrollbars="none">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="20dp">

        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="Contact us" android:textColor="@color/offex_text" android:textSize="22sp"
            android:textStyle="bold" android:fontFamily="sans-serif-black" />
        <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="8dp" android:textColor="@color/offex_text_dim" android:textSize="14sp"
            android:lineSpacingExtra="4dp"
            android:text="Koi dikkat, sawal ya suggestion? Hum se rabta karo - hum jaldi reply karte hain." />

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="20dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Support email" android:textColor="@color/offex_text_dim" android:textSize="12sp" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="support@offexmail.online" android:textColor="@color/offex_text"
                android:textSize="16sp" android:textStyle="bold" android:textIsSelectable="true" />
            <androidx.appcompat.widget.AppCompatButton android:id="@+id/mailBtn"
                android:layout_width="match_parent" android:layout_height="52dp"
                android:layout_marginTop="16dp" android:insetTop="0dp" android:insetBottom="0dp"
                android:background="@drawable/bg_btn_primary" android:textColor="@color/offex_white"
                android:textAllCaps="false" android:textSize="15sp" android:text="Send email" />
        </LinearLayout>

        <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="14dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="20dp">
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Website" android:textColor="@color/offex_text_dim" android:textSize="12sp" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="mytemp-mail.online" android:textColor="@color/offex_text"
                android:textSize="16sp" android:textStyle="bold" />
            <androidx.appcompat.widget.AppCompatButton android:id="@+id/siteBtn"
                android:layout_width="match_parent" android:layout_height="52dp"
                android:layout_marginTop="16dp" android:insetTop="0dp" android:insetBottom="0dp"
                android:background="@drawable/bg_btn_ghost" android:textColor="@color/offex_text"
                android:textAllCaps="false" android:textSize="15sp" android:text="Open website" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
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
        <activity android:name=".AboutActivity" android:exported="false" />
        <activity android:name=".ContactActivity" android:exported="false" />
        <service android:name=".MailService" android:exported="false" android:foregroundServiceType="dataSync" />
    </application>
</manifest>
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("K premium:",len(F))
