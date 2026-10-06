import os, re, io, wave, struct, math

# ---------------------------------------------------------------------------
# gn_r.py  (runs LAST, after gn_q, in the android.yml pipeline)
#
# Applies the v3.5 changes on top of everything emitted by gn_a..gn_q:
#   1. Move the "Why Offex Mail" features section from the top of the home
#      screen to the BOTTOM of the home screen.
#   2. Bundle 2-3 custom notification sounds (real WAV resources in res/raw)
#      and add a More > Notification sound picker. The phone's default sound
#      is no longer used.
#   3. (admin panel is backend-side, not this repo)
#   4. In-app APK update download (DownloadManager + progress + install).
#   5. REQUEST_INSTALL_PACKAGES + unknown-sources install intent.
#   6. Logo (bundled) as launcher icon + animated loading splash.
#   7. Premium INLINE loading state on the Create button (spinner on the
#      button itself; the old floating loading dialog was removed).
#
# API endpoints, JSON field names and admin-controlled features (announcement
# banner, AdMob banner + rewarded ads, notifications, update prompt) are kept
# exactly. No admin panel is re-added inside the app.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def WB(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(b)

def R(p):
    return open(p, encoding="utf-8").read()

# ===========================================================================
# 2 : Prefs  -> persist the chosen notification sound
# ===========================================================================
pp = J + "/Prefs.java"
s = R(pp)
if "notifSound" not in s:
    s = s.rstrip()
    assert s.endswith("}"), "Prefs.java does not end with }"
    extra = ('    public static int notifSound(){ return sp.getInt("notif_sound",0); }\n'
             '    public static void setNotifSound(int i){ sp.edit().putInt("notif_sound",i).apply(); }\n')
    s = s[:-1].rstrip() + "\n" + extra + "}\n"
    W(pp, s)
    print("R: Prefs notifSound added")
else:
    print("R: Prefs already has notifSound")

# ===========================================================================
# 2 : Notifier  -> custom per-sound channels (phone default sound removed)
# ===========================================================================
NOTIFIER = r'''package online.mytempmail.app;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.AudioAttributes;
import android.media.MediaPlayer;
import android.net.Uri;
import android.os.Build;
import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;
public class Notifier {
    public static final String CH = "offex_mail";
    public static final String CH_SERVICE = "offex_service";
    private static final String[] SND_CH = {"offex_mail_s0","offex_mail_s1","offex_mail_s2"};
    public static final int[] SND_RES = {R.raw.notify_1, R.raw.notify_2, R.raw.notify_3};
    public static final String[] SND_NAMES = {"Chime", "Ding", "Pop"};
    private static int clamp(int i){ if(i < 0 || i >= SND_RES.length) return 0; return i; }
    public static int soundIndex(){ return clamp(Prefs.notifSound()); }
    private static Uri soundUri(Context c, int i){
        return Uri.parse("android.resource://" + c.getPackageName() + "/" + SND_RES[clamp(i)]);
    }
    private static void channels(Context c){
        if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O){
            NotificationManager nm = c.getSystemService(NotificationManager.class);
            if(nm == null) return;
            for(int i = 0; i < SND_CH.length; i++){
                NotificationChannel ch = new NotificationChannel(SND_CH[i],
                        c.getString(R.string.notif_channel) + " - " + SND_NAMES[i],
                        NotificationManager.IMPORTANCE_HIGH);
                ch.enableVibration(true);
                ch.setSound(soundUri(c, i), new AudioAttributes.Builder().setUsage(AudioAttributes.USAGE_NOTIFICATION).build());
                nm.createNotificationChannel(ch);
            }
            NotificationChannel svc = new NotificationChannel(CH_SERVICE, c.getString(R.string.notif_service), NotificationManager.IMPORTANCE_LOW);
            svc.setShowBadge(false);
            nm.createNotificationChannel(svc);
        }
    }
    public static void ensure(Context c){ try { channels(c); } catch(Exception e){} }
    public static boolean enabled(Context c){
        try { return NotificationManagerCompat.from(c).areNotificationsEnabled(); } catch(Exception e){ return true; }
    }
    public static void preview(Context c, int i){
        try {
            MediaPlayer mp = MediaPlayer.create(c, SND_RES[clamp(i)]);
            if(mp != null){
                mp.setOnCompletionListener(m -> { try { mp.release(); } catch(Exception e){} });
                mp.start();
            }
        } catch(Exception e){}
    }
    public static void mail(Context c, String from, String subject){
        if(!Prefs.notifyOn()) return;
        try {
            ensure(c);
            if(!enabled(c)) return;
            int si = soundIndex();
            String chan = (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) ? SND_CH[si] : CH;
            String title = (from == null || from.trim().isEmpty()) ? c.getString(R.string.app_name) : from.trim();
            String text = (subject == null) ? "" : subject;
            Intent open = new Intent(c, MainActivity.class);
            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if(Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
            PendingIntent content = PendingIntent.getActivity(c, 0, open, flags);
            NotificationCompat.Builder b = new NotificationCompat.Builder(c, chan)
                .setSmallIcon(R.mipmap.ic_launcher)
                .setContentTitle(title)
                .setContentText(text)
                .setStyle(new NotificationCompat.BigTextStyle().bigText(text))
                .setContentIntent(content)
                .setAutoCancel(true)
                .setOnlyAlertOnce(false)
                .setSound(soundUri(c, si))
                .setPriority(NotificationCompat.PRIORITY_HIGH)
                .setCategory(NotificationCompat.CATEGORY_MESSAGE);
            int id = (int)(System.currentTimeMillis() % 100000) + 1001;
            NotificationManagerCompat.from(c).notify(id, b.build());
        } catch(SecurityException e){}
        catch(Exception e){}
    }
}
'''
W(J + "/Notifier.java", NOTIFIER)

# ===========================================================================
# 2 : Menu  -> "Notification sound" picker (More menu)
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
        final String[] items = {"About Offex Mail", "Rate us", "Privacy Policy", "Terms of Use", "Contact us", sound, theme, notif};
        new AlertDialog.Builder(a)
            .setTitle("More")
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a, AboutActivity.class));
                    else if(w==1) openUrl(a,"https://play.google.com/store/apps/details?id=online.mytempmail.app");
                    else if(w==2) openUrl(a,"https://mytemp-mail.online/privacy");
                    else if(w==3) openUrl(a,"https://mytemp-mail.online/terms");
                    else if(w==4) a.startActivity(new Intent(a, ContactActivity.class));
                    else if(w==5) pickSound(a);
                    else if(w==6) { Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); a.recreate(); }
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

# ===========================================================================
# 4 + 5 : Updater  -> in-app download + install (unknown sources)
# ===========================================================================
UPDATER = r'''package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.app.DownloadManager;
import android.content.Context;
import android.content.Intent;
import android.database.Cursor;
import android.graphics.Color;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.os.Handler;
import android.os.Looper;
import android.provider.Settings;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ProgressBar;
import android.widget.TextView;
import android.widget.Toast;
public class Updater {
    public static void start(final Activity a, final String url){
        if(url == null || url.trim().isEmpty()) return;
        try {
            final DownloadManager dm = (DownloadManager)a.getSystemService(Context.DOWNLOAD_SERVICE);
            if(dm == null) return;
            DownloadManager.Request req = new DownloadManager.Request(Uri.parse(url.trim()));
            req.setTitle("Offex Mail update");
            req.setDescription("Downloading the new version");
            req.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE);
            req.setMimeType("application/vnd.android.package-archive");
            try { req.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, "OffexMail-update.apk"); }
            catch(Exception e){ req.setDestinationInExternalFilesDir(a, Environment.DIRECTORY_DOWNLOADS, "OffexMail-update.apk"); }
            final long id = dm.enqueue(req);

            final ProgressBar bar = new ProgressBar(a, null, android.R.attr.progressBarStyleHorizontal);
            bar.setMax(100);
            bar.setIndeterminate(true);
            final TextView pct = new TextView(a);
            pct.setText("Starting download...");
            pct.setTextColor(Color.parseColor("#5C5875"));
            pct.setPadding(0, 8, 0, 22);
            LinearLayout box = new LinearLayout(a);
            box.setOrientation(LinearLayout.VERTICAL);
            box.setPadding(52, 44, 52, 28);
            box.addView(pct);
            box.addView(bar, new LinearLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT));
            final AlertDialog dlg = new AlertDialog.Builder(a)
                .setTitle("Downloading update")
                .setView(box)
                .setCancelable(false)
                .create();
            dlg.show();

            final Handler h = new Handler(Looper.getMainLooper());
            h.postDelayed(new Runnable(){
                @Override public void run(){
                    boolean again = true;
                    Cursor c = null;
                    try {
                        c = dm.query(new DownloadManager.Query().setFilterById(id));
                        if(c != null && c.moveToFirst()){
                            int st = c.getInt(c.getColumnIndex(DownloadManager.COLUMN_STATUS));
                            long done = c.getLong(c.getColumnIndex(DownloadManager.COLUMN_BYTES_DOWNLOADED_SO_FAR));
                            long total = c.getLong(c.getColumnIndex(DownloadManager.COLUMN_TOTAL_SIZE_BYTES));
                            if(total > 0){
                                bar.setIndeterminate(false);
                                int p = (int)(done * 100 / total);
                                if(p < 0) p = 0; if(p > 100) p = 100;
                                bar.setProgress(p);
                                pct.setText("Downloading... " + p + "%");
                            }
                            if(st == DownloadManager.STATUS_SUCCESSFUL){
                                again = false;
                                try { dlg.dismiss(); } catch(Exception e){}
                                install(a, dm.getUriForDownloadedFile(id));
                            } else if(st == DownloadManager.STATUS_FAILED){
                                again = false;
                                try { dlg.dismiss(); } catch(Exception e){}
                                Toast.makeText(a, "Download failed. Please try again.", Toast.LENGTH_LONG).show();
                            }
                        }
                    } catch(Exception e){
                    } finally {
                        if(c != null) c.close();
                    }
                    if(again) h.postDelayed(this, 700);
                }
            }, 700);
        } catch(Exception e){}
    }

    private static void install(final Activity a, final Uri apk){
        try {
            if(Build.VERSION.SDK_INT >= Build.VERSION_CODES.O && !a.getPackageManager().canRequestPackageInstalls()){
                new AlertDialog.Builder(a)
                    .setTitle("Allow install")
                    .setMessage("To install the update, allow Offex Mail to install unknown apps, then open the update again.")
                    .setPositiveButton("Open settings", (d,w)->{
                        try {
                            Intent i = new Intent(Settings.ACTION_MANAGE_UNKNOWN_APP_SOURCES, Uri.parse("package:" + a.getPackageName()));
                            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                            a.startActivity(i);
                        } catch(Exception e){}
                    })
                    .setNegativeButton("Later", (d,w)->{})
                    .show();
                return;
            }
            Intent i = new Intent(Intent.ACTION_VIEW);
            i.setDataAndType(apk, "application/vnd.android.package-archive");
            i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
            i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
            a.startActivity(i);
        } catch(Exception e){}
    }
}
'''
W(J + "/Updater.java", UPDATER)

# ===========================================================================
# 4 : Config  -> update prompt now downloads in-app
# ===========================================================================
cp = J + "/Config.java"
s = R(cp)
old_btn = 'b.setPositiveButton("Update now", (d,w)->{ try{ a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); }catch(Exception e){} });'
new_btn = 'b.setPositiveButton("Update now", (d,w)->{ try{ Updater.start(a, url); }catch(Exception e){} });'
if old_btn in s:
    s = s.replace(old_btn, new_btn)
    print("R: Config update button -> in-app download")
else:
    print("R: WARN Config update button anchor not found")
s = s.replace('latest.equals("3.3")', 'latest.equals("3.5")')
s = s.replace('latest.equals("__VER__")', 'latest.equals("3.5")')
W(cp, s)

# ===========================================================================
# 7 : MainActivity  -> premium INLINE loading state on the Create button
#     (spinner sits on the button itself; no floating dialog)
# ===========================================================================
mp = J + "/MainActivity.java"
s = R(mp)

if "import android.widget.ImageView;" not in s:
    s = s.replace("import android.widget.EditText;",
                  "import android.widget.EditText;\nimport android.widget.FrameLayout;\nimport android.widget.ImageView;")
if "import android.view.animation.RotateAnimation;" not in s:
    s = s.replace("import android.view.View;",
                  "import android.view.View;\nimport android.view.ViewGroup;\nimport android.view.animation.Animation;\nimport android.view.animation.LinearInterpolator;\nimport android.view.animation.RotateAnimation;")
if "private ImageView createSpin;" not in s:
    s = s.replace("    private Runnable pollTask;",
                  "    private Runnable pollTask;\n    private ImageView createSpin;\n    private boolean createLoading=false;")

old_click = "createBtn.setOnClickListener(v->Ads.rewarded(this, ()->createInbox()));"
new_click = "createBtn.setOnClickListener(v->{ showCreateLoading(); Ads.rewarded(this, ()->createInbox()); });"
if old_click in s:
    s = s.replace(old_click, new_click)
    print("R: MainActivity create click -> inline button loading")
else:
    print("R: WARN MainActivity create click anchor not found")

if "createBtn.setEnabled(false); createBtn.setText(R.string.creating);" in s:
    s = s.replace("createBtn.setEnabled(false); createBtn.setText(R.string.creating);", "showCreateLoading();")
    print("R: createInbox start -> showCreateLoading")
else:
    print("R: WARN createInbox start anchor not found")
if "createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);" in s:
    s = s.replace("createBtn.setEnabled(true); createBtn.setText(R.string.create_inbox);", "hideCreateLoading();")
    print("R: createInbox finish -> hideCreateLoading")

AD_METHODS = r'''    private void setupCreateLoading(){
        try {
            if(createSpin != null) return;
            final ImageView iv = new ImageView(this);
            iv.setImageResource(R.drawable.ox_spinner);
            int sz = (int)(getResources().getDisplayMetrics().density * 22f);
            iv.setLayoutParams(new FrameLayout.LayoutParams(sz, sz, Gravity.CENTER));
            iv.setVisibility(View.GONE);
            ViewGroup parent = (ViewGroup) createBtn.getParent();
            if(parent == null) return;
            int idx = parent.indexOfChild(createBtn);
            ViewGroup.LayoutParams blp = createBtn.getLayoutParams();
            FrameLayout holder = new FrameLayout(this);
            holder.setLayoutParams(blp);
            createBtn.setLayoutParams(new FrameLayout.LayoutParams(ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.MATCH_PARENT));
            parent.removeView(createBtn);
            holder.addView(createBtn);
            holder.addView(iv);
            parent.addView(holder, idx);
            createSpin = iv;
        } catch(Exception e){}
    }
    private void showCreateLoading(){
        try {
            if(createSpin == null) setupCreateLoading();
            if(createSpin == null) return;
            createLoading = true;
            createBtn.setEnabled(false);
            createBtn.setText("");
            if(createSpin.getVisibility() != View.VISIBLE){
                createSpin.setVisibility(View.VISIBLE);
                createSpin.setAlpha(0f);
                createSpin.animate().alpha(1f).setDuration(200).start();
            }
            RotateAnimation ra = new RotateAnimation(0f, 360f,
                Animation.RELATIVE_TO_SELF, 0.5f, Animation.RELATIVE_TO_SELF, 0.5f);
            ra.setDuration(800);
            ra.setInterpolator(new LinearInterpolator());
            ra.setRepeatCount(Animation.INFINITE);
            createSpin.startAnimation(ra);
        } catch(Exception e){}
    }
    private void hideCreateLoading(){
        try {
            createLoading = false;
            createBtn.setEnabled(true);
            createBtn.setText(R.string.create_inbox);
            if(createSpin != null && createSpin.getVisibility() == View.VISIBLE){
                createSpin.animate().alpha(0f).setDuration(200).withEndAction(()->{
                    try { createSpin.clearAnimation(); createSpin.setVisibility(View.GONE); } catch(Exception e){}
                }).start();
            }
        } catch(Exception e){}
    }
'''
anchor_resume = "    @Override protected void onResume(){"
if "private void showCreateLoading" not in s and anchor_resume in s:
    s = s.replace(anchor_resume, AD_METHODS + anchor_resume)
    print("R: MainActivity inline-loading methods inserted")
else:
    print("R: WARN MainActivity inline-loading methods not inserted")
W(mp, s)

# ===========================================================================
# 6 : SplashActivity  -> logo + loading animation
# ===========================================================================
SPLASH = r'''package online.mytempmail.app;
import android.app.Activity;
import android.content.Intent;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.view.animation.AnimationUtils;
import android.widget.ImageView;
public class SplashActivity extends Activity {
    @Override protected void onCreate(Bundle b){
        super.onCreate(b);
        Skin.apply(this);
        setContentView(R.layout.activity_splash);
        try {
            ImageView logo = findViewById(R.id.splashLogo);
            if(logo != null) logo.startAnimation(AnimationUtils.loadAnimation(this, R.anim.splash_pulse));
        } catch(Exception e){}
        new Handler(Looper.getMainLooper()).postDelayed(new Runnable(){
            @Override public void run(){
                try {
                    Intent next = Prefs.onboarded()
                        ? new Intent(SplashActivity.this, MainActivity.class)
                        : new Intent(SplashActivity.this, OnboardingActivity.class);
                    startActivity(next);
                } catch(Exception e){}
                finish();
            }
        }, 1600);
    }
}
'''
W(J + "/SplashActivity.java", SPLASH)

# ===========================================================================
# 6 : layouts / anim / drawable for splash + ad loading
# ===========================================================================
W(RES + "/anim/splash_pulse.xml", '''<?xml version="1.0" encoding="utf-8"?>
<set xmlns:android="http://schemas.android.com/apk/res/android">
    <alpha android:fromAlpha="0.0" android:toAlpha="1.0" android:duration="650" />
    <scale android:fromXScale="0.82" android:toXScale="1.0" android:fromYScale="0.82" android:toYScale="1.0"
        android:pivotX="50%" android:pivotY="50%" android:duration="650" />
</set>
''')

W(RES + "/drawable/splash_bg.xml", '''<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <gradient android:startColor="#C62828" android:centerColor="#E53935" android:endColor="#FF6F60" android:angle="270" />
</shape>
''')

W(RES + "/drawable/ox_spinner.xml", '''<?xml version="1.0" encoding="utf-8"?>
<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:pathData="M12,3 a9,9 0 1,0 18,0 a9,9 0 1,0 -18,0"
        android:strokeColor="#40FFFFFF" android:strokeWidth="2.4"
        android:strokeLineCap="round" android:fillColor="#00000000" />
    <path android:pathData="M12,3 A9,9 0 1 1 3,12"
        android:strokeColor="#FFFFFF" android:strokeWidth="2.6"
        android:strokeLineCap="round" android:fillColor="#00000000" />
</vector>
''')

W(RES + "/layout/activity_splash.xml", '''<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent" android:layout_height="match_parent"
    android:background="@drawable/splash_bg" android:orientation="vertical"
    android:gravity="center" android:padding="32dp">

    <ImageView android:id="@+id/splashLogo"
        android:layout_width="132dp" android:layout_height="132dp"
        android:src="@drawable/logo" android:contentDescription="@string/app_name"
        android:elevation="14dp" />

    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="24dp" android:text="@string/app_name"
        android:textColor="#FFFFFF" android:textSize="22sp" android:textStyle="bold"
        android:fontFamily="sans-serif-black" />

    <ProgressBar android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="22dp" android:indeterminate="true"
        android:indeterminateTint="#FFFFFF" />

    <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
        android:layout_marginTop="10dp" android:text="Loading..."
        android:textColor="#FFD9D9" android:textSize="13sp" />
</LinearLayout>
''')


# ===========================================================================
# 2 : bundle the custom notification sounds (real WAV resources)
# ===========================================================================
def _wav(freqs, dur=0.20, gap=0.045, sr=22050, vol=0.55):
    buf = bytearray()
    for f in freqs:
        n = int(sr * dur)
        for k in range(n):
            env = min(1.0, k / (0.008 * sr)) * min(1.0, (n - k) / (0.06 * sr))
            v = int(vol * 32767 * env * math.sin(2 * math.pi * f * (k / sr)))
            if v > 32767: v = 32767
            if v < -32768: v = -32768
            buf += struct.pack('<h', v)
        buf += b'\x00\x00' * int(sr * gap)
    bio = io.BytesIO()
    w = wave.open(bio, 'wb')
    w.setnchannels(1); w.setsampwidth(2); w.setframerate(sr)
    w.writeframes(bytes(buf)); w.close()
    return bio.getvalue()

try:
    WB(RES + "/raw/notify_1.wav", _wav([784.0, 1046.5]))          # Chime (rising two-note)
    WB(RES + "/raw/notify_2.wav", _wav([1046.5, 1318.5, 1568.0]))  # Ding (three-note)
    WB(RES + "/raw/notify_3.wav", _wav([880.0, 1174.7]))           # Pop (soft two-note)
    print("R: notification sounds written")
except Exception as e:
    print("R: WARN sound gen failed:", e)

# ===========================================================================
# 6 : logo  ->  drawable + launcher icon (mipmaps)
# ===========================================================================
LOGO = None
for _cand in ("resources/assets/logo.jpg", "resources/assets/logo.jpeg", "resources/assets/logo.png"):
    if os.path.exists(_cand):
        LOGO = _cand
        break
if LOGO:
    _ext = os.path.splitext(LOGO)[1].lower()
    if _ext == ".jpeg":
        _ext = ".jpg"
    try:
        WB(RES + "/drawable/logo" + _ext, open(LOGO, "rb").read())
        print("R: drawable/logo" + _ext + " written")
    except Exception as e:
        print("R: WARN logo drawable:", e)
    try:
        from PIL import Image
        img = Image.open(LOGO).convert("RGBA")
        for d, sz in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
            dd = RES + "/mipmap-" + d
            os.makedirs(dd, exist_ok=True)
            img.resize((sz, sz), Image.LANCZOS).save(dd + "/ic_launcher.png")
        print("R: launcher icons regenerated from logo")
    except Exception as e:
        print("R: WARN launcher icons:", e)
else:
    print("R: WARN resources/assets/logo.png missing - keeping existing icon")

# ===========================================================================
# 5 + 6 : AndroidManifest  -> install permission + splash launcher
# ===========================================================================
W("android/app/src/main/AndroidManifest.xml", '''<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE" />
    <uses-permission android:name="android.permission.FOREGROUND_SERVICE_DATA_SYNC" />
    <uses-permission android:name="android.permission.REQUEST_INSTALL_PACKAGES" />
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE" android:maxSdkVersion="28" />
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
        <activity android:name=".SplashActivity" android:exported="true" android:theme="@style/Theme.Offex">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".MainActivity" android:exported="true" android:launchMode="singleTop" android:windowSoftInputMode="adjustResize" />
        <activity android:name=".OnboardingActivity" android:exported="false" />
        <activity android:name=".ReaderActivity" android:exported="false" />
        <activity android:name=".AboutActivity" android:exported="false" />
        <activity android:name=".ContactActivity" android:exported="false" />
        <service android:name=".MailService" android:exported="false" android:foregroundServiceType="dataSync" />
    </application>
</manifest>
''')

# ===========================================================================
# 1 : move the "Why Offex Mail" features section to the BOTTOM of home
# ===========================================================================
lp = RES + "/layout/activity_main.xml"
s = R(lp)
marker = "<!-- ============ FEATURES ============ -->"
if marker in s:
    start = s.index(marker)
    ls = s.rindex("\n", 0, start) + 1                 # start of the comment's line
    fb = s.index('id="@+id/featuresBox"', start)
    open_idx = s.rindex("<LinearLayout", 0, fb)
    depth = 0
    end = None
    for m in re.finditer(r"</?LinearLayout\b[^>]*>", s[open_idx:]):
        if m.group(0).startswith("</"):
            depth -= 1
        else:
            depth += 1
        if depth == 0:
            end = open_idx + m.end()
            break
    if end is not None:
        block = s[ls:end]
        s2 = s[:ls] + s[end:]
        s2 = s2.replace("\n\n\n", "\n\n")
        bottom = "        </LinearLayout>\n    </ScrollView>"
        if bottom in s2:
            s2 = s2.replace(bottom, "\n" + block + "\n" + bottom)
            s = s2
            print("R: features section moved to bottom")
        else:
            print("R: WARN bottom scroll anchor not found")
    else:
        print("R: WARN could not find featuresBox end")
else:
    print("R: WARN features marker not found in activity_main.xml")
W(lp, s)

# ===========================================================================
# version : 3.3 -> 3.5
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = re.sub(r"versionCode \d+", "versionCode 25", s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.5"', s)
W(bp, s)

ap = RES + "/layout/activity_about.xml"
s = R(ap)
s = s.replace("Version 3.3", "Version 3.5").replace("Version 3.1", "Version 3.5")
W(ap, s)

print("R: applied v3.5 changes (inline create-button loading + premium spinner, features move, sounds, in-app update, install perm, logo+splash)")
