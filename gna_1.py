# ============================================================================
#  gna_1.py  -  Offex Audio Android app, generator 1 of 6
# ============================================================================
#  Emits the project skeleton into android-audio/ (a SEPARATE tree from the
#  mail app's android/ directory, so the mail app build is untouched):
#    * gradle settings / root build / gradle.properties / app build.gradle
#    * AndroidManifest.xml
#    * res/values (colors, themes, strings-en, dimens)
#    * res/drawable + res/mipmap launcher icons
#    * res/layout/activity_main.xml (WebView host + native ad container)
#
#  Package: online.offexaudio.app      Version: 1.4 (versionCode 5)
#
#  v1.3: the app's OWN custom UI is HOSTED ON THE SITE (audio/app-ui.html ->
#  https://offexmail.online/app-ui) and loaded from there, so the page shares
#  the site's origin with its /hf proxy and /health. Same-origin fetch/XHR/
#  WebSocket calls mean no CORS problem, and no HF token is inside the app (the
#  Cloudflare Pages worker injects the token server-side).
# ============================================================================
import os
from PIL import Image

ROOT = "android-audio"
APP = ROOT + "/app"
RES = APP + "/src/main/res"
PKG = "online.offexaudio.app"

F = {}

F["android-audio/settings.gradle"] = """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "OffexAudio"
include ':app'
"""

F["android-audio/build.gradle"] = """plugins {
    id 'com.android.application' version '8.5.2' apply false
    id 'com.google.gms.google-services' version '4.4.2' apply false
}
"""

F["android-audio/gradle.properties"] = """android.useAndroidX=true
android.nonTransitiveRClass=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
"""

F["android-audio/app/build.gradle"] = """plugins {
    id 'com.android.application'
    id 'com.google.gms.google-services'
}
android {
    namespace 'online.offexaudio.app'
    compileSdk 34
    defaultConfig {
        applicationId "online.offexaudio.app"
        minSdk 24
        targetSdk 34
        versionCode 5
        versionName "1.4"
        vectorDrawables { useSupportLibrary true }
    }
    buildTypes { release { minifyEnabled false; signingConfig signingConfigs.debug } }
    compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:1.12.0'
    implementation 'androidx.core:core:1.13.1'
    implementation 'com.google.android.gms:play-services-ads:23.2.0'
    implementation 'com.google.firebase:firebase-messaging:24.0.0'
}
"""

F["android-audio/app/src/main/AndroidManifest.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.ACCESS_NETWORK_STATE" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <!-- Media read permissions (declared for completeness; the picker itself
         uses the Storage Access Framework, so no broad permission is needed). -->
    <uses-permission android:name="android.permission.READ_MEDIA_AUDIO" />
    <uses-permission android:name="android.permission.READ_MEDIA_VIDEO" />
    <uses-permission android:name="android.permission.READ_EXTERNAL_STORAGE"
        android:maxSdkVersion="32" />
    <!-- Only needed on API < 29 where DownloadManager writes the public
         Downloads folder directly. -->
    <uses-permission android:name="android.permission.WRITE_EXTERNAL_STORAGE"
        android:maxSdkVersion="28" />

    <application
        android:name=".App"
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:roundIcon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:supportsRtl="true"
        android:usesCleartextTraffic="false"
        android:networkSecurityConfig="@xml/network_security_config"
        android:theme="@style/Theme.OffexAudio">

        <meta-data
            android:name="com.google.android.gms.ads.APPLICATION_ID"
            android:value="ca-app-pub-3940256099942544~3347511713" />
        <meta-data
            android:name="com.google.firebase.messaging.default_notification_channel_id"
            android:value="offex_audio_jobs" />

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:launchMode="singleTop"
            android:configChanges="orientation|screenSize|keyboardHidden|uiMode|locale|layoutDirection"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>

        <service
            android:name=".FcmService"
            android:exported="false">
            <intent-filter>
                <action android:name="com.google.firebase.MESSAGING_EVENT" />
            </intent-filter>
        </service>
    </application>
</manifest>
"""

F["android-audio/app/src/main/res/xml/network_security_config.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<network-security-config>
    <base-config cleartextTrafficPermitted="false">
        <trust-anchors>
            <certificates src="system" />
        </trust-anchors>
    </base-config>
</network-security-config>
"""

F["android-audio/app/src/main/res/values/colors.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="oa_ink">#05060D</color>
    <color name="oa_bg2">#0A0C18</color>
    <color name="oa_brand1">#6366F1</color>
    <color name="oa_brand2">#22D3EE</color>
    <color name="oa_brand3">#D946EF</color>
    <color name="oa_ok">#34D399</color>
    <color name="oa_bad">#F87171</color>
    <color name="oa_text">#EEF1FB</color>
    <color name="oa_muted">#9AA3C0</color>
    <color name="oa_white">#FFFFFF</color>
</resources>
"""

F["android-audio/app/src/main/res/values/dimens.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <dimen name="oa_pad">16dp</dimen>
</resources>
"""

F["android-audio/app/src/main/res/values/themes.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.OffexAudio" parent="Theme.MaterialComponents.NoActionBar">
        <item name="colorPrimary">@color/oa_brand1</item>
        <item name="colorPrimaryVariant">@color/oa_brand1</item>
        <item name="colorOnPrimary">@color/oa_white</item>
        <item name="colorSecondary">@color/oa_brand2</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/oa_ink</item>
        <item name="android:navigationBarColor" tools:targetApi="l">@color/oa_ink</item>
        <item name="android:windowBackground">@color/oa_ink</item>
    </style>
</resources>
"""

F["android-audio/app/src/main/res/values/strings.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Offex Audio</string>
    <string name="tagline">Audio Studio \u2022 Remove Silence \u2022 Enhance \u2022 Isolate</string>
    <string name="live">Live</string>
    <string name="not_connected">Not connected</string>
    <string name="checking">Checking\u2026</string>
    <string name="processor">Processor</string>
    <string name="online">Online</string>

    <string name="tab_remove">Remove Silence</string>
    <string name="tab_enhance">Enhance Audio</string>
    <string name="tab_isolate">Voice / BGM</string>
    <string name="tab_history">History</string>
    <string name="tab_more">More</string>

    <string name="tool_remove_title">Remove Silence</string>
    <string name="tool_remove_sub">Trim the quiet gaps out of a recording</string>
    <string name="tool_enhance_title">Enhance Audio</string>
    <string name="tool_enhance_sub">Noise reduction, clean-up and normalisation</string>
    <string name="tool_isolate_title">Voice / BGM Isolation</string>
    <string name="tool_isolate_sub">Split a track into vocals and background music</string>

    <string name="drop_hint">Tap to choose an audio or video file</string>
    <string name="choose_file">Choose file</string>
    <string name="change_file">Change file</string>
    <string name="no_file">No file selected</string>

    <string name="keep_silence">Keep silence (seconds)</string>
    <string name="enhance_mode">Enhancement mode</string>
    <string name="mode_light">Light</string>
    <string name="mode_balanced">Balanced</string>
    <string name="mode_strong">Strong</string>
    <string name="separation_model">Separation quality</string>

    <string name="process">Process</string>
    <string name="processing">Processing\u2026</string>
    <string name="download">Save to Downloads</string>
    <string name="saving">Saving\u2026</string>
    <string name="saved_to_downloads">Saved to Downloads</string>
    <string name="result_ready">Result ready</string>
    <string name="vocals">Vocals</string>
    <string name="bgm">Background music</string>
    <string name="open_result">Open</string>

    <string name="history_title">History</string>
    <string name="history_empty">Nothing processed yet. Your finished jobs will appear here.</string>
    <string name="history_clear">Clear history</string>
    <string name="history_redownload">Download again</string>

    <string name="more_title">More</string>
    <string name="more_language">Language</string>
    <string name="more_notifications">Job notifications</string>
    <string name="more_notifications_on">On</string>
    <string name="more_notifications_off">Off</string>
    <string name="more_sound">Notification sound</string>
    <string name="more_about">About</string>
    <string name="more_version">Version</string>
    <string name="more_backend">Backend</string>
    <string name="more_backend_value">offexmail.online (Hugging Face Space proxy)</string>
    <string name="more_privacy">Privacy</string>

    <string name="notif_channel_jobs">Job notifications</string>
    <string name="notif_channel_jobs_desc">Alerts when an audio job finishes</string>
    <string name="notif_gate_title">Turn on notifications</string>
    <string name="notif_gate_body">Offex Audio can alert you the moment a job finishes, even in the background. Allow notifications to continue.</string>
    <string name="notif_gate_allow">Allow</string>
    <string name="notif_gate_later">Not now</string>
    <string name="job_done_title">Job finished</string>
    <string name="job_done_body">Your audio is ready to save.</string>

    <string name="permission_needed">Storage permission is needed to save the file.</string>
    <string name="download_started">Download started \u2014 saving to Downloads</string>
    <string name="download_failed">Could not start the download.</string>
    <string name="pick_error">Could not open the file picker.</string>
    <string name="close">Close</string>
    <string name="cancel">Cancel</string>
</resources>
"""

F["android-audio/app/src/main/res/drawable/bg_web.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/oa_ink" />
</shape>
"""

F["android-audio/app/src/main/res/layout/activity_main.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="@color/oa_ink">

    <WebView
        android:id="@+id/webUi"
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1"
        android:background="@color/oa_ink" />

    <!-- Native banner ad, docked below the web UI so it never overlaps the
         page's own bottom tab bar. Ads.loadBanner() adds the AdView here. -->
    <FrameLayout
        android:id="@+id/adBanner"
        android:layout_width="match_parent"
        android:layout_height="wrap_content"
        android:visibility="gone" />
</LinearLayout>
"""

for rel, c in F.items():
    os.makedirs(os.path.dirname(rel), exist_ok=True)
    with open(rel, "w", encoding="utf-8") as f:
        f.write(c)

print("GNA1: wrote %d files" % len(F))

# ---- launcher icons (circular logo, from the site's 512 icon if present) ----
SRC_ICON = None
for cand in ("public/icons/icon-512.png", "audio/favicon.svg", "public/icon-512.png"):
    if os.path.exists(cand) and cand.endswith(".png"):
        SRC_ICON = cand
        break
if SRC_ICON:
    img = Image.open(SRC_ICON).convert("RGBA")
else:
    # Draw a simple gradient-ish circular logo so the build never depends on
    # an external asset being present.
    img = Image.new("RGBA", (512, 512), (0, 0, 0, 0))
    px = img.load()
    for y in range(512):
        for x in range(512):
            dx, dy = x - 256, y - 256
            r = (dx * dx + dy * dy) ** 0.5
            if r <= 250:
                t = (x + y) / 1024.0
                rr = int(99 + (217 - 99) * t)
                gg = int(102 + (70 - 102) * t)
                bb = int(241 + (239 - 241) * t)
                px[x, y] = (rr, gg, bb, 255)
    # simple waveform bars in white
    for i, hgt in enumerate((70, 150, 230, 120, 190, 90)):
        cx = 120 + i * 55
        for x in range(cx - 14, cx + 14):
            for y in range(256 - hgt // 2, 256 + hgt // 2):
                px[x, y] = (255, 255, 255, 255)

for d, s in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
    dd = RES + "/mipmap-" + d
    os.makedirs(dd, exist_ok=True)
    img.resize((s, s), Image.LANCZOS).save(dd + "/ic_launcher.png")
print("GNA1: launcher icons written")
