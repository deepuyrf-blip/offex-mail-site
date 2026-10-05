import os

from PIL import Image

ROOT = "android"
APP = os.path.join(ROOT, "app")
JAVA = os.path.join(APP, "src/main/java/online/mytempmail/app")
RES = os.path.join(APP, "src/main/res")

for d in (JAVA, RES, os.path.join(ROOT, "gradle/wrapper")):
    os.makedirs(d, exist_ok=True)

FILES = {}

FILES["android/settings.gradle"] = """pluginManagement {
    repositories { google(); mavenCentral(); gradlePluginPortal() }
}
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "OffexMail"
include ':app'
"""

FILES["android/build.gradle"] = """plugins {
    id 'com.android.application' version '8.5.2' apply false
}
"""

FILES["android/gradle.properties"] = """android.useAndroidX=true
android.nonTransitiveRClass=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
"""

FILES["android/app/build.gradle"] = """plugins { id 'com.android.application' }

android {
    namespace 'online.mytempmail.app'
    compileSdk 34

    defaultConfig {
        applicationId "online.mytempmail.app"
        minSdk 24
        targetSdk 34
        versionCode 1
        versionName "1.0"
    }

    buildTypes {
        release {
            minifyEnabled false
            signingConfig signingConfigs.debug
        }
    }

    compileOptions {
        sourceCompatibility JavaVersion.VERSION_17
        targetCompatibility JavaVersion.VERSION_17
    }
}

dependencies { }
"""

FILES["android/app/src/main/AndroidManifest.xml"] = """<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">

    <uses-permission android:name="android.permission.INTERNET" />

    <application
        android:label="Offex Mail"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:usesCleartextTraffic="false"
        android:hardwareAccelerated="true"
        android:theme="@android:style/Theme.DeviceDefault.NoActionBar">

        <activity
            android:name=".MainActivity"
            android:exported="true"
            android:configChanges="orientation|screenSize|keyboardHidden|screenLayout"
            android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
    </application>
</manifest>
"""

FILES["android/app/src/main/java/online/mytempmail/app/MainActivity.java"] = """package online.mytempmail.app;

import android.annotation.SuppressLint;
import android.app.Activity;
import android.content.Intent;
import android.net.Uri;
import android.os.Bundle;
import android.view.KeyEvent;
import android.webkit.CookieManager;
import android.webkit.WebChromeClient;
import android.webkit.WebResourceRequest;
import android.webkit.WebSettings;
import android.webkit.WebView;
import android.webkit.WebViewClient;

public class MainActivity extends Activity {

    private static final String HOME = "https://mytemp-mail.online/";
    private WebView web;

    @SuppressLint("SetJavaScriptEnabled")
    @Override
    protected void onCreate(Bundle b) {
        super.onCreate(b);

        web = new WebView(this);
        setContentView(web);

        WebSettings s = web.getSettings();
        s.setJavaScriptEnabled(true);
        s.setDomStorageEnabled(true);
        s.setDatabaseEnabled(true);
        s.setLoadWithOverviewMode(true);
        s.setUseWideViewPort(true);
        s.setMediaPlaybackRequiresUserGesture(false);
        s.setMixedContentMode(WebSettings.MIXED_CONTENT_NEVER_ALLOW);

        CookieManager cm = CookieManager.getInstance();
        cm.setAcceptCookie(true);
        cm.setAcceptThirdPartyCookies(web, true);

        web.setWebViewClient(new WebViewClient() {
            @Override
            public boolean shouldOverrideUrlLoading(WebView v, WebResourceRequest req) {
                Uri u = req.getUrl();
                String host = u.getHost();
                if (host != null && (host.endsWith("mytemp-mail.online") || host.endsWith("offexmail.online"))) {
                    return false;
                }
                try {
                    startActivity(new Intent(Intent.ACTION_VIEW, u));
                } catch (Exception ignored) { }
                return true;
            }
        });

        web.setWebChromeClient(new WebChromeClient());
        web.loadUrl(HOME);
    }

    @Override
    public boolean onKeyDown(int keyCode, KeyEvent event) {
        if (keyCode == KeyEvent.KEYCODE_BACK && web != null && web.canGoBack()) {
            web.goBack();
            return true;
        }
        return super.onKeyDown(keyCode, event);
    }
}
"""

for rel, content in FILES.items():
    p = os.path.join(os.path.dirname(ROOT) or ".", rel)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(content)
print("project files written:", len(FILES))

src = "public/icons/icon-512.png"
img = Image.open(src).convert("RGBA")
for dens, size in (("mdpi", 48), ("hdpi", 72), ("xhdpi", 96), ("xxhdpi", 144), ("xxxhdpi", 192)):
    d = os.path.join(RES, "mipmap-" + dens)
    os.makedirs(d, exist_ok=True)
    img.resize((size, size), Image.LANCZOS).save(os.path.join(d, "ic_launcher.png"))
print("launcher icons written")
