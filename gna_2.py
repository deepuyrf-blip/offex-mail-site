# ============================================================================
#  gna_2.py  -  Offex Audio, generator 2 of 6  (core Java: support classes)
# ============================================================================
#  Emits: App, Prefs, LocaleHelper, Config, Ads, Notifier, Downloader,
#         HistoryStore.
#  No secrets are embedded. The remote config endpoint is a plain URL and all
#  AdMob ids default to Google's official TEST units.
# ============================================================================
import os

J = "android-audio/app/src/main/java/online/offexaudio/app"

F = {}

F["App.java"] = r'''package online.offexaudio.app;

import android.app.Application;

/**
 * Application entry point. Initialises the Mobile Ads SDK once. Everything is
 * wrapped so a missing/blocked ads backend can never crash the app.
 */
public class App extends Application {
    @Override public void onCreate() {
        super.onCreate();
        try {
            com.google.android.gms.ads.MobileAds.initialize(this, status -> { });
        } catch (Throwable t) { /* ads are optional */ }
    }
}
'''

F["Prefs.java"] = r'''package online.offexaudio.app;

import android.content.Context;
import android.content.SharedPreferences;

/** Tiny SharedPreferences wrapper for language, notification and history state. */
public class Prefs {
    private static final String NAME = "offex_audio";

    private static SharedPreferences sp(Context c) {
        return c.getApplicationContext().getSharedPreferences(NAME, Context.MODE_PRIVATE);
    }

    public static String lang(Context c) { return sp(c).getString("lang", "en"); }
    public static void setLang(Context c, String v) { sp(c).edit().putString("lang", v == null ? "en" : v).apply(); }

    public static boolean notifyOn(Context c) { return sp(c).getBoolean("notify", true); }
    public static void setNotifyOn(Context c, boolean v) { sp(c).edit().putBoolean("notify", v).apply(); }

    public static int sound(Context c) { return sp(c).getInt("sound", 0); }
    public static void setSound(Context c, int v) { sp(c).edit().putInt("sound", v).apply(); }

    public static String history(Context c) { return sp(c).getString("history", "[]"); }
    public static void setHistory(Context c, String v) { sp(c).edit().putString("history", v == null ? "[]" : v).apply(); }

    public static String configCache(Context c) { return sp(c).getString("config", "{}"); }
    public static void setConfigCache(Context c, String v) { sp(c).edit().putString("config", v == null ? "{}" : v).apply(); }

    public static boolean gateShown(Context c) { return sp(c).getBoolean("gate", false); }
    public static void setGateShown(Context c, boolean v) { sp(c).edit().putBoolean("gate", v).apply(); }
}
'''

F["LocaleHelper.java"] = r'''package online.offexaudio.app;

import android.content.Context;
import android.content.res.Configuration;
import android.os.Build;

import java.util.Locale;

/**
 * Applies the in-app language choice. The app ships English (default) plus
 * Hindi, Spanish, Portuguese, Arabic (RTL), Russian and Indonesian.
 */
public class LocaleHelper {
    /** code -> label shown in the switcher (in the language itself). */
    public static final String[][] LANGS = {
            {"en", "English"},
            {"hi", "\u0939\u093f\u0928\u094d\u0926\u0940"},
            {"es", "Espa\u00f1ol"},
            {"pt", "Portugu\u00eas"},
            {"ar", "\u0627\u0644\u0639\u0631\u0628\u064a\u0629"},
            {"ru", "\u0420\u0443\u0441\u0441\u043a\u0438\u0439"},
            {"in", "Bahasa Indonesia"},
    };

    public static String current(Context c) { return Prefs.lang(c); }

    /** Wrap a context so resources resolve in the chosen locale. */
    public static Context wrap(Context c) {
        String code = Prefs.lang(c);
        Locale locale = new Locale(code);
        Locale.setDefault(locale);
        Configuration cfg = new Configuration(c.getResources().getConfiguration());
        cfg.setLocale(locale);
        if (Build.VERSION.SDK_INT >= 17) cfg.setLayoutDirection(locale);
        return c.createConfigurationContext(cfg);
    }

    public static boolean isRtl(Context c) {
        String code = Prefs.lang(c);
        return "ar".equals(code);
    }
}
'''

F["Config.java"] = r'''package online.offexaudio.app;

import android.content.Context;

import org.json.JSONObject;

import java.io.BufferedReader;
import java.io.InputStreamReader;
import java.net.HttpURLConnection;
import java.net.URL;

/**
 * Remote configuration.
 *
 * The app reads its config from the Offex backend's public app-config endpoint
 * and tolerates every failure by falling back to built-in defaults, so the app
 * always works even when the panel is not reachable.
 *
 * Endpoint:   https://api.mytemp-mail.online/api/app-config
 * (override with Prefs "config_endpoint" if the panel moves.)
 *
 * Expected JSON shape (all keys optional) - see audioapp/README.md:
 * {
 *   "appearance": { "accent": "#6366f1", "accent2": "#22d3ee",
 *                   "gradient_start": "#6366f1", "gradient_end": "#d946ef",
 *                   "radius": 22, "hero_title": "Offex Audio",
 *                   "hero_tagline": "..." },
 *   "ads":  { "banner": "...", "interstitial": "...", "rewarded": "...",
 *             "app_open": "...", "native": "...", "show_banner": true },
 *   "flags":{ "show_banner_ad": true, "show_history": true,
 *             "show_features": true, "gate_ads": false },
 *   "update":{ "latest": "1.0", "url": "https://.../OffexAudio.apk",
 *              "force": false },
 *   "banner": { "on": false, "text": "", "url": "" },
 *   "announcement": { "on": false, "text": "" },
 *   "endpoints": { "health": "https://offexmail.online/health",
 *                  "proxy": "https://offexmail.online/hf" }
 * }
 */
public class Config {
    public static final String DEFAULT_ENDPOINT = "https://api.mytemp-mail.online/api/app-config";
    public static final String DEFAULT_HEALTH = "https://offexmail.online/health";
    public static final String DEFAULT_PROXY = "https://offexmail.online/hf";

    private static JSONObject j = new JSONObject();

    public static JSONObject raw() { return j; }

    public static void loadAsync(final Context ctx) {
        new Thread(() -> {
            try {
                String s = httpGet(DEFAULT_ENDPOINT);
                if (s != null && s.trim().startsWith("{")) {
                    JSONObject o = new JSONObject(s);
                    j = o;
                    Prefs.setConfigCache(ctx, s);
                }
            } catch (Throwable t) {
                try { j = new JSONObject(Prefs.configCache(ctx)); } catch (Throwable e) { j = new JSONObject(); }
            }
        }).start();
    }

    private static JSONObject obj(String key) {
        try { return j.optJSONObject(key); } catch (Throwable t) { return null; }
    }

    public static JSONObject appearance() { JSONObject o = obj("appearance"); return o == null ? new JSONObject() : o; }

    public static JSONObject ads() { JSONObject o = obj("ads"); return o == null ? new JSONObject() : o; }

    public static JSONObject flags() { JSONObject o = obj("flags"); return o == null ? new JSONObject() : o; }

    public static JSONObject update() { JSONObject o = obj("update"); return o == null ? new JSONObject() : o; }

    public static JSONObject endpoints() { JSONObject o = obj("endpoints"); return o == null ? new JSONObject() : o; }

    public static boolean flag(String k, boolean def) {
        try { return flags().has(k) ? flags().optBoolean(k, def) : def; } catch (Throwable t) { return def; }
    }

    public static String healthUrl() {
        try { return endpoints().optString("health", DEFAULT_HEALTH); } catch (Throwable t) { return DEFAULT_HEALTH; }
    }

    public static String proxyUrl() {
        try { return endpoints().optString("proxy", DEFAULT_PROXY); } catch (Throwable t) { return DEFAULT_PROXY; }
    }

    static String httpGet(String url) {
        HttpURLConnection c = null;
        try {
            c = (HttpURLConnection) new URL(url).openConnection();
            c.setConnectTimeout(8000);
            c.setReadTimeout(8000);
            c.setRequestProperty("Accept", "application/json");
            if (c.getResponseCode() / 100 != 2) return null;
            StringBuilder sb = new StringBuilder();
            try (BufferedReader r = new BufferedReader(new InputStreamReader(c.getInputStream(), "UTF-8"))) {
                String line;
                while ((line = r.readLine()) != null) sb.append(line);
            }
            return sb.toString();
        } catch (Throwable t) {
            return null;
        } finally {
            if (c != null) c.disconnect();
        }
    }
}
'''

F["Ads.java"] = r'''package online.offexaudio.app;

import android.app.Activity;
import android.content.Context;
import android.util.Log;
import android.view.ViewGroup;

import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.appopen.AppOpenAd;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;

/**
 * AdMob placements. Every unit id defaults to Google's OFFICIAL TEST id and is
 * overridable at runtime from the backend config ("ads" object) once the user
 * pastes real ids into the admin panel.
 */
public class Ads {
    private static final String TAG = "OffexAds";

    // ---- Google official TEST unit ids (do NOT ship real ids here) ----
    public static final String TEST_APP_ID      = "ca-app-pub-3940256099942544~3347511713";
    public static final String TEST_BANNER      = "ca-app-pub-3940256099942544/6300978111";
    public static final String TEST_INTERSTITIAL= "ca-app-pub-3940256099942544/1033173712";
    public static final String TEST_REWARDED    = "ca-app-pub-3940256099942544/5224354917";
    public static final String TEST_APP_OPEN    = "ca-app-pub-3940256099942544/9257395921";
    public static final String TEST_NATIVE      = "ca-app-pub-3940256099942544/2247696110";

    public static String unit(String key, String fallback) {
        try {
            String v = Config.ads().optString(key, "");
            if (v != null && v.startsWith("ca-app-pub-")) return v;
        } catch (Throwable t) { }
        return fallback;
    }

    public static String bannerId() { return unit("banner", TEST_BANNER); }
    public static String interstitialId() { return unit("interstitial", TEST_INTERSTITIAL); }
    public static String rewardedId() { return unit("rewarded", TEST_REWARDED); }
    public static String appOpenId() { return unit("app_open", TEST_APP_OPEN); }
    public static String nativeId() { return unit("native", TEST_NATIVE); }

    private static InterstitialAd interstitial;
    private static RewardedAd rewarded;
    private static AppOpenAd appOpen;

    public static void loadBanner(Context c, ViewGroup container) {
        try {
            if (container == null || !Config.flag("show_banner_ad", true)) return;
            AdView v = new AdView(c);
            v.setAdSize(AdSize.BANNER);
            v.setAdUnitId(bannerId());
            container.addView(v);
            v.loadAd(new AdRequest.Builder().build());
        } catch (Throwable t) { Log.w(TAG, "banner: " + t); }
    }

    public static void loadInterstitial(Context c) {
        try {
            InterstitialAd.load(c, interstitialId(), new AdRequest.Builder().build(),
                    new InterstitialAdLoadCallback() {
                        @Override public void onAdLoaded(InterstitialAd ad) { interstitial = ad; }
                        @Override public void onAdFailedToLoad(LoadAdError e) { interstitial = null; }
                    });
        } catch (Throwable t) { Log.w(TAG, "interstitial: " + t); }
    }

    public static void showInterstitial(Activity a) {
        try {
            if (interstitial != null) {
                interstitial.show(a);
                interstitial = null;
                loadInterstitial(a);
            }
        } catch (Throwable t) { Log.w(TAG, "showInterstitial: " + t); }
    }

    public static void loadRewarded(Context c) {
        try {
            RewardedAd.load(c, rewardedId(), new AdRequest.Builder().build(),
                    new RewardedAdLoadCallback() {
                        @Override public void onAdLoaded(RewardedAd ad) { rewarded = ad; }
                        @Override public void onAdFailedToLoad(LoadAdError e) { rewarded = null; }
                    });
        } catch (Throwable t) { Log.w(TAG, "rewarded: " + t); }
    }

    public static void showRewarded(Activity a, Runnable onReward) {
        try {
            if (rewarded != null) {
                final RewardedAd ad = rewarded;
                ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                    @Override public void onAdDismissedFullScreenContent() {
                        rewarded = null; loadRewarded(a);
                        if (onReward != null) onReward.run();
                    }
                });
                ad.show(a, reward -> { });
                rewarded = null;
            } else if (onReward != null) {
                onReward.run();
            }
        } catch (Throwable t) { Log.w(TAG, "showRewarded: " + t); if (onReward != null) onReward.run(); }
    }

    /** App-open ad shown once on cold start (never blocks the UI if it fails). */
    public static void showAppOpenIfAvailable(final Activity a) {
        try {
            AppOpenAd.load(a, appOpenId(), new AdRequest.Builder().build(),
                    new AppOpenAd.AppOpenAdLoadCallback() {
                        @Override public void onAdLoaded(AppOpenAd ad) {
                            appOpen = ad;
                            ad.setFullScreenContentCallback(new FullScreenContentCallback() {
                                @Override public void onAdDismissedFullScreenContent() { appOpen = null; }
                                @Override public void onAdFailedToShowFullScreenContent(AdError e) { appOpen = null; }
                            });
                            try { ad.show(a); } catch (Throwable t) { appOpen = null; }
                        }
                        @Override public void onAdFailedToLoad(LoadAdError e) { appOpen = null; }
                    });
        } catch (Throwable t) { Log.w(TAG, "appopen: " + t); }
    }
}
'''

F["Notifier.java"] = r'''package online.offexaudio.app;

import android.app.Notification;
import android.app.NotificationChannel;
import android.app.NotificationManager;
import android.app.PendingIntent;
import android.content.Context;
import android.content.Intent;
import android.media.RingtoneManager;
import android.net.Uri;
import android.os.Build;

import androidx.core.app.NotificationCompat;
import androidx.core.app.NotificationManagerCompat;

/** Single notification path for both local job alerts and FCM pushes. */
public class Notifier {
    public static final String CH_ID = "offex_audio_jobs";
    private static final int[] SND_RAW = { R.raw.notify_1, R.raw.notify_2, R.raw.notify_3 };
    public static final String[] SND_NAMES = { "Bell", "Chime", "Note" };

    public static void ensureChannel(Context c) {
        if (Build.VERSION.SDK_INT < 26) return;
        NotificationManager nm = (NotificationManager) c.getSystemService(Context.NOTIFICATION_SERVICE);
        if (nm == null || nm.getNotificationChannel(CH_ID) != null) return;
        NotificationChannel ch = new NotificationChannel(CH_ID, c.getString(R.string.notif_channel_jobs),
                NotificationManager.IMPORTANCE_HIGH);
        ch.setDescription(c.getString(R.string.notif_channel_jobs_desc));
        ch.enableVibration(true);
        nm.createNotificationChannel(ch);
    }

    private static Uri sound(Context c) {
        try {
            int i = Prefs.sound(c);
            if (i < 0 || i >= SND_RAW.length) i = 0;
            return Uri.parse("android.resource://" + c.getPackageName() + "/" + SND_RAW[i]);
        } catch (Throwable t) {
            return RingtoneManager.getDefaultUri(RingtoneManager.TYPE_NOTIFICATION);
        }
    }

    public static void job(Context c, String title, String body) {
        if (!Prefs.notifyOn(c)) return;
        ensureChannel(c);
        try {
            Intent open = new Intent(c, MainActivity.class);
            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);
            int flags = PendingIntent.FLAG_UPDATE_CURRENT;
            if (Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;
            PendingIntent content = PendingIntent.getActivity(c, (int) (System.currentTimeMillis() & 0xffff), open, flags);

            NotificationCompat.Builder b = new NotificationCompat.Builder(c, CH_ID)
                    .setSmallIcon(R.mipmap.ic_launcher)
                    .setContentTitle(title == null ? c.getString(R.string.job_done_title) : title)
                    .setContentText(body == null ? c.getString(R.string.job_done_body) : body)
                    .setAutoCancel(true)
                    .setSound(sound(c))
                    .setPriority(NotificationCompat.PRIORITY_HIGH)
                    .setContentIntent(content);
            Notification n = b.build();
            NotificationManagerCompat.from(c).notify((int) (System.currentTimeMillis() & 0xffff), n);
        } catch (Throwable t) { }
    }
}
'''

F["Downloader.java"] = r'''package online.offexaudio.app;

import android.app.DownloadManager;
import android.content.ContentValues;
import android.content.Context;
import android.net.Uri;
import android.os.Build;
import android.os.Environment;
import android.provider.MediaStore;
import android.util.Base64;

import java.io.File;
import java.io.FileOutputStream;
import java.io.OutputStream;

/**
 * Saves finished results into the device's public Downloads folder.
 *  - https results  -> DownloadManager (DIRECTORY_DOWNLOADS, correct mime).
 *  - in-page blob   -> written straight to Downloads via MediaStore (API 29+)
 *                      or a plain file (API < 29).
 */
public class Downloader {

    public static void fromUrl(Context c, String url, String filename, String mime) {
        try {
            if (url == null || url.isEmpty()) return;
            String name = safe(filename);
            DownloadManager dm = (DownloadManager) c.getSystemService(Context.DOWNLOAD_SERVICE);
            if (dm == null) return;
            DownloadManager.Request r = new DownloadManager.Request(Uri.parse(url));
            r.setTitle(name);
            r.setMimeType(mime == null || mime.isEmpty() ? "audio/mpeg" : mime);
            r.setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED);
            r.setDestinationInExternalPublicDir(Environment.DIRECTORY_DOWNLOADS, name);
            dm.enqueue(r);
        } catch (Throwable t) { }
    }

    /** @return the human-readable location, or null on failure. */
    public static String fromBase64(Context c, String b64, String filename, String mime) {
        try {
            byte[] data = Base64.decode(b64, Base64.DEFAULT);
            String name = safe(filename);
            String mm = (mime == null || mime.isEmpty()) ? "audio/mpeg" : mime;
            if (Build.VERSION.SDK_INT >= 29) {
                ContentValues v = new ContentValues();
                v.put(MediaStore.Downloads.DISPLAY_NAME, name);
                v.put(MediaStore.Downloads.MIME_TYPE, mm);
                v.put(MediaStore.Downloads.IS_PENDING, 1);
                Uri uri = c.getContentResolver().insert(MediaStore.Downloads.EXTERNAL_CONTENT_URI, v);
                if (uri == null) return null;
                try (OutputStream os = c.getContentResolver().openOutputStream(uri)) {
                    if (os == null) return null;
                    os.write(data);
                }
                v.clear();
                v.put(MediaStore.Downloads.IS_PENDING, 0);
                c.getContentResolver().update(uri, v, null, null);
                return "Downloads/" + name;
            } else {
                File dir = new File(Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS), "");
                if (!dir.exists()) dir.mkdirs();
                File f = new File(dir, name);
                try (FileOutputStream os = new FileOutputStream(f)) { os.write(data); }
                return f.getAbsolutePath();
            }
        } catch (Throwable t) {
            return null;
        }
    }

    private static String safe(String name) {
        String n = (name == null || name.trim().isEmpty()) ? "offex_audio_output" : name.trim();
        n = n.replaceAll("[\\\\/:*?\"<>|]", "_");
        if (n.length() > 120) n = n.substring(n.length() - 120);
        return n;
    }
}
'''

F["HistoryStore.java"] = r'''package online.offexaudio.app;

import android.content.Context;

import org.json.JSONArray;
import org.json.JSONObject;

/** Local job history (SharedPreferences-backed JSON array, newest first). */
public class HistoryStore {
    private static final int MAX = 100;

    public static synchronized void add(Context c, String tool, String filename, String when, String url) {
        try {
            JSONArray a = new JSONArray(Prefs.history(c));
            JSONArray out = new JSONArray();
            JSONObject o = new JSONObject();
            o.put("tool", tool == null ? "" : tool);
            o.put("file", filename == null ? "" : filename);
            o.put("when", when == null ? "" : when);
            o.put("url", url == null ? "" : url);
            out.put(o);
            for (int i = 0; i < a.length() && i < MAX - 1; i++) out.put(a.getJSONObject(i));
            Prefs.setHistory(c, out.toString());
        } catch (Throwable t) { }
    }

    public static synchronized void clear(Context c) { Prefs.setHistory(c, "[]"); }

    public static synchronized JSONArray list(Context c) {
        try { return new JSONArray(Prefs.history(c)); } catch (Throwable t) { return new JSONArray(); }
    }

    /** Optionally reported to the backend so the admin panel can see activity. */
    public static void reportAsync(final Context c, final String tool, final String filename) {
        new Thread(() -> {
            try {
                java.net.HttpURLConnection conn = (java.net.HttpURLConnection)
                        new java.net.URL("https://api.mytemp-mail.online/api/audio-history").openConnection();
                conn.setConnectTimeout(6000);
                conn.setReadTimeout(6000);
                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "application/json");
                JSONObject o = new JSONObject();
                o.put("tool", tool == null ? "" : tool);
                o.put("file", filename == null ? "" : filename);
                o.put("at", System.currentTimeMillis());
                try (java.io.OutputStream os = conn.getOutputStream()) {
                    os.write(o.toString().getBytes("UTF-8"));
                }
                conn.getResponseCode();
                conn.disconnect();
            } catch (Throwable t) { /* best-effort only */ }
        }).start();
    }
}
'''

for name, body in F.items():
    p = os.path.join(J, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)

print("GNA2: wrote %d java files" % len(F))
