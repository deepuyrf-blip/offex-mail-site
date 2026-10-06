import os, re

# ---------------------------------------------------------------------------
# gn_t.py  (runs LAST, after gn_s, in the android.yml pipeline)
#
# Adds an end-to-end Chat / Support feature:
#   1. SupportActivity  - a chat-style support screen. The user picks a
#      category (Bug / Help / Other), types a message and taps Send. The
#      screen auto-attaches useful context (app version, device model,
#      Android version and the active temporary address).
#   2. activity_support.xml + chat bubble drawables - light-theme-first,
#      brand accent, same card / rounded / spacing system as the rest of
#      the app.
#   3. "Chat Support" entry at the top of the existing More menu.
#   4. Reachable on error: the Create-inbox failure dialog now offers a
#      "Contact support" action that opens SupportActivity pre-filled.
#   5. POSTs the payload {message, category, address, version, device} to
#      POST /api/support (identical shape to the backend in Part B).
#   6. Bumps the app version 3.6 -> 3.7.
#
# Everything emitted by gn_a..gn_s is preserved: API endpoints/JSON fields,
# admin-controlled banner/AdMob/rewarded/update prompt, bottom nav
# (Email/Inbox/Switch/More), light theme default, bundled notification
# sounds, the features section, the Create-button loading animation and the
# FCM push code.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def R(p):
    return open(p, encoding="utf-8").read()

# ===========================================================================
# 1 : SupportActivity.java  -> chat-style support screen
# ===========================================================================
SUP = r'''package online.mytempmail.app;
import android.app.Activity;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ArrayAdapter;
import android.widget.Button;
import android.widget.EditText;
import android.widget.LinearLayout;
import android.widget.Spinner;
import android.widget.TextView;
import android.widget.Toast;
import org.json.JSONObject;
public class SupportActivity extends Activity {
    // Self version, kept in step with the release (see android.yml).
    public static final String VERSION = "3.7";
    private final Handler ui = new Handler(Looper.getMainLooper());
    private EditText msgBox; private Spinner catBox; private Button sendBtn, retryBtn;
    private TextView statusText, contextText; private LinearLayout thread;
    private String pendingMessage = null, pendingCategory = null;
    private final String[] CATS = {"Bug", "Help", "Other"};

    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        Skin.apply(this);
        setContentView(R.layout.activity_support);
        msgBox = findViewById(R.id.supMessage);
        catBox = findViewById(R.id.supCategory);
        sendBtn = findViewById(R.id.supSend);
        retryBtn = findViewById(R.id.supRetry);
        statusText = findViewById(R.id.supStatus);
        contextText = findViewById(R.id.supContext);
        thread = findViewById(R.id.supThread);
        catBox.setAdapter(new ArrayAdapter<>(this, android.R.layout.simple_spinner_dropdown_item, CATS));
        contextText.setText(contextLine());
        addBubble(getString(R.string.support_greeting), false);
        try {
            String pre = getIntent().getStringExtra("prefill");
            if(pre != null && !pre.trim().isEmpty()) msgBox.setText(pre);
        } catch(Exception e){}
        sendBtn.setOnClickListener(v -> send());
        retryBtn.setOnClickListener(v -> { if(pendingMessage != null) attempt(pendingMessage, pendingCategory); });
    }

    private String deviceName(){
        try { return (Build.MANUFACTURER + " " + Build.MODEL).trim(); } catch(Exception e){ return "Android"; }
    }

    private String contextLine(){
        String addr = Prefs.address();
        String s = "v" + VERSION + "  \u2022  " + deviceName() + "  \u2022  Android " + Build.VERSION.RELEASE;
        if(addr != null && !addr.isEmpty()) s += "  \u2022  " + addr;
        return s;
    }

    private void send(){
        String m = msgBox.getText().toString().trim();
        if(m.isEmpty()){ Toast.makeText(this, getString(R.string.support_empty), Toast.LENGTH_SHORT).show(); return; }
        attempt(m, String.valueOf(catBox.getSelectedItem()));
    }

    private void attempt(final String message, final String category){
        pendingMessage = message; pendingCategory = category;
        sendBtn.setEnabled(false); retryBtn.setVisibility(View.GONE);
        statusText.setText(getString(R.string.support_sending)); statusText.setTextColor(0xFF5C5875);
        new Thread(() -> {
            try {
                JSONObject body = new JSONObject();
                body.put("message", message);
                body.put("category", category);
                body.put("address", Prefs.address());
                body.put("version", VERSION);
                body.put("device", deviceName());
                ApiClient.post("/api/support", body.toString());
                ui.post(() -> {
                    sendBtn.setEnabled(true);
                    statusText.setText(getString(R.string.support_sent)); statusText.setTextColor(0xFF1DBF73);
                    addBubble(message, true);
                    msgBox.setText(""); pendingMessage = null;
                });
            } catch(final Exception e){
                ui.post(() -> {
                    sendBtn.setEnabled(true);
                    retryBtn.setVisibility(View.VISIBLE);
                    String msg = e.getMessage() == null ? "network error" : e.getMessage();
                    statusText.setText(getString(R.string.support_failed) + msg);
                    statusText.setTextColor(0xFFE5484D);
                });
            }
        }).start();
    }

    private void addBubble(String text, boolean mine){
        try {
            LinearLayout row = new LinearLayout(this);
            row.setOrientation(LinearLayout.HORIZONTAL);
            row.setGravity(mine ? Gravity.END : Gravity.START);
            LinearLayout.LayoutParams rp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            rp.topMargin = dp(10); row.setLayoutParams(rp);
            TextView tv = new TextView(this);
            tv.setText(text); tv.setTextSize(14); tv.setLineSpacing(dp(3), 1f);
            tv.setPadding(dp(16), dp(12), dp(16), dp(12));
            if(mine){ tv.setBackgroundResource(R.drawable.bg_bubble_me); tv.setTextColor(0xFFFFFFFF); }
            else { tv.setBackgroundResource(R.drawable.bg_bubble_them); tv.setTextColor(resolveText()); }
            LinearLayout.LayoutParams tp = new LinearLayout.LayoutParams(
                    ViewGroup.LayoutParams.WRAP_CONTENT, ViewGroup.LayoutParams.WRAP_CONTENT);
            tp.rightMargin = dp(mine ? 0 : 44); tp.leftMargin = dp(mine ? 44 : 0);
            tv.setLayoutParams(tp);
            row.addView(tv);
            thread.addView(row);
        } catch(Exception e){}
    }

    private int dp(int v){ return (int)(getResources().getDisplayMetrics().density * v); }

    private int resolveText(){
        try { android.util.TypedValue tv = new android.util.TypedValue();
            getTheme().resolveAttribute(R.attr.oxText, tv, true); return tv.data; } catch(Exception e){ return 0xFF1B1730; }
    }
}
'''
W(J + "/SupportActivity.java", SUP)

# ===========================================================================
# 2 : layout activity_support.xml  -> chat UI
# ===========================================================================
SUP_XML = r'''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@color/offex_bg" android:orientation="vertical"
    android:padding="16dp" android:fitsSystemWindows="true">

    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:text="@string/support_title" android:textColor="@color/offex_text"
        android:textSize="22sp" android:textStyle="bold" android:fontFamily="sans-serif-black" />
    <TextView android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginTop="6dp" android:text="@string/support_sub"
        android:textColor="@color/offex_text_dim" android:textSize="14sp"
        android:lineSpacingExtra="3dp" />

    <TextView android:id="@+id/supContext"
        android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginTop="12dp" android:background="@drawable/bg_chip"
        android:paddingLeft="14dp" android:paddingRight="14dp"
        android:paddingTop="8dp" android:paddingBottom="8dp"
        android:textColor="?attr/oxChipText" android:textSize="12sp" />

    <ScrollView android:layout_width="match_parent" android:layout_height="0dp"
        android:layout_weight="1" android:layout_marginTop="10dp" android:scrollbars="none">
        <LinearLayout android:id="@+id/supThread"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:orientation="vertical" android:paddingBottom="8dp" />
    </ScrollView>

    <LinearLayout android:layout_width="match_parent" android:layout_height="wrap_content"
        android:layout_marginTop="6dp" android:background="@drawable/bg_card"
        android:elevation="3dp" android:orientation="vertical" android:padding="16dp">

        <Spinner android:id="@+id/supCategory"
            android:layout_width="match_parent" android:layout_height="48dp"
            android:background="@drawable/bg_input" android:paddingLeft="12dp"
            android:paddingRight="12dp" />

        <EditText android:id="@+id/supMessage"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="10dp" android:background="@drawable/bg_input"
            android:gravity="top|start" android:hint="@string/support_hint"
            android:inputType="textMultiLine|textCapSentences" android:minLines="3"
            android:maxLines="6" android:padding="14dp" android:textColor="@color/offex_text"
            android:textColorHint="@color/offex_text_mute" android:textSize="15sp" />

        <androidx.appcompat.widget.AppCompatButton android:id="@+id/supSend"
            android:layout_width="match_parent" android:layout_height="52dp"
            android:layout_marginTop="12dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:background="@drawable/bg_btn_primary" android:text="@string/support_send"
            android:textAllCaps="false" android:textColor="@color/offex_white"
            android:textSize="16sp" android:textStyle="bold" />

        <androidx.appcompat.widget.AppCompatButton android:id="@+id/supRetry"
            android:layout_width="match_parent" android:layout_height="48dp"
            android:layout_marginTop="8dp" android:insetTop="0dp" android:insetBottom="0dp"
            android:background="@drawable/bg_btn_ghost" android:text="@string/support_retry"
            android:textAllCaps="false" android:textColor="@color/offex_text"
            android:textSize="15sp" android:visibility="gone" />

        <TextView android:id="@+id/supStatus"
            android:layout_width="match_parent" android:layout_height="wrap_content"
            android:layout_marginTop="8dp" android:gravity="center"
            android:textColor="@color/offex_text_dim" android:textSize="13sp" />
    </LinearLayout>
</LinearLayout>
'''
W(RES + "/layout/activity_support.xml", SUP_XML)

# ===========================================================================
# 3 : chat bubble drawables
# ===========================================================================
BUBBLE_ME = r'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#E53935" android:centerColor="#D32F2F" android:endColor="#FF6F60" android:angle="0" />
    <corners android:radius="18dp" />
</shape>
'''
BUBBLE_THEM = r'''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="?attr/oxCard" />
    <corners android:radius="18dp" />
    <stroke android:width="1dp" android:color="?attr/oxCardBorder" />
</shape>
'''
W(RES + "/drawable/bg_bubble_me.xml", BUBBLE_ME)
W(RES + "/drawable/bg_bubble_them.xml", BUBBLE_THEM)

# ===========================================================================
# 4 : strings
# ===========================================================================
sp = RES + "/values/strings.xml"
s = R(sp)
if "support_title" not in s:
    add = (
        '    <string name="support_title">Chat Support</string>\n'
        '    <string name="support_sub">Koi dikkat aa gayi? Apna message likh ke bhejo - hum admin panel me dekh kar jaldi help karte hain.</string>\n'
        '    <string name="support_greeting">Hi! Tell us what went wrong and tap Send. Your message reaches our team right away.</string>\n'
        '    <string name="support_hint">Type your message\u2026</string>\n'
        '    <string name="support_send">Send</string>\n'
        '    <string name="support_retry">Retry</string>\n'
        '    <string name="support_sending">Sending\u2026</string>\n'
        '    <string name="support_sent">Sent \u2713</string>\n'
        '    <string name="support_failed">Could not send: </string>\n'
        '    <string name="support_empty">Please type your message first</string>\n'
        '    <string name="support_contact">Contact support</string>\n'
        '    <string name="support_error_title">Something went wrong</string>\n'
    )
    s = s.replace("</resources>", add + "</resources>")
    W(sp, s)
    print("T: strings.xml -> support strings")

# ===========================================================================
# 5 : AndroidManifest -> register SupportActivity
# ===========================================================================
mf = "android/app/src/main/AndroidManifest.xml"
s = R(mf)
if "SupportActivity" not in s:
    s = s.replace(
        '        <activity android:name=".ContactActivity" android:exported="false" />',
        '        <activity android:name=".ContactActivity" android:exported="false" />\n'
        '        <activity android:name=".SupportActivity" android:exported="false" />',
    )
    W(mf, s)
    print("T: manifest -> SupportActivity")
else:
    print("T: manifest already has SupportActivity")

# ===========================================================================
# 6 : Menu.java -> add "Chat Support" as the first More item
# ===========================================================================
MENU = r'''package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;
public class Menu {
    public static void open(final Activity a){
        final String theme = "Theme: " + (Prefs.isDark() ? "Dark" : "Light");
        final String notif = "Notifications: " + (Prefs.notifyOn() ? "ON" : "OFF");
        final String sound = "Notification sound: " + Notifier.SND_NAMES[Notifier.soundIndex()];
        final String[] items = {"Chat Support", "About Offex Mail", "Rate us", "Privacy Policy", "Terms of Use", "Contact us", sound, theme, notif};
        new AlertDialog.Builder(a)
            .setTitle("More")
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a, SupportActivity.class));
                    else if(w==1) a.startActivity(new Intent(a, AboutActivity.class));
                    else if(w==2) openUrl(a,"https://play.google.com/store/apps/details?id=online.mytempmail.app");
                    else if(w==3) openUrl(a,"https://mytemp-mail.online/privacy");
                    else if(w==4) openUrl(a,"https://mytemp-mail.online/terms");
                    else if(w==5) a.startActivity(new Intent(a, ContactActivity.class));
                    else if(w==6) pickSound(a);
                    else if(w==7) { Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); a.recreate(); }
                    else {
                        Prefs.setNotify(!Prefs.notifyOn());
                        if(Prefs.notifyOn()) Notifier.ensure(a);
                        Toast.makeText(a, "Notifications " + (Prefs.notifyOn() ? "ON" : "OFF"), Toast.LENGTH_SHORT).show();
                    }
                } catch(Exception e){}
            })
            .show();
    }
    private static void pickSound(final Activity a){
        try {
            new AlertDialog.Builder(a)
                .setTitle("Notification sound")
                .setSingleChoiceItems(Notifier.SND_NAMES, Notifier.soundIndex(), (d,w)->{ Prefs.setNotifSound(w); Notifier.preview(a, w); })
                .setPositiveButton("Done", (d,w)->{})
                .show();
        } catch(Exception e){}
    }
    private static void openUrl(Activity a,String url){
        try { a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch(Exception e){}
    }
}
'''
W(J + "/Menu.java", MENU)
print("T: Menu.java -> Chat Support entry added to More")

# ===========================================================================
# 7 : MainActivity -> "Contact support" action on the Create-inbox error
# ===========================================================================
mp = J + "/MainActivity.java"
s = R(mp)
old_err = (
    "            } catch(final Exception e){\n"
    "                ui.post(()->{ hideCreateLoading();\n"
    "                    Toast.makeText(this,e.getMessage(),Toast.LENGTH_LONG).show(); });\n"
    "            }\n"
)
new_err = (
    "            } catch(final Exception e){\n"
    "                ui.post(()->{ hideCreateLoading();\n"
    "                    final String em = (e.getMessage()==null) ? \"network error\" : e.getMessage();\n"
    "                    try {\n"
    "                        new android.app.AlertDialog.Builder(this)\n"
    "                            .setTitle(R.string.support_error_title)\n"
    "                            .setMessage(em)\n"
    "                            .setPositiveButton(R.string.support_contact, (d,w)->{\n"
    "                                try { Intent si=new Intent(this, SupportActivity.class);\n"
    "                                      si.putExtra(\"prefill\", \"I hit this error: \"+em);\n"
    "                                      startActivity(si); } catch(Exception x){}\n"
    "                            })\n"
    "                            .setNegativeButton(\"Dismiss\", (d,w)->{})\n"
    "                            .show();\n"
    "                    } catch(Exception x){ Toast.makeText(this, em, Toast.LENGTH_LONG).show(); }\n"
    "                });\n"
    "            }\n"
)
if old_err in s and "SupportActivity" not in s:
    s = s.replace(old_err, new_err)
    W(mp, s)
    print("T: MainActivity -> error dialog with Contact support action")
else:
    print("T: MainActivity error dialog already patched / anchor not found")

# ===========================================================================
# 8 : version strings 3.6 -> 3.7
# ===========================================================================
cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("3.6")', 'latest.equals("3.7")').replace('latest.equals("3.5")', 'latest.equals("3.7")')
W(cp, s)

ab = "android/app/build.gradle"
s = R(ab)
s = re.sub(r"versionCode \d+", "versionCode 27", s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.7"', s)
W(ab, s)

alp = RES + "/layout/activity_about.xml"
if os.path.exists(alp):
    s = R(alp)
    s = s.replace("Version 3.6", "Version 3.7").replace("Version 3.5", "Version 3.7")
    W(alp, s)

print("T: applied v3.7 changes (Chat Support screen + More entry + error action; version 3.6 -> 3.7)")
