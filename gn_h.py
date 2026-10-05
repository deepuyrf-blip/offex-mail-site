import os
J="android/app/src/main/java/online/mytempmail/app"
RES="android/app/src/main/res"
F={}
def W(p,c): F[p]=c

W(J+"/AdminActivity.java","""package online.mytempmail.app;
import android.app.Activity;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.View;
import android.widget.Button;
import android.widget.EditText;
import android.widget.Switch;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.nio.charset.StandardCharsets;
public class AdminActivity extends Activity {
    private final Handler ui=new Handler(Looper.getMainLooper());
    private String code="";
    private EditText codeBox, annText, verText, urlText;
    private Switch annOn, adsOn, forceOn;
    private View panel;
    private TextView statsText;
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        setContentView(R.layout.activity_admin);
        codeBox=findViewById(R.id.codeBox);
        panel=findViewById(R.id.panel);
        annText=findViewById(R.id.annText); verText=findViewById(R.id.verText); urlText=findViewById(R.id.urlText);
        annOn=findViewById(R.id.annOn); adsOn=findViewById(R.id.adsOn); forceOn=findViewById(R.id.forceOn);
        statsText=findViewById(R.id.statsText);
        Button unlock=findViewById(R.id.unlockBtn);
        unlock.setOnClickListener(v->{
            final String entered=codeBox.getText().toString().trim();
            if(entered.isEmpty()){ Toast.makeText(this,R.string.admin_hint,Toast.LENGTH_SHORT).show(); return; }
            new Thread(()->{
                try {
                    JSONObject body=new JSONObject(); body.put("code",entered);
                    ApiClient.post("/api/auth",body.toString());
                    code=entered;
                    ui.post(()->{ panel.setVisibility(View.VISIBLE); codeBox.setVisibility(View.GONE); unlock.setVisibility(View.GONE); load(); });
                } catch(final Exception e){
                    ui.post(()->Toast.makeText(this,R.string.wrong_code,Toast.LENGTH_SHORT).show());
                }
            }).start();
        });
        findViewById(R.id.saveBtn).setOnClickListener(v->save());
    }
    private void load(){
        new Thread(()->{
            try {
                JSONObject j=new JSONObject(ApiClient.get("/api/app-config"));
                JSONObject a=j.optJSONObject("announcement"), ad=j.optJSONObject("ads"),
                           up=j.optJSONObject("update"), st=j.optJSONObject("stats");
                ui.post(()->{
                    if(a!=null){ annOn.setChecked(a.optBoolean("on")); annText.setText(a.optString("text")); }
                    if(ad!=null) adsOn.setChecked(ad.optBoolean("on"));
                    if(up!=null){ verText.setText(up.optString("latest")); urlText.setText(up.optString("url")); forceOn.setChecked(up.optBoolean("force")); }
                    if(st!=null) statsText.setText("Inboxes: "+st.optInt("inboxes")+"   Mails: "+st.optInt("messages"));
                });
            } catch(Exception e){}
        }).start();
    }
    private void save(){
        final JSONObject body=new JSONObject();
        try {
            JSONObject a=new JSONObject(); a.put("on",annOn.isChecked()); a.put("text",annText.getText().toString()); body.put("announcement",a);
            JSONObject ad=new JSONObject(); ad.put("on",adsOn.isChecked()); ad.put("banner",""); ad.put("interstitial",""); body.put("ads",ad);
            JSONObject up=new JSONObject(); up.put("latest",verText.getText().toString().trim());
            up.put("min",""); up.put("url",urlText.getText().toString().trim()); up.put("force",forceOn.isChecked()); body.put("update",up);
        } catch(Exception e){}
        new Thread(()->{
            try {
                postAdmin("/api/admin/app-config", body.toString());
                ui.post(()->Toast.makeText(this,"Saved",Toast.LENGTH_SHORT).show());
            } catch(final Exception e){
                ui.post(()->Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show());
            }
        }).start();
    }
    private String postAdmin(String path,String body) throws Exception {
        HttpURLConnection c=(HttpURLConnection)new URL(ApiClient.BASE+path).openConnection();
        c.setRequestMethod("POST");
        c.setConnectTimeout(20000); c.setReadTimeout(20000);
        c.setDoOutput(true);
        c.setRequestProperty("Content-Type","application/json");
        c.setRequestProperty("Accept","application/json");
        c.setRequestProperty("Origin","https://mytemp-mail.online");
        c.setRequestProperty("Referer","https://mytemp-mail.online/");
        c.setRequestProperty("x-admin-code",code);
        OutputStream os=c.getOutputStream(); os.write(body.getBytes(StandardCharsets.UTF_8)); os.flush(); os.close();
        int st=c.getResponseCode();
        BufferedReader r=new BufferedReader(new InputStreamReader(st>=400?c.getErrorStream():c.getInputStream(),StandardCharsets.UTF_8));
        StringBuilder sb=new StringBuilder(); String l;
        while((l=r.readLine())!=null) sb.append(l);
        r.close();
        if(st>=400) throw new Exception("HTTP "+st);
        return sb.toString();
    }
}
""")

W(RES+"/layout/activity_admin.xml","""<?xml version="1.0" encoding="utf-8"?>
<ScrollView xmlns:android="http://schemas.android.com/apk/res/android"
    xmlns:app="http://schemas.android.com/apk/res-auto"
    android:layout_width="match_parent" android:layout_height="match_parent" android:background="@color/offex_bg">
    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:orientation="vertical" android:padding="18dp">

        <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
            android:text="@string/admin" android:textColor="@color/offex_text" android:textSize="22sp" android:textStyle="bold" />

        <EditText android:id="@+id/codeBox" android:layout_width="match_parent" android:layout_height="52dp"
            android:layout_marginTop="16dp" android:background="@drawable/bg_input" android:hint="@string/admin_hint"
            android:inputType="textPassword" android:paddingStart="16dp" android:paddingEnd="16dp"
            android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />

        <Button android:id="@+id/unlockBtn" android:layout_width="match_parent" android:layout_height="52dp"
            android:layout_marginTop="12dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:backgroundTint="@color/offex_purple" android:textColor="@color/offex_white"
            android:textAllCaps="false" android:textSize="16sp" android:text="@string/unlock" app:cornerRadius="14dp" />

        <LinearLayout android:id="@+id/panel" android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="18dp" android:background="@drawable/bg_card" android:elevation="3dp"
            android:orientation="vertical" android:padding="18dp" android:visibility="gone">

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="Announcement" android:textColor="@color/offex_text" android:textSize="15sp" android:textStyle="bold" />
            <Switch android:id="@+id/annOn" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="Show banner in app" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
            <EditText android:id="@+id/annText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:minHeight="48dp" android:background="@drawable/bg_input" android:hint="Banner message"
                android:inputType="textMultiLine" android:paddingStart="14dp" android:paddingEnd="14dp"
                android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />

            <View android:layout_width="match_parent" android:layout_height="1dp" android:layout_marginTop="16dp" android:background="@color/offex_line" />

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:text="Ads" android:textColor="@color/offex_text" android:textSize="15sp" android:textStyle="bold" />
            <Switch android:id="@+id/adsOn" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="Enable AdMob ads" android:textColor="@color/offex_text_dim" android:textSize="13sp" />

            <View android:layout_width="match_parent" android:layout_height="1dp" android:layout_marginTop="16dp" android:background="@color/offex_line" />

            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:text="App update" android:textColor="@color/offex_text" android:textSize="15sp" android:textStyle="bold" />
            <EditText android:id="@+id/verText" android:layout_width="match_parent" android:layout_height="48dp"
                android:background="@drawable/bg_input" android:hint="Latest version (e.g. 2.4)"
                android:paddingStart="14dp" android:paddingEnd="14dp"
                android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />
            <EditText android:id="@+id/urlText" android:layout_width="match_parent" android:layout_height="48dp"
                android:layout_marginTop="8dp" android:background="@drawable/bg_input" android:hint="Download URL"
                android:inputType="textUri" android:paddingStart="14dp" android:paddingEnd="14dp"
                android:textColorHint="@color/offex_text_dim" android:textColor="@color/offex_text" />
            <Switch android:id="@+id/forceOn" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:text="Force update (block old app)" android:textColor="@color/offex_text_dim" android:textSize="13sp" />

            <Button android:id="@+id/saveBtn" android:layout_width="match_parent" android:layout_height="50dp"
                android:layout_marginTop="14dp" android:insetTop="0dp" android:insetBottom="0dp"
                android:backgroundTint="@color/offex_purple" android:textColor="@color/offex_white"
                android:textAllCaps="false" android:textSize="15sp" android:text="Save" app:cornerRadius="14dp" />

            <TextView android:id="@+id/statsText" android:layout_width="match_parent" android:layout_height="wrap_content"
                android:layout_marginTop="14dp" android:textColor="@color/offex_text_dim" android:textSize="13sp" />
        </LinearLayout>
    </LinearLayout>
</ScrollView>
""")

W(RES+"/values/strings.xml","""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Offex Mail</string>
    <string name="tagline">Temp Mail - Instant Inbox</string>
    <string name="ob1_title">Instant disposable inbox</string>
    <string name="ob1_body">Get a private disposable inbox in one tap - for OTPs, verification links and test emails.</string>
    <string name="ob2_title">New mail notifications</string>
    <string name="ob2_body">The app keeps checking in the background, so you get a notification the moment new mail arrives.</string>
    <string name="ob3_title">Free - No signup</string>
    <string name="ob3_body">No account, no password. Every inbox expires on its own after a while.</string>
    <string name="ob_next">Next</string>
    <string name="ob_start">Get started</string>
    <string name="ob_skip">Skip</string>
    <string name="new_inbox">New inbox</string>
    <string name="hint_name">Name (optional)</string>
    <string name="create_inbox">Create inbox</string>
    <string name="creating">Creating...</string>
    <string name="your_address">Your temporary address</string>
    <string name="copy">Copy</string>
    <string name="refresh">Refresh</string>
    <string name="delete">Delete</string>
    <string name="copied">Address copied</string>
    <string name="messages">Messages</string>
    <string name="history">History</string>
    <string name="history_empty">Your past inboxes will appear here. Tap one to switch back to it.</string>
    <string name="no_messages">No mail yet. Paste this address wherever you need it and mail will land here.</string>
    <string name="notif_on">Notifications</string>
    <string name="notif_channel">New mail</string>
    <string name="admin">Admin panel</string>
    <string name="admin_hint">Admin code</string>
    <string name="unlock">Unlock</string>
    <string name="wrong_code">Wrong code</string>
    <string name="expires_in">Expires in</string>
    <string name="version">Version</string>
</resources>
""")

for rel,c in F.items():
    os.makedirs(os.path.dirname(rel),exist_ok=True)
    open(rel,"w",encoding="utf-8").write(c)
print("H:",len(F))
