# ============================================================================
#  gna_3.py  -  Offex Audio, generator 3 of 6  (MainActivity)
# ============================================================================
#  v1.1 REWRITE.
#
#  What changed and why:
#    * The app used to load a bundled file:// HTML shell and fake the whole
#      pipeline by intercepting backend requests in shouldInterceptRequest().
#      That broke the real Gradio/WebSocket/upload flow, so no genuine job ever
#      ran ("no job handle" / instant fake "COMPLETED 100%").
#    * The WebView now loads the REAL audio website (https://offexmail.online),
#      which already has the working Gradio/HF flow (through its /hf proxy),
#      the real upload %, the real processing, the correct default silence
#      value and the Live badge. The tools therefore behave EXACTLY like the
#      website.
#    * The native request-interception path (BackendProxy) and all fake-job
#      logic are REMOVED. There is no instant fake "job finished".
#
#  The native shell is kept and drives the loaded site:
#    * Bottom tab bar: Remove Silence / Enhance / Voice-BGM scroll the real page
#      (JS scrollIntoView); History and More open native panels.
#    * File chooser: WebChromeClient.onShowFileChooser -> ACTION_OPEN_DOCUMENT
#      (audio/*, video/*) with a persisted read grant for the picked URI.
#    * Downloads: (a) the page's finished blob is captured in JS and written to
#      the public Downloads folder via MediaStore; (b) a real http(s) link the
#      page triggers goes through DownloadManager; (c) a native "Save result"
#      button saves the latest result URL with DownloadManager.
#    * Notifications (permission gate + FCM/local), History store, ads and the
#      multi-language switcher are all kept.
# ============================================================================
import os

J = "android-audio/app/src/main/java/online/offexaudio/app"

MAIN = r'''package online.offexaudio.app;

import android.Manifest;
import android.app.AlertDialog;
import android.content.Intent;
import android.content.pm.PackageManager;
import android.graphics.Typeface;
import android.net.Uri;
import android.os.Build;
import android.os.Bundle;
import android.os.Handler;
import android.os.Looper;
import android.util.Log;
import android.util.TypedValue;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.webkit.ConsoleMessage;
import android.webkit.CookieManager;
import android.webkit.JavascriptInterface;
import android.webkit.ValueCallback;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceError;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;
import android.widget.ImageView;
import android.widget.LinearLayout;
import android.widget.TextView;
import android.widget.Toast;

import androidx.annotation.NonNull;
import androidx.appcompat.app.AppCompatActivity;
import androidx.core.app.ActivityCompat;
import androidx.core.content.ContextCompat;

import org.json.JSONArray;
import org.json.JSONObject;

import java.text.SimpleDateFormat;
import java.util.Date;
import java.util.Locale;

/**
 * Offex Audio v1.1.
 *
 * The whole screen is the REAL audio website loaded in a WebView, wrapped in a
 * native shell (bottom tabs, notifications, Downloads, history, ads, language
 * switcher). The tools run through the genuine Gradio / Hugging Face flow, so
 * upload progress, server processing and results are exactly what the website
 * does - no native request interception, no fake "job finished".
 */
public class MainActivity extends AppCompatActivity {

    private static final String TAG = "OffexAudio";

    /** The live audio website (real Gradio/HF flow through its /hf proxy). */
    private static final String SITE_URL = "https://offexmail.online/";
    private static final String SITE_HOST = "offexmail.online";
    private static final String OFFLINE_URL = "file:///android_asset/offline.html";

    private static final int REQ_NOTIF = 8801;
    private static final int REQ_FILE = 8802;

    private WebView webUi;
    private View adBanner;
    private TextView saveResult;
    private ViewGroup panelHost;
    private LinearLayout panelContent;

    private ValueCallback<Uri[]> filePathCallback;
    private final Handler ui = new Handler(Looper.getMainLooper());

    private volatile String lastResultUrl = null;
    private volatile String lastResultName = null;
    private volatile String lastResultMime = "audio/mpeg";
    private volatile boolean offlineShown = false;

    private static MainActivity live0;

    // Injected after each page load. Installs a small bridge into the REAL site:
    //  * captures the finished blob download and hands it to the native
    //    Downloader (so results land in the device's Downloads folder);
    //  * watches the site's result download links and reports a completed job
    //    to native (history + notification).
    private static final String BRIDGE_JS =
            "(function(){try{" +
            "if(window.__offexNativeBridge)return;window.__offexNativeBridge=true;" +
            "function b64(blob,cb){try{var fr=new FileReader();fr.onload=function(){var s=String(fr.result||'');var i=s.indexOf(',');cb(i>=0?s.slice(i+1):'');};fr.onerror=function(){cb(null);};fr.readAsDataURL(blob);}catch(e){cb(null);}}" +
            "var orig=window.triggerBlobDownload;" +
            "window.triggerBlobDownload=function(blob,filename){try{if(!blob){if(orig)return orig(blob,filename);return;}b64(blob,function(data){if(!data){if(orig)try{orig(blob,filename);}catch(e){}return;}try{OffexNative.downloadData(data,String(filename||'offex_audio_output'),(blob&&blob.type)||'audio/mpeg');}catch(e){if(orig)try{orig(blob,filename);}catch(e2){}}});}catch(e){if(orig)try{orig(blob,filename);}catch(e2){}}};" +
            "var map=[['downloadLink','Remove Silence'],['enhancedDownload','Enhance Audio'],['vocalsDownload','Voice / BGM'],['bgmDownload','Voice / BGM']];" +
            "var seen={};var last={};" +
            "function scan(){for(var i=0;i<map.length;i++){var id=map[i][0],tool=map[i][1],el=document.getElementById(id);if(!el)continue;var u=el.dataset?el.dataset.fileUrl:null;if(u&&!seen[id]){seen[id]=u;var fn=(el.dataset&&el.dataset.filename)||'';var now=Date.now();if(!last[tool]||(now-last[tool])>8000){last[tool]=now;try{OffexNative.jobDone(tool,fn,u,fn);}catch(e){}}}else if(!u&&seen[id]){delete seen[id];}}}" +
            "setInterval(scan,1500);scan();" +
            "}catch(e){}})();";

    @Override protected void onCreate(Bundle b) {
        super.onCreate(b);
        live0 = this;
        LocaleHelper.wrap(this);
        setContentView(R.layout.activity_main);
        Notifier.ensureChannel(this);
        Config.loadAsync(this);

        saveResult = findViewById(R.id.saveResult);
        panelHost = findViewById(R.id.panelHost);
        panelContent = findViewById(R.id.panelContent);
        if (saveResult != null) saveResult.setOnClickListener(v -> saveCurrentResult());

        setupTabs();
        setupWebUi();

        adBanner = findViewById(R.id.adBanner);
        if (adBanner != null && Config.flag("show_banner_ad", true)) {
            adBanner.setVisibility(View.VISIBLE);
            Ads.loadBanner(this, (ViewGroup) adBanner);
        }
        Ads.loadInterstitial(this);
        Ads.loadRewarded(this);
        maybeShowNotifGate();
        Ads.showAppOpenIfAvailable(this);
    }

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
            ws.setJavaScriptCanOpenWindowsAutomatically(true);
            ws.setSupportMultipleWindows(false);
            ws.setMediaPlaybackRequiresUserGesture(false);
            ws.setCacheMode(WebSettings.LOAD_DEFAULT);
            ws.setLoadWithOverviewMode(true);
            ws.setUseWideViewPort(true);
            ws.setSupportZoom(false);
            ws.setBuiltInZoomControls(false);
            ws.setDisplayZoomControls(false);
            // A normal mobile user-agent (the site is responsive and expects it).
            ws.setUserAgentString("Mozilla/5.0 (Linux; Android 13; Pixel 6) AppleWebKit/537.36 "
                    + "(KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36");
            if (Build.VERSION.SDK_INT >= 21) {
                // The site is HTTPS; allow compatibility so no resource is blocked.
                ws.setMixedContentMode(WebSettings.MIXED_CONTENT_COMPATIBILITY_MODE);
            }
            webUi.setBackgroundColor(0xFF05060D);
            webUi.setVerticalScrollBarEnabled(false);
            webUi.setHorizontalScrollBarEnabled(false);
            webUi.setOverScrollMode(View.OVER_SCROLL_NEVER);

            CookieManager cm = CookieManager.getInstance();
            cm.setAcceptCookie(true);
            if (Build.VERSION.SDK_INT >= 21) cm.setAcceptThirdPartyCookies(webUi, true);

            webUi.setWebViewClient(new WebViewClient() {
                @Override public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest r) {
                    return handleNav(r.getUrl().toString());
                }
                @Override public boolean shouldOverrideUrlLoading(WebView v, String url) {
                    return handleNav(url);
                }
                @Override public void onPageFinished(WebView v, String url) {
                    try {
                        if (url != null && url.contains(SITE_HOST)) offlineShown = false;
                        injectBridge();
                    } catch (Throwable t) { }
                }
                @Override public void onReceivedError(WebView v, WebResourceRequest r, WebResourceError e) {
                    try {
                        if (r != null && r.isForMainFrame() && !offlineShown) {
                            offlineShown = true;
                            v.loadUrl(OFFLINE_URL);
                        }
                    } catch (Throwable t) { }
                }
            });

            webUi.setWebChromeClient(new WebChromeClient() {
                @Override public boolean onConsoleMessage(ConsoleMessage m) {
                    try { Log.i(TAG, "console: " + m.message() + " @" + m.lineNumber()); } catch (Throwable t) { }
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
                        i.addFlags(Intent.FLAG_GRANT_READ_URI_PERMISSION);
                        i.addFlags(Intent.FLAG_GRANT_PERSISTABLE_URI_PERMISSION);
                        startActivityForResult(Intent.createChooser(i, getString(R.string.choose_file)), REQ_FILE);
                        return true;
                    } catch (Throwable t) {
                        filePathCallback = null;
                        toast(getString(R.string.pick_error));
                        return false;
                    }
                }
            });

            // (b) any real http(s) link the page triggers is saved natively.
            webUi.setDownloadListener((url, ua, contentDisposition, mime, len) -> {
                try {
                    if (url == null) return;
                    if (url.startsWith("blob:") || url.startsWith("data:")) return; // handled in JS
                    Downloader.fromUrl(MainActivity.this, url, guessName(contentDisposition, url), mime);
                    toast(getString(R.string.download_started));
                } catch (Throwable t) { toast(getString(R.string.download_failed)); }
            });

            webUi.addJavascriptInterface(new OffexBridge(), "OffexNative");
            webUi.loadUrl(SITE_URL);
        } catch (Throwable t) { Log.e(TAG, "setupWebUi: " + t); }
    }

    private void injectBridge() {
        try { if (webUi != null) webUi.evaluateJavascript(BRIDGE_JS, null); }
        catch (Throwable t) { }
    }

    /** Keep offexmail.online in-app; open everything else (mailto/tel/other hosts) externally. */
    private boolean handleNav(String url) {
        try {
            if (url == null) return false;
            String u = url.trim();
            if (u.startsWith("about:") || u.startsWith("blob:") || u.startsWith("data:")
                    || u.startsWith("javascript:") || u.startsWith("file:")) return false;
            Uri uri = Uri.parse(u);
            String scheme = uri.getScheme() == null ? "" : uri.getScheme().toLowerCase(Locale.US);
            if (scheme.equals("mailto") || scheme.equals("tel") || scheme.equals("sms")) {
                Intent i = new Intent(Intent.ACTION_VIEW, uri);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
                return true;
            }
            String host = uri.getHost() == null ? "" : uri.getHost();
            if (host.equals(SITE_HOST) || host.endsWith("." + SITE_HOST)) return false;
            if (scheme.equals("http") || scheme.equals("https")) {
                Intent i = new Intent(Intent.ACTION_VIEW, uri);
                i.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK);
                startActivity(i);
                return true;
            }
            return false;
        } catch (Throwable t) { return false; }
    }

    @Override protected void onActivityResult(int req, int res, Intent data) {
        if (req == REQ_FILE) {
            Uri[] out = null;
            if (res == RESULT_OK && data != null && data.getData() != null) {
                Uri uri = data.getData();
                try {
                    getContentResolver().takePersistableUriPermission(uri, Intent.FLAG_GRANT_READ_URI_PERMISSION);
                } catch (Throwable t) { /* not persistable - the transient grant still applies */ }
                out = new Uri[]{ uri };
            }
            if (filePathCallback != null) { filePathCallback.onReceiveValue(out); filePathCallback = null; }
            return;
        }
        super.onActivityResult(req, res, data);
    }

    // --------------------------------------------------------------- tab bar
    private void setupTabs() {
        setTab(R.id.tabRemove, "remove");
        setTab(R.id.tabEnhance, "enhance");
        setTab(R.id.tabIsolate, "isolate");
        setTab(R.id.tabHistory, "history");
        setTab(R.id.tabMore, "more");
        highlightTab("remove");
    }

    private void setTab(int id, final String tab) {
        try {
            View v = findViewById(id);
            if (v != null) v.setOnClickListener(x -> onTab(tab));
        } catch (Throwable t) { }
    }

    private void onTab(String tab) {
        closePanel();
        if ("remove".equals(tab)) { highlightTab("remove"); scrollTo("removeTool"); }
        else if ("enhance".equals(tab)) { highlightTab("enhance"); scrollTo("enhanceTool"); }
        else if ("isolate".equals(tab)) { highlightTab("isolate"); scrollTo("isolateTool"); }
        else if ("history".equals(tab)) { highlightTab("history"); showHistoryPanel(); }
        else if ("more".equals(tab)) { highlightTab("more"); showMorePanel(); }
    }

    /** Drive the loaded site to a tool section (real site UI, real progress). */
    private void scrollTo(String elementId) {
        try {
            if (webUi == null) return;
            String js = "(function(){try{var el=document.getElementById('" + elementId + "');"
                    + "if(el){el.scrollIntoView({behavior:'smooth',block:'start'});}"
                    + "else{window.scrollTo(0,0);}return !!el;}catch(e){return false;}})();";
            webUi.evaluateJavascript(js, null);
        } catch (Throwable t) { }
    }

    private void highlightTab(String active) {
        tintTab(R.id.tabRemove, "remove".equals(active));
        tintTab(R.id.tabEnhance, "enhance".equals(active));
        tintTab(R.id.tabIsolate, "isolate".equals(active));
        tintTab(R.id.tabHistory, "history".equals(active));
        tintTab(R.id.tabMore, "more".equals(active));
    }

    private void tintTab(int id, boolean on) {
        try {
            ViewGroup g = findViewById(id);
            if (g == null) return;
            int color = on ? 0xFF22D3EE : 0xFF9AA3C0;
            for (int i = 0; i < g.getChildCount(); i++) {
                View c = g.getChildAt(i);
                if (c instanceof ImageView) ((ImageView) c).setColorFilter(color);
                else if (c instanceof TextView) ((TextView) c).setTextColor(color);
            }
        } catch (Throwable t) { }
    }

    // --------------------------------------------------------------- panels
    private void openPanel() { try { if (panelHost != null) panelHost.setVisibility(View.VISIBLE); } catch (Throwable t) { } }

    private void closePanel() {
        try {
            if (panelHost != null) panelHost.setVisibility(View.GONE);
            if (panelContent != null) panelContent.removeAllViews();
        } catch (Throwable t) { }
    }

    private TextView panelTitle(String s) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextColor(0xFFEEF1FB);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 20);
        t.setTypeface(Typeface.DEFAULT_BOLD);
        t.setPadding(0, 0, 0, 18);
        return t;
    }

    private TextView panelBody(String s) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextColor(0xFF9AA3C0);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 14);
        t.setPadding(0, 0, 0, 14);
        return t;
    }

    private TextView panelButton(String s, final Runnable r) {
        TextView t = new TextView(this);
        t.setText(s);
        t.setTextColor(0xFFEEF1FB);
        t.setTextSize(TypedValue.COMPLEX_UNIT_SP, 15);
        t.setPadding(30, 30, 30, 30);
        t.setGravity(Gravity.CENTER_VERTICAL);
        t.setBackgroundColor(0xFF141830);
        LinearLayout.LayoutParams lp = new LinearLayout.LayoutParams(
                ViewGroup.LayoutParams.MATCH_PARENT, ViewGroup.LayoutParams.WRAP_CONTENT);
        lp.setMargins(0, 0, 0, 10);
        t.setLayoutParams(lp);
        t.setClickable(true);
        t.setOnClickListener(v -> { if (r != null) r.run(); });
        return t;
    }

    private void showHistoryPanel() {
        try {
            if (panelContent == null) return;
            panelContent.removeAllViews();
            panelContent.addView(panelTitle(getString(R.string.history_title)));
            JSONArray h = HistoryStore.list(this);
            if (h.length() == 0) {
                panelContent.addView(panelBody(getString(R.string.history_empty)));
            } else {
                for (int i = 0; i < h.length(); i++) {
                    JSONObject o = h.getJSONObject(i);
                    final String tool = o.optString("tool");
                    final String file = o.optString("file");
                    final String when = o.optString("when");
                    final String url = o.optString("url");
                    String line = (tool.isEmpty() ? getString(R.string.app_name) : tool)
                            + "\n" + file + (when.isEmpty() ? "" : "  \u00b7  " + when);
                    panelContent.addView(panelButton(line, () -> {
                        if (url != null && (url.startsWith("http://") || url.startsWith("https://"))) {
                            Downloader.fromUrl(MainActivity.this, url, file, "audio/mpeg");
                            toast(getString(R.string.download_started));
                        } else {
                            toast(getString(R.string.download_failed));
                        }
                    }));
                }
            }
            panelContent.addView(panelButton(getString(R.string.history_clear), () -> {
                HistoryStore.clear(MainActivity.this);
                showHistoryPanel();
            }));
            panelContent.addView(panelButton(getString(R.string.close), this::closePanel));
            openPanel();
        } catch (Throwable t) { Log.w(TAG, "history panel: " + t); }
    }

    private void showMorePanel() {
        try {
            if (panelContent == null) return;
            panelContent.removeAllViews();
            panelContent.addView(panelTitle(getString(R.string.more_title)));

            panelContent.addView(panelBody(getString(R.string.more_language)));
            final String cur = LocaleHelper.current(this);
            for (String[] l : LocaleHelper.LANGS) {
                final String code = l[0];
                String prefix = code.equals(cur) ? "\u2713  " : "     ";
                panelContent.addView(panelButton(prefix + l[1], () -> applyLang(code)));
            }

            boolean on = Prefs.notifyOn(this);
            panelContent.addView(panelBody(getString(R.string.more_notifications) + ": "
                    + getString(on ? R.string.more_notifications_on : R.string.more_notifications_off)));
            panelContent.addView(panelButton(
                    (on ? getString(R.string.more_notifications_off) : getString(R.string.more_notifications_on))
                            + " \u00b7 " + getString(R.string.more_notifications),
                    () -> { toggleNotify(); showMorePanel(); }));

            int snd = Math.max(0, Math.min(Notifier.SND_NAMES.length - 1, Prefs.sound(this)));
            panelContent.addView(panelBody(getString(R.string.more_sound) + ": " + Notifier.SND_NAMES[snd]));
            for (int i = 0; i < Notifier.SND_NAMES.length; i++) {
                final int idx = i;
                String prefix = (Prefs.sound(this) == i) ? "\u2713  " : "     ";
                panelContent.addView(panelButton(prefix + Notifier.SND_NAMES[i], () -> {
                    Prefs.setSound(MainActivity.this, idx);
                    Notifier.job(MainActivity.this, getString(R.string.job_done_title), getString(R.string.job_done_body));
                    showMorePanel();
                }));
            }

            panelContent.addView(panelBody(getString(R.string.more_version) + ": 1.1\n"
                    + getString(R.string.more_backend) + ": " + getString(R.string.more_backend_value)));
            panelContent.addView(panelButton(getString(R.string.more_privacy), () -> {
                closePanel();
                if (webUi != null) webUi.loadUrl(SITE_URL + "privacy.html");
            }));
            panelContent.addView(panelButton(getString(R.string.close), this::closePanel));
            openPanel();
        } catch (Throwable t) { Log.w(TAG, "more panel: " + t); }
    }

    private void applyLang(String code) {
        try { Prefs.setLang(this, code); closePanel(); recreate(); } catch (Throwable t) { }
    }

    private void toggleNotify() {
        try {
            boolean on = !Prefs.notifyOn(this);
            Prefs.setNotifyOn(this, on);
            if (on && Build.VERSION.SDK_INT >= 33
                    && ContextCompat.checkSelfPermission(this, Manifest.permission.POST_NOTIFICATIONS)
                    != PackageManager.PERMISSION_GRANTED) {
                ActivityCompat.requestPermissions(this, new String[]{Manifest.permission.POST_NOTIFICATIONS}, REQ_NOTIF);
            }
        } catch (Throwable t) { }
    }

    // --------------------------------------------------------------- downloads
    /** (c) native "Save result" affordance for the latest real (http/https) result. */
    private void saveCurrentResult() {
        try {
            if (lastResultUrl == null
                    || !(lastResultUrl.startsWith("http://") || lastResultUrl.startsWith("https://"))) {
                toast(getString(R.string.download_failed));
                return;
            }
            Downloader.fromUrl(this, lastResultUrl, lastResultName, lastResultMime);
            toast(getString(R.string.download_started));
        } catch (Throwable t) { toast(getString(R.string.download_failed)); }
    }

    private static String guessName(String contentDisposition, String url) {
        try {
            if (contentDisposition != null) {
                java.util.regex.Matcher m = java.util.regex.Pattern
                        .compile("filename\\*?=(?:UTF-8'')?\"?([^\";]+)\"?")
                        .matcher(contentDisposition);
                if (m.find()) return m.group(1);
            }
        } catch (Throwable t) { }
        try {
            String p = Uri.parse(url).getLastPathSegment();
            if (p != null && p.length() > 0) return p;
        } catch (Throwable t) { }
        return "offex_audio_output";
    }

    // --------------------------------------------------------------- notify
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
        try { Toast.makeText(this, s, Toast.LENGTH_SHORT).show(); } catch (Throwable t) { }
    }

    @Override public void onBackPressed() {
        try {
            if (panelHost != null && panelHost.getVisibility() == View.VISIBLE) { closePanel(); return; }
            if (webUi != null && webUi.canGoBack()) { webUi.goBack(); return; }
        } catch (Throwable t) { }
        super.onBackPressed();
    }

    static void onPush() {
        // FCM already delivered its alert through Notifier; nothing else to do.
        MainActivity a = live0;
        if (a == null) return;
    }

    // ================================================================== bridge
    // Each method is called from the page with EXACTLY its declared parameter
    // count (the Android bridge resolves @JavascriptInterface by arity).
    public class OffexBridge {

        /** (a) the page's finished blob -> written straight into Downloads. */
        @JavascriptInterface public void downloadData(final String b64, final String filename, final String mime) {
            new Thread(() -> {
                final String path = Downloader.fromBase64(MainActivity.this, b64, filename, mime);
                runOnUiThread(() -> {
                    if (path != null) toast(getString(R.string.saved_to_downloads) + " \u00b7 " + path);
                    else toast(getString(R.string.download_failed));
                });
            }).start();
        }

        /** A real http(s) URL handed over by the page. */
        @JavascriptInterface public void download(final String url, final String filename, final String mime) {
            runOnUiThread(() -> {
                try {
                    Downloader.fromUrl(MainActivity.this, url, filename, mime);
                    toast(getString(R.string.download_started));
                } catch (Throwable t) { toast(getString(R.string.download_failed)); }
            });
        }

        /** The site produced a result: record history, expose Save, post an alert. */
        @JavascriptInterface public void jobDone(final String tool, final String detail, final String url, final String filename) {
            runOnUiThread(() -> {
                try {
                    String when = new SimpleDateFormat("dd/MM/yyyy HH:mm", Locale.US).format(new Date());
                    boolean real = url != null && (url.startsWith("http://") || url.startsWith("https://"));
                    HistoryStore.add(MainActivity.this, tool, filename, when, real ? url : "");
                    HistoryStore.reportAsync(MainActivity.this, tool, filename);
                    if (real) {
                        lastResultUrl = url;
                        lastResultName = filename;
                        if (saveResult != null) saveResult.setVisibility(View.VISIBLE);
                    }
                    Notifier.job(MainActivity.this, getString(R.string.job_done_title),
                            (tool == null ? "" : tool + " \u00b7 ")
                                    + (detail == null ? getString(R.string.job_done_body) : detail));
                } catch (Throwable t) { }
            });
        }

        @JavascriptInterface public void setLang(final String code) { runOnUiThread(() -> applyLang(code)); }

        @JavascriptInterface public void openLink(final String url) { runOnUiThread(() -> handleNav(url)); }

        @JavascriptInterface public void log(final String msg) {
            try { Log.i(TAG, msg == null ? "" : msg); } catch (Throwable t) { }
        }
    }
}
'''

p = os.path.join(J, "MainActivity.java")
os.makedirs(os.path.dirname(p), exist_ok=True)
with open(p, "w", encoding="utf-8") as f:
    f.write(MAIN)
print("GNA3: wrote MainActivity.java (loads real site, no request interception)")
