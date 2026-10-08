# ============================================================================
#  gna_3.py  -  Offex Audio, generator 3 of 6  (MainActivity)
# ============================================================================
#  The whole screen is the app's OWN bundled HTML UI (the v1.0 custom design:
#  three tool tabs + History + More, file zone, options, progress meter and
#  result player) hosted in a WebView, bridged to native Java through
#  @JavascriptInterface "OffexNative". Java pushes state back with
#  window.OffexAudioUI.render(json).
#
#  IMPORTANT (learned from the mail app): the Android Java bridge resolves a
#  @JavascriptInterface method by its ARGUMENT COUNT, so the JS side must call
#  every method with EXACTLY its declared parameter count. The page's call()
#  helper forwards the arguments it is given, unchanged.
#
#  v1.3 BACKEND FIX (this is the key change over v1.2):
#    v1.2 served the bundled UI from a local appassets origin and
#    had it call the site's /hf proxy cross-origin. That cross-origin call was
#    blocked (CORS / the proxy), so no real job ran (no upload %, instant fake
#    completion).
#    Now the app's OWN custom UI is HOSTED ON THE SITE itself and loaded from
#    https://offexmail.online/app-ui, so the page shares the site's origin with
#    the /hf proxy and /health. Same-origin fetch/XHR/WebSocket calls to
#    https://offexmail.online/hf/* and https://offexmail.online/health are not
#    cross-origin, so there is no CORS problem and no HF token inside the app
#    (the Cloudflare Pages worker injects the token server-side). The page runs
#    the real @gradio/client flow (connect -> upload -> submit -> stream
#    progress -> fetch result URL). This is still the app's own design, NOT the
#    marketing website.
# ============================================================================
import os

J = "android-audio/app/src/main/java/online/offexaudio/app"

MAIN = r'''package online.offexaudio.app;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.view.View;
import android.webkit.ConsoleMessage;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONArray;
import org.json.JSONObject;

import java.io.InputStream;
import java.net.HttpURLConnection;
import java.net.URL;
import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

public class MainActivity extends AppCompatActivity {

    private static final String TAG = "OffexAudio";

    /**
     * The app's OWN custom UI is hosted on the site itself and loaded from
     * there, so the page shares the site's origin with the /hf proxy and
     * /health. Same origin means the page's ordinary fetch/XHR/WebSocket calls
     * to https://offexmail.online/hf/* and https://offexmail.online/health are
     * NOT cross-origin - no CORS problem, and no HF token in the app (the
     * Cloudflare Pages worker injects the token server-side).
     */
    private static final String UI_URL = "https://offexmail.online/app-ui";

    /** Hosts the page is allowed to talk to from inside the WebView. */
    private static final String BACKEND_HOST = "offexmail.online";

    private static final int REQ_NOTIF = 8801;
    private static final int REQ_FILE = 8802;

    private WebView webUi;
    private View adBanner;
    private volatile String stateJson = "{}";
    private ValueCallback<Uri[]> filePathCallback;

    private final Handler ui = new Handler(Looper.getMainLooper());
    private volatile boolean live = false;
    private volatile boolean processor = false;
    private volatile String healthNote = "Checking\u2026";
    private volatile boolean healthRunning = false;
    private static MainActivity live0;

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        live0 = this;
        LocaleHelper.wrap(this);
        setContentView(R.layout.activity_main);
        Notifier.ensureChannel(this);
        Config.loadAsync(this);
        setupWebUi();
        adBanner = findViewById(R.id.adBanner);
        if (adBanner != null && Config.flag("show_banner_ad", true)) {
            adBanner.setVisibility(View.VISIBLE);
            Ads.loadBanner(this, (android.view.ViewGroup) adBanner);
        }
        Ads.loadInterstitial(this);
        Ads.loadRewarded(this);
        startHealthLoop();
        maybeShowNotifGate();
        /* Register this device's FCM token with the backend on EVERY app start
           (not only when FCM happens to mint a fresh token), so the audio
           panel's broadcast reaches this install. Token refreshes are handled
           by FcmService.onNewToken -> DeviceReg.send. */
        DeviceReg.start(this);
        Ads.showAppOpenIfAvailable(this);
    }

    @Override protected void onResume() { super.onResume(); pushState(); }

    // ------------------------------------------------------------------ WebView
    private void setupWebUi() {
        try {
            webUi = findViewById(R.id.webUi);
            if (webUi == null) return;

            WebSettings ws = webUi.getSettings();
            ws.setJavaScriptEnabled(true);
            ws.setDomStorageEnabled(true);
            ws.setDatabaseEnabled(true);
            ws.setAllowFileAccess(true);
            ws.setAllowContentAccess(true);
            ws.setSupportZoom(false);
            ws.setBuiltInZoomControls(false);
            ws.setDisplayZoomControls(false);
            ws.setMediaPlaybackRequiresUserGesture(false);
            ws.setCacheMode(WebSettings.LOAD_DEFAULT);
            // A normal mobile UA so the backend and its proxy see a real device.
            ws.setUserAgentString(
                    "Mozilla/5.0 (Linux; Android 13; Pixel 7) AppleWebKit/537.36 " +
                    "(KHTML, like Gecko) Chrome/120.0.0.0 Mobile Safari/537.36");
            if (Build.VERSION.SDK_INT >= 21) {
                ws.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
            }
            webUi.setBackgroundColor(0xFF05060D);
            webUi.setVerticalScrollBarEnabled(false);
            webUi.setHorizontalScrollBarEnabled(false);
            webUi.setOverScrollMode(View.OVER_SCROLL_NEVER);

            CookieManager cm = CookieManager.getInstance();
            cm.setAcceptCookie(true);
            cm.setAcceptThirdPartyCookies(webUi, true);

            webUi.setWebViewClient(new WebViewClient() {
                @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                    String u = r.getUrl() == null ? "" : r.getUrl().toString();
                    if (isInternal(u)) return false;   // keep it inside the WebView
                    return openExternal(u);
                }
                @Override public boolean shouldOverrideUrlLoading(WebView v, String url) {
                    if (isInternal(url)) return false;
                    return openExternal(url);
                }
                @Override public void onPageFinished(WebView v, String url) { pushState(); }
            });

            webUi.setWebChromeClient(new WebChromeClient() {
                @Override public boolean onConsoleMessage(ConsoleMessage m) {
                    try { Log.i(TAG, m.message() + " @" + m.lineNumber()); } catch (Throwable t) { }
                    return true;
                }
                @Override public boolean onShowFileChooser(WebView v, ValueCallback<Uri[]> cb,
                                                           FileChooserParams params) {
                    if (filePathCallback != null) { filePathCallback.onReceiveValue(null); }
                    filePathCallback = cb;
                    try {
                        Intent i = new Intent(Intent.ACTION_OPEN_DOCUMENT);
                        i.addCategory(Intent.CATEGORY_OPENABLE);
                        i.setType("*/*");
                        i.putExtra(Intent.EXTRA_MIME_TYPES, new String[]{"audio/*", "video/*"});
                        startActivityForResult(Intent.createChooser(i, getString(R.string.choose_file)), REQ_FILE);
                        return true;
                    } catch (Throwable t) {
                        filePathCallback = null;
                        toast(getString(R.string.pick_error));
                        return false;
                    }
                }
            });

            webUi.addJavascriptInterface(new OffexBridge(), "OffexNative");
            webUi.loadUrl(UI_URL);
        } catch (Throwable t) { Log.e(TAG, "setupWebUi: " + t); }
    }

    /** The app origin and the backend host stay inside the WebView. */
    private boolean isInternal(String url) {
        try {
            if (url == null) return false;
            String u = url.trim();
            if (u.startsWith("file:") || u.startsWith("about:") || u.startsWith("data:")) return true;
            Uri uri = Uri.parse(u);
            String h = uri.getHost();
            if (h == null) return false;
            return h.equals(BACKEND_HOST) || h.endsWith("." + BACKEND_HOST)
                    || h.endsWith(".hf.space");
        } catch (Throwable t) { return false; }
    }

    @Override protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_FILE) {
            Uri[] out = null;
            if (res == RESULT_OK && data != null && data.getData() != null) {
                Uri u = data.getData();
                // Persist a read grant for the picked document so the WebView can
                // read it for the upload even after the picker returns.
                try {
                    getContentResolver().takePersistableUriPermission(u, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                } catch (Throwable t) { }
                out = new Uri[]{ u };
            }
            if (filePathCallback != null) { filePathCallback.onReceiveValue(out); filePathCallback = null; }
            return;
        }
        super.onActivityResult(req, res, data);
    }

    private boolean openExternal(String url) {
        try {
            if (url == null) return false;
            String u = url.trim();
            if (u.startsWith("file:") || u.startsWith("about:") || u.startsWith("javascript:") || u.startsWith("data:"))
                return false;
            if (u.startsWith("http://") || u.startsWith("https://") || u.startsWith("mailto:") || u.startsWith("tel:")) {
                Intent i = new Intent(Intent.ACTION_VIEW, Uri.parse(u));
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
                return true;
            }
        } catch (Throwable t) { }
        return false;
    }

    // ------------------------------------------------------------------ health
    private void startHealthLoop() {
        final Runnable[] tick = new Runnable[1];
        tick[0] = () -> {
            if (!healthRunning) {
                healthRunning = true;
                new Thread(() -> {
                    boolean ok = false;
                    String note = getString(R.string.not_connected);
                    HttpURLConnection c = null;
                    try {
                        URL url = new URL(Config.healthUrl() + "?ts=" + System.currentTimeMillis());
                        c = (HttpURLConnection) url.openConnection();
                        c.setConnectTimeout(5000);
                        c.setReadTimeout(5000);
                        c.setRequestProperty("Accept", "application/json");
                        if (c.getResponseCode() / 100 == 2) {
                            StringBuilder sb = new StringBuilder();
                            try (InputStream is = c.getInputStream()) {
                                byte[] buf = new byte[4096]; int n;
                                while ((n = is.read(buf)) > 0) sb.append(new String(buf, 0, n, "UTF-8"));
                            }
                            JSONObject o = new JSONObject(sb.toString());
                            ok = o.optBoolean("backend", o.optBoolean("processor", false));
                            note = ok ? getString(R.string.online) : getString(R.string.not_connected);
                        }
                    } catch (Throwable t) { ok = false; }
                    finally { if (c != null) c.disconnect(); }
                    final boolean fok = ok; final String fnote = note;
                    ui.post(() -> {
                        live = fok; processor = fok; healthNote = fnote;
                        healthRunning = false;
                        pushState();
                    });
                }).start();
            }
            ui.postDelayed(tick[0], 25000);
        };
        ui.post(tick[0]);
    }

    private void forceHealthPing() { healthRunning = false; }

    // ------------------------------------------------------------------ state
    private JSONObject buildStrings() {
        JSONObject t = new JSONObject();
        try {
            String[] keys = {
                    "app_name", "tagline", "live", "not_connected", "checking", "processor", "online",
                    "tab_remove", "tab_enhance", "tab_isolate", "tab_history", "tab_more",
                    "tool_remove_title", "tool_remove_sub", "tool_enhance_title", "tool_enhance_sub",
                    "tool_isolate_title", "tool_isolate_sub",
                    "drop_hint", "choose_file", "change_file", "no_file",
                    "keep_silence", "enhance_mode", "mode_light", "mode_balanced", "mode_strong",
                    "separation_model", "process", "processing", "download", "saving",
                    "saved_to_downloads", "result_ready", "vocals", "bgm", "open_result",
                    "history_title", "history_empty", "history_clear", "history_redownload",
                    "more_title", "more_language", "more_notifications", "more_notifications_on",
                    "more_notifications_off", "more_sound", "more_about", "more_version", "more_backend",
                    "more_backend_value", "more_privacy", "download_started", "download_failed"
            };
            for (String k : keys) {
                int id = getResources().getIdentifier(k, "string", getPackageName());
                if (id != 0) t.put(k, getString(id));
            }
        } catch (Throwable t2) { }
        return t;
    }

    private String buildState() {
        JSONObject s = new JSONObject();
        try {
            s.put("live", live);
            s.put("processor", processor);
            s.put("healthNote", healthNote);
            s.put("lang", LocaleHelper.current(this));
            s.put("rtl", LocaleHelper.isRtl(this));
            s.put("version", "1.4");
            s.put("proxy", Config.proxyUrl());
            s.put("health", Config.healthUrl());
            s.put("strings", buildStrings());

            JSONObject fl = new JSONObject();
            fl.put("show_history", Config.flag("show_history", true));
            fl.put("show_features", Config.flag("show_features", true));
            fl.put("show_banner_ad", Config.flag("show_banner_ad", true));
            s.put("flags", fl);

            s.put("appearance", Config.appearance());

            JSONObject ads = new JSONObject();
            ads.put("banner", Ads.bannerId());
            ads.put("interstitial", Ads.interstitialId());
            ads.put("rewarded", Ads.rewardedId());
            ads.put("app_open", Ads.appOpenId());
            ads.put("native", Ads.nativeId());
            s.put("ads", ads);

            JSONArray h = HistoryStore.list(this);
            JSONArray hl = new JSONArray();
            for (int i = 0; i < h.length(); i++) {
                JSONObject o = h.getJSONObject(i);
                JSONObject r = new JSONObject();
                r.put("tool", o.optString("tool"));
                r.put("file", o.optString("file"));
                r.put("when", o.optString("when"));
                r.put("url", o.optString("url"));
                hl.put(r);
            }
            s.put("history", hl);

            s.put("notify", Prefs.notifyOn(this));
            s.put("sound", Prefs.sound(this));
            JSONArray langs = new JSONArray();
            for (String[] l : LocaleHelper.LANGS) {
                JSONObject o = new JSONObject();
                o.put("code", l[0]); o.put("label", l[1]);
                langs.put(o);
            }
            s.put("langs", langs);
        } catch (Throwable t) { }
        return s.toString();
    }

    private void pushState() {
        try {
            ui.post(() -> {
                try {
                    stateJson = buildState();
                    if (webUi != null)
                        webUi.evaluateJavascript("window.OffexAudioUI&&window.OffexAudioUI.render(" + stateJson + ");", null);
                } catch (Throwable t) { }
            });
        } catch (Throwable t) { }
    }

    static void onPush() {
        MainActivity a = live0;
        if (a == null) return;
        a.pushState();
    }

    // ------------------------------------------------------------------ notify
    private void maybeShowNotifGate() {
        try {
            if (Build.VERSION.SDK_INT < 33) return;
            if (ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS) == PackageManager.PERMISSION_GRANTED)
                return;
            if (Prefs.gateShown(this)) return;
            Prefs.setGateShown(this, true);
            new AlertDialog.Builder(this)
                    .setTitle(R.string.notif_gate_title)
                    .setMessage(R.string.notif_gate_body)
                    .setPositiveButton(R.string.notif_gate_allow, (d, w) ->
                            ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIF))
                    .setNegativeButton(R.string.notif_gate_later, (d, w) -> { })
                    .show();
        } catch (Throwable t) { }
    }

    @Override public void onRequestPermissionsResult(int req, @NonNull String[] perms, @NonNull int[] res) {
        super.onRequestPermissionsResult(req, perms, res);
    }

    private void toast(String s) {
        try { android.widget.Toast.makeText(this, s, android.widget.Toast.LENGTH_SHORT).show(); } catch (Throwable t) { }
    }

    @Override public void onBackPressed() {
        final MainActivity self = this;
        try {
            if (webUi != null) {
                webUi.evaluateJavascript("(function(){try{return window.OffexAudioUI&&window.OffexAudioUI.onBack&&window.OffexAudioUI.onBack();}catch(e){return false;}})();",
                        value -> { if (!"true".equals(value)) self.finish(); });
                return;
            }
        } catch (Throwable t) { }
        super.onBackPressed();
    }

    // ================================================================== bridge
    // Every method below is called from the page with EXACTLY its parameter
    // count (the Android bridge resolves by arity).
    public class OffexBridge {

        @JavascriptInterface public String getState() { return stateJson; }

        @JavascriptInterface public void ready() { pushState(); }

        @JavascriptInterface public void log(final String msg) {
            try { Log.i(TAG, msg == null ? "" : msg); } catch (Throwable t) { }
        }

        /** https result -> DownloadManager into the public Downloads folder. */
        @JavascriptInterface public void download(final String url, final String filename, final String mime) {
            runOnUiThread(() -> {
                try {
                    Downloader.fromUrl(MainActivity.this, url, filename, mime);
                    toast(getString(R.string.download_started));
                } catch (Throwable t) { toast(getString(R.string.download_failed)); }
            });
        }

        /** in-page blob result -> written straight into Downloads. */
        @JavascriptInterface public void downloadData(final String b64, final String filename, final String mime) {
            runOnUiThread(() -> {
                String path = Downloader.fromBase64(MainActivity.this, b64, filename, mime);
                if (path != null) toast(getString(R.string.saved_to_downloads) + " \u00b7 " + path);
                else toast(getString(R.string.download_failed));
            });
        }

        /** A job finished: record history, report it, and post a local alert. */
        @JavascriptInterface public void jobDone(final String tool, final String detail, final String url, final String filename) {
            runOnUiThread(() -> {
                try {
                    String when = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.US).format(new Date());
                    HistoryStore.add(MainActivity.this, tool, filename, when, url);
                    HistoryStore.reportAsync(MainActivity.this, tool, filename);
                    Notifier.job(MainActivity.this, getString(R.string.job_done_title), (tool == null ? "" : tool + " \u00b7 ") + (detail == null ? getString(R.string.job_done_body) : detail));
                    pushState();
                } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void setLang(final String code) {
            runOnUiThread(() -> {
                try {
                    Prefs.setLang(MainActivity.this, code);
                    recreate();
                } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void setNotify(final String on) {
            runOnUiThread(() -> {
                try {
                    Prefs.setNotifyOn(MainActivity.this, "1".equals(on) || "true".equalsIgnoreCase(on));
                    if (Prefs.notifyOn(MainActivity.this) && Build.VERSION.SDK_INT >= 33
                            && ContextCompat.checkSelfPermission(MainActivity.this, Manifest.permission.POST_NOTIFICATIONS) != PackageManager.PERMISSION_GRANTED) {
                        ActivityCompat.requestPermissions(MainActivity.this, new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIF);
                    }
                    pushState();
                } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void setSound(final String idx) {
            runOnUiThread(() -> {
                try { Prefs.setSound(MainActivity.this, Integer.parseInt(idx)); pushState(); } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void openLink(final String url) {
            runOnUiThread(() -> openExternal(url));
        }

        @JavascriptInterface public void openMore() {
            runOnUiThread(() -> {
                try {
                    new AlertDialog.Builder(MainActivity.this)
                            .setTitle(R.string.more_title)
                            .setMessage(getString(R.string.more_version) + ": 1.4\n"
                                    + getString(R.string.more_backend) + ": " + getString(R.string.more_backend_value))
                            .setPositiveButton(R.string.close, (d, w) -> { })
                            .show();
                } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void healthPing() { forceHealthPing(); }

        @JavascriptInterface public void clearHistory() {
            runOnUiThread(() -> { try { HistoryStore.clear(MainActivity.this); pushState(); } catch (Throwable t) { } });
        }

        @JavascriptInterface public void showInterstitial() { runOnUiThread(() -> Ads.showInterstitial(MainActivity.this)); }

        @JavascriptInterface public void showRewarded() {
            runOnUiThread(() -> Ads.showRewarded(MainActivity.this, () -> pushState()));
        }
    }
}
'''

p = os.path.join(J, "MainActivity.java")
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, "w", encoding="utf-8") as f:
    f.write(MAIN)
print("GNA3: wrote MainActivity.java")
