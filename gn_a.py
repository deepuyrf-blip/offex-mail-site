import os
from PIL import Image
ROOT="android"; APP=ROOT+"/app"; RES=APP+"/src/main/res"
F={}
F["android/settings.gradle"]="""pluginManagement { repositories { google(); mavenCentral(); gradlePluginPortal() } }
dependencyResolutionManagement {
    repositoriesMode.set(RepositoriesMode.PREFER_SETTINGS)
    repositories { google(); mavenCentral() }
}
rootProject.name = "OffexMail"
include ':app'
"""
F["android/build.gradle"]="""plugins { id 'com.android.application' version '8.5.2' apply false }
"""
F["android/gradle.properties"]="""android.useAndroidX=true
android.nonTransitiveRClass=true
org.gradle.jvmargs=-Xmx2048m -Dfile.encoding=UTF-8
"""
F["android/app/build.gradle"]="""plugins { id 'com.android.application' }
android {
    namespace 'online.mytempmail.app'
    compileSdk 34
    defaultConfig {
        applicationId "online.mytempmail.app"
        minSdk 24
        targetSdk 34
        versionCode 2
        versionName "2.0"
    }
    buildTypes { release { minifyEnabled false; signingConfig signingConfigs.debug } }
    compileOptions { sourceCompatibility JavaVersion.VERSION_17; targetCompatibility JavaVersion.VERSION_17 }
}
dependencies {
    implementation 'androidx.appcompat:appcompat:1.7.0'
    implementation 'com.google.android.material:material:1.12.0'
    implementation 'androidx.recyclerview:recyclerview:1.3.2'
    implementation 'androidx.core:core:1.13.1'
}
"""
F["android/app/src/main/AndroidManifest.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<manifest xmlns:android="http://schemas.android.com/apk/res/android">
    <uses-permission android:name="android.permission.INTERNET" />
    <uses-permission android:name="android.permission.POST_NOTIFICATIONS" />
    <application
        android:name=".App"
        android:label="@string/app_name"
        android:icon="@mipmap/ic_launcher"
        android:allowBackup="true"
        android:usesCleartextTraffic="false"
        android:theme="@style/Theme.Offex">
        <activity android:name=".OnboardingActivity" android:exported="false" />
        <activity android:name=".MainActivity" android:exported="true" android:launchMode="singleTop" android:windowSoftInputMode="adjustResize">
            <intent-filter>
                <action android:name="android.intent.action.MAIN" />
                <category android:name="android.intent.category.LAUNCHER" />
            </intent-filter>
        </activity>
        <activity android:name=".ReaderActivity" android:exported="false" />
        <activity android:name=".AdminActivity" android:exported="false" />
    </application>
</manifest>
"""
F["android/app/src/main/res/values/colors.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <color name="offex_purple">#6D4DFF</color>
    <color name="offex_purple_dark">#4B2FD6</color>
    <color name="offex_bg">#F5F6FB</color>
    <color name="offex_card">#FFFFFF</color>
    <color name="offex_text">#14162B</color>
    <color name="offex_text_dim">#6B7086</color>
    <color name="offex_green">#1DBF73</color>
    <color name="offex_red">#E5484D</color>
    <color name="offex_white">#FFFFFF</color>
</resources>
"""
F["android/app/src/main/res/values/strings.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources>
    <string name="app_name">Offex Mail</string>
    <string name="ob1_title">Instant disposable inbox</string>
    <string name="ob1_body">Ek tap me private temporary email pao \u2014 OTP, verification link aur test mail ke liye.</string>
    <string name="ob2_title">New mail pe notification</string>
    <string name="ob2_body">Inbox active hone par app background me check karta rehta hai \u2014 naya mail aate hi notification.</string>
    <string name="ob3_title">Free \u2022 No signup</string>
    <string name="ob3_body">Koi account nahi, koi password nahi. Inbox kuch der me khud expire ho jaata hai.</string>
    <string name="ob_next">Next</string>
    <string name="ob_start">Get started</string>
    <string name="ob_skip">Skip</string>
    <string name="new_inbox">New inbox</string>
    <string name="hint_name">Name (optional)</string>
    <string name="create_inbox">Create inbox</string>
    <string name="creating">Creating\u2026</string>
    <string name="your_address">Your temporary address</string>
    <string name="copy">Copy</string>
    <string name="refresh">Refresh</string>
    <string name="delete">Delete</string>
    <string name="copied">Address copied</string>
    <string name="messages">Messages</string>
    <string name="no_messages">Koi mail nahi aaya abhi. Address kahin paste karo \u2014 mail yahan aayega.</string>
    <string name="notif_on">Notifications</string>
    <string name="notif_channel">New mail</string>
    <string name="admin">Admin panel</string>
    <string name="admin_hint">Admin code daalo</string>
    <string name="unlock">Unlock</string>
    <string name="wrong_code">Galat code</string>
    <string name="expires_in">Expires in</string>
    <string name="version">Version</string>
</resources>
"""
F["android/app/src/main/res/values/themes.xml"]="""<?xml version="1.0" encoding="utf-8"?>
<resources xmlns:tools="http://schemas.android.com/tools">
    <style name="Theme.Offex" parent="Theme.MaterialComponents.Light.NoActionBar">
        <item name="colorPrimary">@color/offex_purple</item>
        <item name="colorPrimaryVariant">@color/offex_purple_dark</item>
        <item name="colorOnPrimary">@color/offex_white</item>
        <item name="colorSecondary">@color/offex_purple</item>
        <item name="android:statusBarColor" tools:targetApi="l">@color/offex_purple</item>
        <item name="android:windowBackground">@color/offex_bg</item>
    </style>
</resources>
"""
for rel,c in F.items():
    p=os.path.join(rel); os.makedirs(os.path.dirname(p),exist_ok=True)
    open(p,"w",encoding="utf-8").write(c)
print("A:",len(F))
img=Image.open("public/icons/icon-512.png").convert("RGBA")
for d,s in (("mdpi",48),("hdpi",72),("xhdpi",96),("xxhdpi",144),("xxxhdpi",192)):
    dd=RES+"/mipmap-"+d; os.makedirs(dd,exist_ok=True)
    img.resize((s,s),Image.LANCZOS).save(dd+"/ic_launcher.png")
print("icons ok")
