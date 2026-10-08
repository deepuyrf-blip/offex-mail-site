# ============================================================================
#  gna_1.py  -  Offex Audio Android app, generator 1 of 6
# ============================================================================
#  Emits the project skeleton into android-audio/ (a SEPARATE tree from the
#  mail app's android/ directory, so the mail app build is untouched):
#    * gradle settings / root build / gradle.properties / app build.gradle
#    * AndroidManifest.xml
#    * res/values (colors, themes, strings-en, dimens)
#    * res/drawable + res/mipmap launcher icons + native tab-bar icons
#    * res/layout/activity_main.xml (real-site WebView + native tab bar +
#      native ad container + native result/history/more panels)
#
#  Package: online.offexaudio.app      Version: 1.1 (versionCode 2)
#
#  v1.1 change: the app no longer ships a fake local HTML shell. The WebView
#  now loads the REAL audio website (https://offexmail.online) so the tools
#  run through the genuine Gradio / Hugging Face flow (real upload progress,
#  real processing). The native shell (bottom tabs, notifications, Downloads,
#  history, ads, languages) is kept and drives the loaded site.
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
        versionCode 2
        versionName "1.1"
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

    <!-- One bottom-nav tab: icon over label, evenly weighted. -->
    <style name="OaTab">
        <item name="android:layout_width">0dp</item>
        <item name="android:layout_height">match_parent</item>
        <item name="android:layout_weight">1</item>
        <item name="android:orientation">vertical</item>
        <item name="android:gravity">center</item>
        <item name="android:clickable">true</item>
        <item name="android:focusable">true</item>
        <item name="android:background">?android:attr/selectableItemBackground</item>
    </style>
</resources>
"""

F["android-audio/app/src/main/res/values/strings.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Offex Audio</string>
    <string name="tagline">Audio Studio \\u2022 Remove Silence \\u2022 Enhance \\u2022 Isolate</string>
    <string name="live">Live</string>
    <string name="not_connected">Not connected</string>
    <string name="checking">Checking\\u2026</string>
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
    <string name="processing">Processing\\u2026</string>
    <string name="download">Save to Downloads</string>
    <string name="save_result">Save result</string>
    <string name="saving">Saving\\u2026</string>
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
    <string name="more_backend_value">offexmail.online (live site \\u2014 Hugging Face Space)</string>
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
    <string name="download_started">Download started \\u2014 saving to Downloads</string>
    <string name="download_failed">Could not start the download.</string>
    <string name="pick_error">Could not open the file picker.</string>
    <string name="close">Close</string>
    <string name="cancel">Cancel</string>
    <string name="back">Back</string>
</resources>
"""

F["android-audio/app/src/main/res/drawable/bg_web.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<shape xmlns:android="http://schemas.android.com/apk/res/android" android:shape="rectangle">
    <solid android:color="@color/oa_ink" />
</shape>
"""

# ---- native bottom-nav icons (simple, deterministic vector paths) ----------
F["android-audio/app/src/main/res/drawable/ic_oa_remove.xml"] = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF"
        android:pathData="M3,10h2v4H3z M7,7h2v10H7z M11,4h2v16h-2z M15,8h2v8h-2z M19,11h2v2h-2z" />
</vector>
"""

F["android-audio/app/src/main/res/drawable/ic_oa_enhance.xml"] = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF"
        android:pathData="M12,2 L14,10 L22,12 L14,14 L12,22 L10,14 L2,12 L10,10 Z" />
</vector>
"""

F["android-audio/app/src/main/res/drawable/ic_oa_isolate.xml"] = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF" android:pathData="M10,3h4v11h-4z" />
    <path android:strokeColor="#FFFFFF" android:strokeWidth="1.8" android:fillColor="#00000000"
        android:pathData="M7,11 a5,5 0 0 1 10,0" />
    <path android:strokeColor="#FFFFFF" android:strokeWidth="1.8" android:fillColor="#00000000"
        android:pathData="M12,16 v4 M9,20 h6" />
</vector>
"""

F["android-audio/app/src/main/res/drawable/ic_oa_history.xml"] = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:strokeColor="#FFFFFF" android:strokeWidth="1.8" android:fillColor="#00000000"
        android:pathData="M12,3 a9,9 0 1 0 0.01,0" />
    <path android:strokeColor="#FFFFFF" android:strokeWidth="1.8" android:fillColor="#00000000"
        android:pathData="M12,7 L12,12 L16,14" />
</vector>
"""

F["android-audio/app/src/main/res/drawable/ic_oa_more.xml"] = """<vector xmlns:android="http://schemas.android.com/apk/res/android"
    android:width="24dp" android:height="24dp"
    android:viewportWidth="24" android:viewportHeight="24">
    <path android:fillColor="#FFFFFF"
        android:pathData="M6,12 a1.7,1.7 0 1 0 0.01,0 Z M12,12 a1.7,1.7 0 1 0 0.01,0 Z M18,12 a1.7,1.7 0 1 0 0.01,0 Z" />
</vector>
"""

F["android-audio/app/src/main/res/layout/activity_main.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<LinearLayout xmlns:android="http://schemas.android.com/apk/res/android"
    android:layout_width="match_parent"
    android:layout_height="match_parent"
    android:orientation="vertical"
    android:background="@color/oa_ink">

    <!-- WebView host: loads the REAL audio site, plus the native result button
         and the native History / More overlay panels. -->
    <FrameLayout
        android:layout_width="match_parent"
        android:layout_height="0dp"
        android:layout_weight="1">

        <WebView
            android:id="@+id/webUi"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:background="@color/oa_ink" />

        <!-- Native "Save result" affordance, shown once the site has a result. -->
        <TextView
            android:id="@+id/saveResult"
            android:layout_width="wrap_content"
            android:layout_height="wrap_content"
            android:layout_gravity="bottom|end"
            android:layout_margin="14dp"
            android:background="@color/oa_ok"
            android:paddingLeft="16dp"
            android:paddingRight="16dp"
            android:paddingTop="10dp"
            android:paddingBottom="10dp"
            android:textColor="@color/oa_ink"
            android:textStyle="bold"
            android:textSize="13sp"
            android:text="@string/save_result"
            android:visibility="gone" />

        <!-- Native overlay for the History and More tabs. -->
        <FrameLayout
            android:id="@+id/panelHost"
            android:layout_width="match_parent"
            android:layout_height="match_parent"
            android:background="#F205060D"
            android:visibility="gone">

            <ScrollView
                android:layout_width="match_parent"
                android:layout_height="match_parent"
                android:fillViewport="true">

                <LinearLayout
                    android:id="@+id/panelContent"
                    android:layout_width="match_parent"
                    android:layout_height="wrap_content"
                    android:orientation="vertical"
                    android:padding="18dp" />
            </ScrollView>
        </FrameLayout>
    </FrameLayout>

    <!-- Native bottom tab bar. Tabs drive the loaded site via JS navigation
         (Remove Silence / Enhance / Voice-BGM) or open the native panels. -->
    <LinearLayout
        android:id="@+id/tabBar"
        android:layout_width="match_parent"
        android:layout_height="62dp"
        android:orientation="horizontal"
        android:background="@color/oa_bg2"
        android:baselineAligned="false">

        <LinearLayout android:id="@+id/tabRemove" style="@style/OaTab">
            <ImageView android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_oa_remove" android:tint="@color/oa_muted"
                android:contentDescription="@string/tab_remove" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tab_remove" android:textSize="9sp" android:textColor="@color/oa_muted"
                android:gravity="center" android:maxLines="2" />
        </LinearLayout>

        <LinearLayout android:id="@+id/tabEnhance" style="@style/OaTab">
            <ImageView android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_oa_enhance" android:tint="@color/oa_muted"
                android:contentDescription="@string/tab_enhance" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tab_enhance" android:textSize="9sp" android:textColor="@color/oa_muted"
                android:gravity="center" android:maxLines="2" />
        </LinearLayout>

        <LinearLayout android:id="@+id/tabIsolate" style="@style/OaTab">
            <ImageView android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_oa_isolate" android:tint="@color/oa_muted"
                android:contentDescription="@string/tab_isolate" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tab_isolate" android:textSize="9sp" android:textColor="@color/oa_muted"
                android:gravity="center" android:maxLines="2" />
        </LinearLayout>

        <LinearLayout android:id="@+id/tabHistory" style="@style/OaTab">
            <ImageView android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_oa_history" android:tint="@color/oa_muted"
                android:contentDescription="@string/tab_history" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tab_history" android:textSize="9sp" android:textColor="@color/oa_muted"
                android:gravity="center" android:maxLines="2" />
        </LinearLayout>

        <LinearLayout android:id="@+id/tabMore" style="@style/OaTab">
            <ImageView android:layout_width="22dp" android:layout_height="22dp"
                android:src="@drawable/ic_oa_more" android:tint="@color/oa_muted"
                android:contentDescription="@string/tab_more" />
            <TextView android:layout_width="wrap_content" android:layout_height="wrap_content"
                android:text="@string/tab_more" android:textSize="9sp" android:textColor="@color/oa_muted"
                android:gravity="center" android:maxLines="2" />
        </LinearLayout>
    </LinearLayout>

    <!-- Native banner ad, docked below the tab bar so it never overlaps the
         site's own content. Ads.loadBanner() adds the AdView here. -->
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
