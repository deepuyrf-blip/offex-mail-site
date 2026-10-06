import os, re

# ---------------------------------------------------------------------------
# gn_u.py  (runs LAST, after gn_t, in the android.yml pipeline)
#
# v3.8 changes:
#   1. Notification permission is now MANDATORY: a blocking, non-cancelable
#      gate on launch + resume. The core flow cannot be used until the user
#      grants POST_NOTIFICATIONS.
#   2. Inbox / Switch bottom-nav fix: each tab now scrolls to its OWN section
#      heading (secInbox / secSwitch) instead of a view at the tail of the
#      section, which made Inbox land on the Switch screen and Switch land on
#      the features section.
#   3. Circular logo: a circular logo asset for the splash + a circular
#      launcher icon (roundIcon), keeping the same artwork.
#   4. "Silent feature update" (remote-config, no APK, no version change): the
#      backend serves a `feature` payload the app applies live on launch/resume
#      (banner text, a one-time "What's new" card, feature flags + string
#      overrides). Separate from the full-version update track.
#   5. All ad placements wired: App Open, Banner, Interstitial, Native (plus
#      the existing Rewarded), every unit id driven by the admin panel config
#      with Google's official TEST ids as fallbacks.
#   6. Version 3.7 -> 3.8.
#
# Everything emitted by gn_a..gn_t is preserved: API endpoints/JSON fields, the
# mail ingest path, FCM pushes, the support feature, bundled notification
# sounds, the bottom nav, LIGHT theme default, the features section, the
# announcement banner, the full-version update prompt and the Create-button
# loading animation.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def R(p):
    return open(p, encoding="utf-8").read()

def must(s, anchor, name):
    if anchor not in s:
        raise SystemExit("gn_u: FATAL anchor missing (%s)" % name)
    return s

# ===========================================================================
# 5 : Ads.java  -> App Open + Banner + Interstitial + Native + Rewarded
# ===========================================================================
ADS = r'''package online.mytempmail.app;
import android.app.Activity;
import android.graphics.Typeface;
import android.view.View;
import android.view.ViewGroup;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import android.widget.TextView;
import com.google.android.gms.ads.AdError;
import com.google.android.gms.ads.AdLoader;
import com.google.android.gms.ads.AdRequest;
import com.google.android.gms.ads.AdSize;
import com.google.android.gms.ads.AdView;
import com.google.android.gms.ads.FullScreenContentCallback;
import com.google.android.gms.ads.LoadAdError;
import com.google.android.gms.ads.MobileAds;
import com.google.android.gms.ads.appopen.AppOpenAd;
import com.google.android.gms.ads.interstitial.InterstitialAd;
import com.google.android.gms.ads.interstitial.InterstitialAdLoadCallback;
import com.google.android.gms.ads.nativead.MediaView;
import com.google.android.gms.ads.nativead.NativeAd;
import com.google.android.gms.ads.nativead.NativeAdView;
import com.google.android.gms.ads.rewarded.RewardedAd;
import com.google.android.gms.ads.rewarded.RewardedAdLoadCallback;
import org.json.JSONObject;

public class Ads {
    // Google official TEST ad unit ids (fallbacks only; the admin panel wins).
    public static final String TEST_BANNER    = "ca-app-pub-3940256099942544/6300978111";
    public static final String TEST_INTER     = "ca-app-pub-3940256099942544/1033173712";
    public static final String TEST_REWARDED  = "ca-app-pub-3940256099942544/5224354917";
    public static final String TEST_APP_OPEN  = "ca-app-pub-3940256099942544/9257395921";
    public static final String TEST_NATIVE    = "ca-app-pub-3940256099942544/2247696110";

    private static boolean sdkStarted = false;
    private static boolean bannerPlaced = false;
    private static boolean nativePlaced = false;
    private static Activity act;
    private static AppOpenAd appOpenAd = null;
    private static boolean appOpenLoading = false;
    private static long appOpenShownAt = 0L;
    private static InterstitialAd interstitialAd = null;
    private static boolean interstitialLoading = false;
    private static long interstitialShownAt = 0L;

    private static boolean on(){
        try { JSONObject ad = Config.j.optJSONObject("ads"); return ad != null && ad.optBoolean("on"); }
        catch(Exception e){ return false; }
    }
    private static String unit(String key, String fallback){
        try {
            JSONObject ad = Config.j.optJSONObject("ads");
            String u = ad == null ? "" : ad.optString(key).trim();
            if(!valid(u)) u = fallback;
            return u;
        } catch(Exception e){ return fallback; }
    }
    private static boolean valid(String u){
        if(u == null) return false;
        int i = u.indexOf('/');
        if(i < 0) return false;
        return u.startsWith("ca-app-pub-") && u.substring(i + 1).trim().length() >= 9;
    }
    private static int dp(Activity a, int v){
        try { return (int)(a.getResources().getDisplayMetrics().density * v); } catch(Exception e){ return v; }
    }

    public static void init(final Activity a){
        try {
            act = a;
            if(!sdkStarted){ sdkStarted = true; MobileAds.initialize(a, s -> {}); }
            if(!on()) return;
            loadBanner();
            nativeAd(a);
            preloadAppOpen();
            preloadInterstitial();
        } catch(Exception e){}
    }

    // Insert an ad inside the ScrollView content so it is actually visible.
    private static ViewGroup host(Activity a){
        try {
            View root = a.findViewById(android.R.id.content);
            if(!(root instanceof ViewGroup)) return null;
            ViewGroup content = (ViewGroup) root;
            if(content.getChildCount() == 0) return null;
            View v = content.getChildAt(0);
            if(!(v instanceof ViewGroup)) return null;
            ViewGroup g = (ViewGroup) v;
            if(g instanceof ScrollView && g.getChildCount() > 0 && g.getChildAt(0) instanceof ViewGroup)
                return (ViewGroup) g.getChildAt(0);
            for(int i = 0; i < g.getChildCount(); i++){
                View c = g.getChildAt(i);
                if(c instanceof ScrollView && ((ViewGroup) c).getChildCount() > 0
                        && ((ViewGroup) c).getChildAt(0) instanceof ViewGroup)
                    return (ViewGroup)((ViewGroup) c).getChildAt(0);
            }
            return g;
        } catch(Exception e){ return null; }
    }

    private static void loadBanner(){
        try {
            if(bannerPlaced || act == null) return;
            if(!on()) return;
            ViewGroup g = host(act);
            if(g == null) return;
            AdView av = new AdView(act);
            av.setAdSize(AdSize.BANNER);
            av.setAdUnitId(unit("banner", TEST_BANNER));
            g.addView(av, 0);
            av.loadAd(new AdRequest.Builder().build());
            bannerPlaced = true;
        } catch(Exception e){}
    }

    // ---- NATIVE -----------------------------------------------------------
    public static void nativeAd(final Activity a){
        try {
            if(nativePlaced || a == null) return;
            if(!on()) return;
            final View box = a.findViewById(R.id.nativeAdBox);
            if(!(box instanceof ViewGroup)) return;
            final ViewGroup container = (ViewGroup) box;
            AdLoader loader = new AdLoader.Builder(a, unit("native", TEST_NATIVE))
                .forNativeAd(new NativeAd.OnNativeAdLoadedListener(){
                    @Override public void onNativeAdLoaded(NativeAd ad){
                        try {
                            container.removeAllViews();
                            NativeAdView nav = new NativeAdView(a);
                            LinearLayout col = new LinearLayout(a);
                            col.setOrientation(LinearLayout.VERTICAL);
                            col.setPadding(dp(a, 16), dp(a, 14), dp(a, 16), dp(a, 14));
                            col.setBackgroundResource(R.drawable.bg_card);
                            TextView label = new TextView(a);
                            label.setText("Sponsored");
                            label.setTextSize(10);
                            label.setTextColor(0xFF9A96AD);
                            TextView hl = new TextView(a);
                            hl.setTextSize(15);
                            hl.setTypeface(null, Typeface.BOLD);
                            hl.setTextColor(0xFF1B1730);
                            TextView body = new TextView(a);
                            body.setTextSize(13);
                            body.setTextColor(0xFF5C5875);
                            MediaView mv = new MediaView(a);
                            TextView cta = new TextView(a);
                            cta.setTextSize(13);
                            cta.setTextColor(0xFFE53935);
                            cta.setTypeface(null, Typeface.BOLD);
                            cta.setPadding(0, dp(a, 8), 0, 0);
                            col.addView(label);
                            col.addView(hl);
                            col.addView(body);
                            col.addView(mv);
                            col.addView(cta);
                            nav.addView(col);
                            nav.setHeadlineView(hl);
                            nav.setBodyView(body);
                            nav.setMediaView(mv);
                            nav.setCallToActionView(cta);
                            hl.setText(ad.getHeadline() == null ? "" : ad.getHeadline());
                            if(ad.getBody() != null) body.setText(ad.getBody());
                            if(ad.getCallToAction() != null) cta.setText(ad.getCallToAction());
                            nav.setNativeAd(ad);
                            container.addView(nav);
                            container.setVisibility(View.VISIBLE);
                            nativePlaced = true;
                        } catch(Exception e){}
                    }
                })
                .build();
            loader.loadAd(new AdRequest.Builder().build());
        } catch(Exception e){}
    }

    // ---- APP OPEN ---------------------------------------------------------
    private static void preloadAppOpen(){
        try {
            if(!on() || appOpenAd != null || appOpenLoading) return;
            appOpenLoading = true;
            AppOpenAd.load(act, unit("app_open", TEST_APP_OPEN), new AdRequest.Builder().build(),
                new AppOpenAd.AppOpenAdLoadCallback(){
                    @Override public void onAdLoaded(AppOpenAd ad){ appOpenAd = ad; appOpenLoading = false; }
                    @Override public void onAdFailedToLoad(LoadAdError e){ appOpenLoading = false; }
                });
        } catch(Exception e){ appOpenLoading = false; }
    }

    public static void showAppOpen(final Activity a){
        try {
            if(!on() || a == null) return;
            long now = System.currentTimeMillis();
            if(appOpenShownAt != 0 && now - appOpenShownAt < 4L * 3600L * 1000L) return;
            if(appOpenAd != null){
                appOpenAd.setFullScreenContentCallback(new FullScreenContentCallback(){
                    @Override public void onAdDismissedFullScreenContent(){ appOpenAd = null; }
                    @Override public void onAdFailedToShowFullScreenContent(AdError e){ appOpenAd = null; }
                });
                appOpenAd.show(a);
                appOpenShownAt = now;
            } else if(!appOpenLoading){
                appOpenLoading = true;
                AppOpenAd.load(a, unit("app_open", TEST_APP_OPEN), new AdRequest.Builder().build(),
                    new AppOpenAd.AppOpenAdLoadCallback(){
                        @Override public void onAdLoaded(AppOpenAd ad){
                            appOpenAd = ad; appOpenLoading = false;
                            try { showAppOpen(a); } catch(Exception e){}
                        }
                        @Override public void onAdFailedToLoad(LoadAdError e){ appOpenLoading = false; }
                    });
            }
        } catch(Exception e){}
    }

    // ---- INTERSTITIAL -----------------------------------------------------
    private static void preloadInterstitial(){
        try {
            if(!on() || interstitialAd != null || interstitialLoading) return;
            interstitialLoading = true;
            InterstitialAd.load(act, unit("interstitial", TEST_INTER), new AdRequest.Builder().build(),
                new InterstitialAdLoadCallback(){
                    @Override public void onAdLoaded(InterstitialAd ad){ interstitialAd = ad; interstitialLoading = false; }
                    @Override public void onAdFailedToLoad(LoadAdError e){ interstitialLoading = false; }
                });
        } catch(Exception e){ interstitialLoading = false; }
    }

    public static void interstitial(final Activity a, final Runnable after){
        final boolean[] ran = { false };
        final Runnable go = () -> { if(!ran[0]){ ran[0] = true; try { if(after != null) after.run(); } catch(Exception e){} } };
        try {
            if(!on() || a == null){ go.run(); return; }
            long now = System.currentTimeMillis();
            if(interstitialShownAt != 0 && now - interstitialShownAt < 60L * 1000L){ go.run(); return; }
            if(interstitialAd != null){
                interstitialAd.setFullScreenContentCallback(new FullScreenContentCallback(){
                    @Override public void onAdDismissedFullScreenContent(){ interstitialAd = null; preloadInterstitial(); go.run(); }
                    @Override public void onAdFailedToShowFullScreenContent(AdError e){ interstitialAd = null; go.run(); }
                });
                interstitialAd.show(a);
                interstitialShownAt = now;
            } else {
                preloadInterstitial();
                go.run();
            }
        } catch(Exception e){ go.run(); }
    }

    // ---- REWARDED (create inbox) -----------------------------------------
    public static void rewarded(final Activity a, final Runnable after){
        final boolean[] ran = { false };
        final Runnable go = () -> { if(!ran[0]){ ran[0] = true; try { if(after != null) after.run(); } catch(Exception e){} } };
        try {
            if(!on() || a == null){ go.run(); return; }
            RewardedAd.load(a, unit("rewarded", TEST_REWARDED), new AdRequest.Builder().build(),
                new RewardedAdLoadCallback(){
                    @Override public void onAdLoaded(RewardedAd r){
                        try {
                            r.setFullScreenContentCallback(new FullScreenContentCallback(){
                                @Override public void onAdDismissedFullScreenContent(){ go.run(); }
                                @Override public void onAdFailedToShowFullScreenContent(AdError e){ go.run(); }
                            });
                            r.show(a, reward -> {});
                        } catch(Exception e){ go.run(); }
                    }
                    @Override public void onAdFailedToLoad(LoadAdError e){ go.run(); }
                });
        } catch(Exception e){ go.run(); }
    }
}
'''
W(J + "/Ads.java", ADS)

# ===========================================================================
# 4 : Config.java  -> remote config + silent feature-update + visible banner
# ===========================================================================
CFG = r'''package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Context;
import android.content.Intent;
import android.content.SharedPreferences;
import android.graphics.Color;
import android.net.Uri;
import android.view.Gravity;
import android.view.View;
import android.view.ViewGroup;
import android.widget.ScrollView;
import android.widget.TextView;
import org.json.JSONObject;

public class Config {
    public static JSONObject j = new JSONObject();
    private static SharedPreferences sp(Context c){ return c.getSharedPreferences("offex", Context.MODE_PRIVATE); }
    private static int lastTs(Context c){ return sp(c).getInt("push_ts", 0); }
    private static void setLastTs(Context c, int t){ sp(c).edit().putInt("push_ts", t).apply(); }
    private static boolean shownBanner = false;
    private static boolean shownFeatBanner = false;
    private static Context ctx = null;

    public static void refresh(){
        try { j = new JSONObject(ApiClient.get("/api/app-config")); } catch(Exception e){}
    }

    public static void push(Context c){
        try {
            JSONObject p = j.optJSONObject("push");
            if(p == null) return;
            int ts = p.optInt("ts");
            String body = p.optString("body");
            if(ts <= 0 || body.isEmpty()) return;
            if(ts <= lastTs(c)) return;
            setLastTs(c, ts);
            Notifier.mail(c, p.optString("title"), body);
        } catch(Exception e){}
    }

    public static void apply(final Activity a){
        try {
            ctx = a;
            new Thread(() -> {
                refresh();
                try {
                    a.runOnUiThread(() -> {
                        try { push(a); } catch(Exception e){}
                        try { updateCheck(a); } catch(Exception e){}
                        try { banner(a); } catch(Exception e){}
                        try { Ads.init(a); } catch(Exception e){}
                        try { applyFeature(a, null); } catch(Exception e){}
                    });
                } catch(Exception e){}
            }).start();
        } catch(Exception e){}
    }

    // Refresh config in the background, then re-apply the silent feature update.
    public static void refreshFeature(final Activity a, final Runnable afterUI){
        try {
            ctx = a;
            new Thread(() -> {
                refresh();
                try {
                    a.runOnUiThread(() -> {
                        try { applyFeature(a, afterUI); } catch(Exception e){}
                    });
                } catch(Exception e){}
            }).start();
        } catch(Exception e){}
    }

    // ---- the silent "feature update" (no APK, no version change) ----------
    public static void applyFeature(final Activity a, final Runnable afterUI){
        try {
            ctx = a;
            JSONObject f = j.optJSONObject("feature");
            if(f != null){
                int ts = f.optInt("ts", 0);
                if(ts > lastFeatTs(a)){
                    JSONObject fl = f.optJSONObject("flags");
                    JSONObject st = f.optJSONObject("strings");
                    sp(a).edit()
                        .putInt("feat_ts", ts)
                        .putString("feat_title", f.optString("title", ""))
                        .putString("feat_message", f.optString("message", ""))
                        .putString("feat_banner", f.optString("banner", ""))
                        .putString("feat_flags", fl == null ? "{}" : fl.toString())
                        .putString("feat_strings", st == null ? "{}" : st.toString())
                        .apply();
                    String title = f.optString("title", "");
                    String msg = f.optString("message", "");
                    if(!msg.trim().isEmpty()){
                        try {
                            AlertDialog.Builder b = new AlertDialog.Builder(a);
                            b.setTitle(title.trim().isEmpty() ? a.getString(R.string.feature_whats_new) : title);
                            b.setMessage(msg);
                            b.setPositiveButton(a.getString(R.string.feature_ok), (d, w) -> {});
                            b.show();
                        } catch(Exception e2){}
                    }
                }
            }
            featureBanner(a);
        } catch(Exception e){}
        if(afterUI != null){ try { a.runOnUiThread(afterUI); } catch(Exception e){} }
    }

    private static int lastFeatTs(Context c){ return sp(c).getInt("feat_ts", 0); }

    private static void featureBanner(Activity a){
        try {
            if(shownFeatBanner) return;
            String text = sp(a).getString("feat_banner", "");
            if(text == null || text.trim().isEmpty()) return;
            ViewGroup g = host(a);
            if(g == null) return;
            TextView tv = new TextView(a);
            tv.setText(text);
            tv.setTextSize(13);
            tv.setTextColor(Color.parseColor("#1B1730"));
            tv.setBackgroundColor(Color.parseColor("#EFEAFF"));
            tv.setPadding(36, 26, 36, 26);
            tv.setGravity(Gravity.CENTER_VERTICAL);
            tv.setOnClickListener(v -> { try { ((ViewGroup) tv.getParent()).removeView(tv); } catch(Exception e){} });
            g.addView(tv, 0);
            shownFeatBanner = true;
        } catch(Exception e){}
    }

    // Feature flags / string overrides pushed by the "Feature update" section.
    public static boolean flag(String key, boolean def){
        try {
            if(ctx == null) return def;
            JSONObject o = new JSONObject(sp(ctx).getString("feat_flags", "{}"));
            if(o.has(key)) return o.optBoolean(key, def);
        } catch(Exception e){}
        return def;
    }
    public static String str(String key, String def){
        try {
            if(ctx == null) return def;
            JSONObject o = new JSONObject(sp(ctx).getString("feat_strings", "{}"));
            String v = o.optString(key, "");
            if(v != null && !v.isEmpty()) return v;
        } catch(Exception e){}
        return def;
    }

    private static void updateCheck(final Activity a){
        try {
            JSONObject up = j.optJSONObject("update");
            if(up == null) return;
            final String latest = up.optString("latest");
            if(latest.isEmpty()) return;
            if(latest.equals("3.8")) return;
            final String url = up.optString("url");
            boolean force = up.optBoolean("force");
            AlertDialog.Builder b = new AlertDialog.Builder(a);
            b.setTitle("Update available");
            b.setMessage("Offex Mail " + latest + " aa gaya hai. Naye features ke liye update karo.");
            b.setCancelable(!force);
            b.setPositiveButton("Update now", (d, w) -> { try { Updater.start(a, url); } catch(Exception e){} });
            if(!force) b.setNegativeButton("Later", (d, w) -> {});
            b.show();
        } catch(Exception e){}
    }

    // Insert inside the ScrollView content so a banner is actually visible.
    private static ViewGroup host(Activity a){
        try {
            View root = a.findViewById(android.R.id.content);
            if(!(root instanceof ViewGroup)) return null;
            ViewGroup content = (ViewGroup) root;
            if(content.getChildCount() == 0) return null;
            View v = content.getChildAt(0);
            if(!(v instanceof ViewGroup)) return null;
            ViewGroup g = (ViewGroup) v;
            if(g instanceof ScrollView && g.getChildCount() > 0 && g.getChildAt(0) instanceof ViewGroup)
                return (ViewGroup) g.getChildAt(0);
            for(int i = 0; i < g.getChildCount(); i++){
                View c = g.getChildAt(i);
                if(c instanceof ScrollView && ((ViewGroup) c).getChildCount() > 0
                        && ((ViewGroup) c).getChildAt(0) instanceof ViewGroup)
                    return (ViewGroup)((ViewGroup) c).getChildAt(0);
            }
            return g;
        } catch(Exception e){ return null; }
    }

    private static void banner(Activity a){
        try {
            if(shownBanner) return;
            JSONObject an = j.optJSONObject("announcement");
            if(an == null || !an.optBoolean("on")) return;
            String text = an.optString("text");
            if(text.isEmpty()) return;
            ViewGroup g = host(a);
            if(g == null) return;
            TextView tv = new TextView(a);
            tv.setText(text);
            tv.setTextSize(13);
            tv.setTextColor(Color.parseColor("#C62828"));
            tv.setBackgroundColor(Color.parseColor("#FDECEA"));
            tv.setPadding(36, 30, 36, 30);
            g.addView(tv, 0);
            shownBanner = true;
        } catch(Exception e){}
    }
}
'''
W(J + "/Config.java", CFG)

# ===========================================================================
# 1 + 2 : MainActivity  -> mandatory notification gate + nav fix +
#         feature UI + interstitial on open
# ===========================================================================
mp = J + "/MainActivity.java"
s = R(mp)

# -- imports --
if "import android.app.AlertDialog;" not in s:
    s = s.replace("import android.app.Activity;", "import android.app.Activity;\nimport android.app.AlertDialog;")

# -- fields --
anchor = "    private boolean createLoading=false;"
must(s, anchor, "MainActivity.createLoading field")
s = s.replace(anchor, anchor + "\n    private AlertDialog notifDialog;\n    private boolean notifGateShown=false;")

# -- onCreate: enforce notification gate + apply feature --
a = "        Config.apply(this);\n        askNotify();"
must(s, a, "MainActivity.onCreate apply/askNotify")
s = s.replace(a, "        Config.apply(this);\n        enforceNotify();\n        Config.applyFeature(this, this::applyFeatureUI);")

# -- onCreate: App Open ad on cold start --
a2 = "        wireNav();\n        if(!Prefs.address().isEmpty()){"
must(s, a2, "MainActivity.onCreate wireNav")
s = s.replace(a2, "        wireNav();\n        ui.postDelayed(()->{ try { Ads.showAppOpen(this); } catch(Exception e){} },1500);\n        if(!Prefs.address().isEmpty()){")

# -- replace askNotify with the mandatory gate --
OLD_ASK = r'''    private void askNotify(){
        try {
            if(Build.VERSION.SDK_INT>=33 && checkSelfPermission("android.permission.POST_NOTIFICATIONS")!=PackageManager.PERMISSION_GRANTED){
                requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"},77);
            }
        } catch(Exception e){}
    }'''
must(s, OLD_ASK, "MainActivity.askNotify")
NEW_GATE = r'''    private boolean notifGranted(){
        try {
            if(Build.VERSION.SDK_INT>=33)
                return checkSelfPermission("android.permission.POST_NOTIFICATIONS")==PackageManager.PERMISSION_GRANTED;
            return Notifier.enabled(this);
        } catch(Exception e){ return true; }
    }
    private void enforceNotify(){
        try { if(!notifGranted()) showNotifGate(); } catch(Exception e){}
    }
    private void showNotifGate(){
        try {
            if(notifDialog!=null && notifDialog.isShowing()) return;
            AlertDialog.Builder b=new AlertDialog.Builder(this);
            b.setTitle(R.string.notif_gate_title);
            b.setMessage(R.string.notif_gate_body);
            b.setCancelable(false);
            b.setPositiveButton(R.string.notif_gate_allow,(d,w)->{
                try {
                    if(Build.VERSION.SDK_INT>=33){
                        requestPermissions(new String[]{"android.permission.POST_NOTIFICATIONS"},77);
                    } else {
                        openNotifSettings();
                    }
                } catch(Exception e){}
            });
            b.setNegativeButton(R.string.notif_gate_settings,(d,w)->openNotifSettings());
            notifDialog=b.create();
            notifDialog.setCanceledOnTouchOutside(false);
            notifDialog.show();
        } catch(Exception e){}
    }
    private void openNotifSettings(){
        try {
            Intent i=new Intent(android.provider.Settings.ACTION_APP_NOTIFICATION_SETTINGS);
            i.putExtra(android.provider.Settings.EXTRA_APP_PACKAGE,getPackageName());
            startActivity(i);
        } catch(Exception e){
            try { startActivity(new Intent(android.provider.Settings.ACTION_SETTINGS)); } catch(Exception e2){}
        }
    }
    @Override public void onRequestPermissionsResult(int req,String[] perms,int[] res){
        super.onRequestPermissionsResult(req,perms,res);
        if(req==77){ if(!notifGranted()) ui.postDelayed(this::enforceNotify,350); }
    }
    @Override public void onBackPressed(){
        if(!notifGranted()){ enforceNotify(); return; }
        super.onBackPressed();
    }'''
s = s.replace(OLD_ASK, NEW_GATE)

# -- navAction fix: scroll to each section's OWN heading --
OLD_NAV = r'''    private void navAction(int idx){
        try {
            if(idx==0){ if(rootScroll!=null) rootScroll.smoothScrollTo(0,0); }
            else if(idx==1){ if(rootScroll!=null&&msgList!=null) rootScroll.smoothScrollTo(0,Math.max(0,msgList.getTop()-24)); }
            else if(idx==2){ if(rootScroll!=null&&historyBox!=null) rootScroll.smoothScrollTo(0,Math.max(0,historyBox.getTop()-24)); }
            else { Menu.open(this); }
        } catch(Exception e){}
    }'''
must(s, OLD_NAV, "MainActivity.navAction")
NEW_NAV = r'''    private void navAction(int idx){
        try {
            if(idx==0){
                if(rootScroll!=null) rootScroll.post(()->rootScroll.smoothScrollTo(0,0));
            } else if(idx==1){
                scrollToSection(R.id.secInbox);
            } else if(idx==2){
                scrollToSection(R.id.secSwitch);
            } else {
                Menu.open(this);
            }
        } catch(Exception e){}
    }
    private void scrollToSection(final int id){
        try {
            if(rootScroll==null) return;
            rootScroll.post(()->{
                try {
                    View target=findViewById(id);
                    if(target==null) return;
                    rootScroll.smoothScrollTo(0,Math.max(0,target.getTop()-12));
                } catch(Exception e){}
            });
        } catch(Exception e){}
    }'''
s = s.replace(OLD_NAV, NEW_NAV)

# -- renderHistory: honour the show_history feature flag --
OLD_RH = "    private void renderHistory(){\n        historyBox.removeAllViews();"
must(s, OLD_RH, "MainActivity.renderHistory")
s = s.replace(OLD_RH,
    "    private void renderHistory(){\n        historyBox.removeAllViews();\n"
    "        if(!Config.flag(\"show_history\",true)){ try { historyEmpty.setVisibility(View.GONE); } catch(Exception e){} return; }")

# -- openMail: show an interstitial, then open the reader --
OLD_OPEN = "    private void openMail(Mail m){\n        Intent i=new Intent(this,ReaderActivity.class); i.putExtra(\"id\",m.id); startActivity(i);\n    }"
must(s, OLD_OPEN, "MainActivity.openMail")
NEW_OPEN = r'''    private void openMail(final Mail m){
        try {
            Ads.interstitial(this,()->{
                try { Intent i=new Intent(this,ReaderActivity.class); i.putExtra("id",m.id); startActivity(i); } catch(Exception e){}
            });
        } catch(Exception e){
            try { Intent i=new Intent(this,ReaderActivity.class); i.putExtra("id",m.id); startActivity(i); } catch(Exception e2){}
        }
    }'''
s = s.replace(OLD_OPEN, NEW_OPEN)

# -- onResume: re-enforce the gate + re-apply the silent feature update --
OLD_RESUME = ("    @Override protected void onResume(){\n"
              "        super.onResume();\n"
              "        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }\n"
              "    }")
must(s, OLD_RESUME, "MainActivity.onResume")
NEW_RESUME = r'''    @Override protected void onResume(){
        super.onResume();
        enforceNotify();
        Config.refreshFeature(this,this::applyFeatureUI);
        applyFeatureUI();
        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }
    }
    // Apply the silent feature-update payload (flags + string overrides) live.
    private void applyFeatureUI(){
        try {
            boolean showFeat=Config.flag("show_features",true);
            int fv=showFeat?View.VISIBLE:View.GONE;
            View fb=findViewById(R.id.featuresBox); if(fb!=null) fb.setVisibility(fv);
            View ft=findViewById(R.id.secFeatures); if(ft!=null) ft.setVisibility(fv);
            View fs=findViewById(R.id.secFeaturesSub); if(fs!=null) fs.setVisibility(fv);
            if(emptyText!=null) emptyText.setText(Config.str("inbox_empty",getString(R.string.no_messages)));
        } catch(Exception e){}
    }'''
s = s.replace(OLD_RESUME, NEW_RESUME)

W(mp, s)
print("U: MainActivity patched (mandatory notification gate, nav fix, feature UI, interstitial)")

# ===========================================================================
# 4 : ReaderActivity  -> honour the show_otp_card feature flag
# ===========================================================================
rp = J + "/ReaderActivity.java"
s = R(rp)
OLD_OTP = "                    if(otp!=null&&!otp.isEmpty()&&otpCard!=null){"
must(s, OLD_OTP, "ReaderActivity otp card")
s = s.replace(OLD_OTP, "                    if(otp!=null&&!otp.isEmpty()&&otpCard!=null&&Config.flag(\"show_otp_card\",true)){")
W(rp, s)
print("U: ReaderActivity patched (OTP card feature flag)")

# ===========================================================================
# 3 : circular logo assets (splash drawable + launcher round icon)
# ===========================================================================
LOGO = None
for _cand in ("resources/assets/logo.jpg", "resources/assets/logo.jpeg", "resources/assets/logo.png"):
    if os.path.exists(_cand):
        LOGO = _cand
        break
if LOGO:
    try:
        from PIL import Image, ImageDraw
        src = Image.open(LOGO).convert("RGBA")
        side = min(src.size)
        src = src.crop(((src.width - side) // 2, (src.height - side) // 2,
                        (src.width + side) // 2, (src.height + side) // 2))
        ss = 4
        mask = Image.new("L", (side * ss, side * ss), 0)
        ImageDraw.Draw(mask).ellipse((0, 0, side * ss - 1, side * ss - 1), fill=255)
        mask = mask.resize((side, side), Image.LANCZOS)
        out = Image.new("RGBA", (side, side), (0, 0, 0, 0))
        out.paste(src, (0, 0), mask)
        os.makedirs(RES + "/drawable", exist_ok=True)
        out.save(RES + "/drawable/logo_round.png")
        for d, sz in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
            dd = RES + "/mipmap-" + d
            os.makedirs(dd, exist_ok=True)
            out.resize((sz, sz), Image.LANCZOS).save(dd + "/ic_launcher_round.png")
        print("U: circular logo -> drawable/logo_round.png + mipmap-*/ic_launcher_round.png")
    except Exception as e:
        print("U: WARN circular logo failed:", e)
else:
    print("U: WARN resources/assets/logo missing")

# ===========================================================================
# 3 : splash layout -> circular logo
# ===========================================================================
sp_xml = RES + "/layout/activity_splash.xml"
s = R(sp_xml)
must(s, 'android:src="@drawable/logo"', "splash logo src")
s = s.replace('android:src="@drawable/logo"', 'android:src="@drawable/logo_round"')
W(sp_xml, s)
print("U: splash logo -> circular")

# ===========================================================================
# 3 : manifest -> circular launcher icon (roundIcon) + keep everything else
# ===========================================================================
mf = "android/app/src/main/AndroidManifest.xml"
s = R(mf)
if 'android:roundIcon=' not in s:
    s = s.replace('        android:icon="@mipmap/ic_launcher"\n',
                  '        android:icon="@mipmap/ic_launcher"\n        android:roundIcon="@mipmap/ic_launcher_round"\n')
    W(mf, s)
    print("U: manifest -> roundIcon")
else:
    print("U: manifest already has roundIcon")

# ===========================================================================
# 2 : main layout -> section ids for the nav fix + native ad slot
# ===========================================================================
lp = RES + "/layout/activity_main.xml"
s = R(lp)
pairs = [
    ('android:layout_marginTop="26dp" android:text="@string/inbox_title"',
     'android:id="@+id/secInbox" android:layout_marginTop="26dp" android:text="@string/inbox_title"'),
    ('android:layout_marginTop="26dp" android:text="@string/switch_title"',
     'android:id="@+id/secSwitch" android:layout_marginTop="26dp" android:text="@string/switch_title"'),
    ('android:layout_marginTop="26dp" android:text="@string/features_title"',
     'android:id="@+id/secFeatures" android:layout_marginTop="26dp" android:text="@string/features_title"'),
    ('android:layout_marginTop="3dp"\n                android:text="@string/choose_email"',
     'android:id="@+id/secChoose" android:layout_marginTop="3dp"\n                android:text="@string/choose_email"'),
    ('android:layout_marginTop="3dp"\n                android:text="@string/features_sub"',
     'android:id="@+id/secFeaturesSub" android:layout_marginTop="3dp"\n                android:text="@string/features_sub"'),
]
for old, new in pairs:
    must(s, old, "layout id " + new.split('"')[1])
    s = s.replace(old, new, 1)

NATIVE_SLOT = ('            <!-- ============ NATIVE AD ============ -->\n'
               '            <LinearLayout android:id="@+id/nativeAdBox" android:layout_width="match_parent"\n'
               '                android:layout_height="wrap_content" android:layout_marginStart="16dp"\n'
               '                android:layout_marginEnd="16dp" android:layout_marginTop="16dp"\n'
               '                android:orientation="vertical" android:visibility="gone" />\n\n')
marker = "            <!-- ============ FEATURES ============ -->"
must(s, marker, "layout features marker")
s = s.replace(marker, NATIVE_SLOT + marker, 1)
W(lp, s)
print("U: activity_main.xml -> section ids + native ad slot")

# ===========================================================================
# strings
# ===========================================================================
sp = RES + "/values/strings.xml"
s = R(sp)
NEW_STR = [
    ("notif_gate_title", "Notifications are required"),
    ("notif_gate_body", "Offex Mail ka poora kaam notifications par chalta hai - naya mail ya OTP aate hi hum turant batate hain. Notification allow kiye bina app use nahi ho sakta. Tap Allow and choose \\u201cAllow\\u201d."),
    ("notif_gate_allow", "Allow notifications"),
    ("notif_gate_settings", "Open settings"),
    ("feature_whats_new", "What's new"),
    ("feature_ok", "Got it"),
]
block = ""
for k, v in NEW_STR:
    if ('name="%s"' % k) not in s:
        block += '    <string name="%s">%s</string>\n' % (k, v)
if block:
    s = s.replace("</resources>", block + "</resources>")
    W(sp, s)
    print("U: strings.xml -> notification gate + feature strings")

# ===========================================================================
# version 3.7 -> 3.8
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = re.sub(r"versionCode \d+", "versionCode 28", s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.8"', s)
W(bp, s)

cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("3.7")', 'latest.equals("3.8")')
W(cp, s)

sup = J + "/SupportActivity.java"
if os.path.exists(sup):
    s = R(sup)
    s = s.replace('public static final String VERSION = "3.7";', 'public static final String VERSION = "3.8";')
    W(sup, s)

alp = RES + "/layout/activity_about.xml"
if os.path.exists(alp):
    s = R(alp)
    s = s.replace("Version 3.7", "Version 3.8").replace("Version 3.6", "Version 3.8")
    W(alp, s)

print("U: applied v3.8 changes (mandatory notifications, nav fix, circular logo, silent feature update, all ad placements; version 3.7 -> 3.8)")
