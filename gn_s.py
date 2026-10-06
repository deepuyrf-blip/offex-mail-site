import os, re, shutil

# ---------------------------------------------------------------------------
# gn_s.py  (runs LAST, after gn_r, in the android.yml pipeline)
#
# Adds instant Firebase Cloud Messaging (FCM) push notifications:
#   1. Places google-services.json into the app module (android/app).
#   2. Adds the Google Services Gradle plugin + firebase-messaging SDK.
#   3. Adds FcmService (FirebaseMessagingService) that posts a notification
#      through the app's EXISTING Notifier path (custom user-selected sound).
#   4. Adds DeviceReg: fetches the FCM token (on start + on refresh) and
#      registers it with the backend via POST /api/device.
#   5. Declares the FCM service + default channel in the manifest.
#   6. Bumps the app version 3.5 -> 3.6.
#
# Everything emitted by gn_a..gn_r is preserved: API endpoints/JSON fields,
# admin-controlled banner/AdMob/rewarded/update prompt, bottom nav, light
# theme default, features section, and the Create-button loading animation.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"
APP = "android/app"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def R(p):
    return open(p, encoding="utf-8").read()

# ===========================================================================
# 1 : google-services.json -> app module root (android/app/)
# ===========================================================================
_src = None
for _cand in ("google-services.json", "android/google-services.json", "resources/google-services.json"):
    if os.path.exists(_cand):
        _src = _cand
        break
if _src:
    os.makedirs(APP, exist_ok=True)
    shutil.copyfile(_src, APP + "/google-services.json")
    print("S: google-services.json -> android/app/google-services.json (from %s)" % _src)
else:
    print("S: WARN google-services.json not found in repo")

# ===========================================================================
# 2 : Gradle  -> google-services plugin + firebase-messaging
# ===========================================================================
rb = "android/build.gradle"
s = R(rb)
if "com.google.gms.google-services" not in s:
    s = s.replace(
        "plugins { id 'com.android.application' version '8.5.2' apply false }",
        "plugins {\n"
        "    id 'com.android.application' version '8.5.2' apply false\n"
        "    id 'com.google.gms.google-services' version '4.4.2' apply false\n"
        "}\n",
    )
    W(rb, s)
    print("S: root build.gradle -> google-services plugin")
else:
    print("S: root build.gradle already has google-services")

ab = "android/app/build.gradle"
s = R(ab)
if "com.google.gms.google-services" not in s:
    s = s.replace("plugins { id 'com.android.application' }",
                  "plugins {\n"
                  "    id 'com.android.application'\n"
                  "    id 'com.google.gms.google-services'\n"
                  "}\n")
    print("S: app build.gradle -> google-services plugin applied")
if "firebase-messaging" not in s:
    s = s.replace("    implementation 'com.google.android.gms:play-services-ads:23.2.0'",
                  "    implementation 'com.google.android.gms:play-services-ads:23.2.0'\n"
                  "    implementation 'com.google.firebase:firebase-messaging:24.0.0'")
    if "firebase-messaging" not in s:
        # fallback: append before closing brace of dependencies block
        s = s.replace("dependencies {", "dependencies {\n    implementation 'com.google.firebase:firebase-messaging:24.0.0'")
    print("S: app build.gradle -> firebase-messaging dependency")
# version 3.5 -> 3.6
s = re.sub(r"versionCode \d+", "versionCode 26", s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.6"', s)
W(ab, s)

# ===========================================================================
# 3 : FcmService  -> reuse the existing Notifier path + custom sound
# ===========================================================================
FCM = r'''package online.mytempmail.app;
import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;
import java.util.Map;
public class FcmService extends FirebaseMessagingService {
    @Override public void onNewToken(String token){
        // Token rotated: register the fresh token with the backend.
        try { DeviceReg.send(this, token); } catch(Exception e){}
    }
    @Override public void onMessageReceived(RemoteMessage msg){
        try {
            String sender = null, subject = null, otp = null;
            Map<String,String> d = msg.getData();
            if(d != null){
                sender  = d.get("sender");
                subject = d.get("subject");
                otp     = d.get("otp");
            }
            RemoteMessage.Notification n = msg.getNotification();
            String title = (sender != null && !sender.trim().isEmpty())
                    ? sender : (n != null ? n.getTitle() : null);
            String body = (subject != null && !subject.trim().isEmpty())
                    ? subject : (n != null ? n.getBody() : null);
            if(otp != null && !otp.trim().isEmpty() && !"null".equals(otp)){
                body = (body == null || body.trim().isEmpty())
                        ? ("OTP: " + otp) : (body + " | OTP: " + otp);
            }
            // Reuse the app's single notification system (Notifier) so the
            // user's selected custom sound + channel are honoured.
            Notifier.mail(this, title, body);
        } catch(Exception e){}
    }
}
'''
W(J + "/FcmService.java", FCM)

# ===========================================================================
# 4 : DeviceReg  -> fetch FCM token and POST it to the backend
# ===========================================================================
REG = r'''package online.mytempmail.app;
import android.content.Context;
import com.google.firebase.messaging.FirebaseMessaging;
import org.json.JSONObject;
public class DeviceReg {
    public static void register(Context c){
        try {
            FirebaseMessaging.getInstance().getToken().addOnCompleteListener(t -> {
                try {
                    if(t.isSuccessful() && t.getResult() != null){
                        send(c, t.getResult());
                    }
                } catch(Exception e){}
            });
        } catch(Exception e){}
    }
    public static void send(Context c, final String token){
        if(token == null || token.trim().isEmpty()) return;
        new Thread(()->{
            try {
                JSONObject body = new JSONObject();
                body.put("token", token);
                body.put("address", Prefs.address());
                body.put("platform", "android");
                ApiClient.post("/api/device", body.toString());
            } catch(Exception e){}
        }).start();
    }
}
'''
W(J + "/DeviceReg.java", REG)

# --- App.java: register token on app start --------------------------------
ap = J + "/App.java"
s = R(ap)
if "DeviceReg.register" not in s:
    s = s.replace("Prefs.init(this); }", "Prefs.init(this); DeviceReg.register(this); }")
    W(ap, s)
    print("S: App.onCreate -> DeviceReg.register")
else:
    print("S: App already registers device")

# --- MainActivity: re-register when the active address changes -------------
mp = J + "/MainActivity.java"
s = R(mp)
_changed = False
a1 = "Prefs.setAddress(addr); Prefs.setExpiresAt(exp); Prefs.setLastMsgId(-1);"
if a1 in s and "DeviceReg.register" not in s:
    s = s.replace(a1, a1 + " DeviceReg.register(this);")
    _changed = True
a2 = "if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }"
if a2 in s and "DeviceReg.register" not in s:
    s = s.replace(a2, "DeviceReg.register(this); " + a2)
    _changed = True
if _changed:
    W(mp, s)
    print("S: MainActivity -> DeviceReg.register on address change / resume")
else:
    print("S: MainActivity already registers device")

# ===========================================================================
# 5 : AndroidManifest  -> FCM service + default notification channel
# ===========================================================================
mf = "android/app/src/main/AndroidManifest.xml"
s = R(mf)
if "FcmService" not in s:
    block = (
        '        <service android:name=".FcmService" android:exported="false">\n'
        '            <intent-filter>\n'
        '                <action android:name="com.google.firebase.MESSAGING_EVENT" />\n'
        '            </intent-filter>\n'
        '        </service>\n'
        '        <meta-data\n'
        '            android:name="com.google.firebase.messaging.default_notification_channel_id"\n'
        '            android:value="offex_mail_s0" />\n'
        '        <meta-data\n'
        '            android:name="com.google.firebase.messaging.default_notification_icon"\n'
        '            android:resource="@mipmap/ic_launcher" />\n'
    )
    s = s.replace("    </application>", block + "    </application>")
    W(mf, s)
    print("S: manifest -> FcmService + default channel")
else:
    print("S: manifest already has FcmService")

# ===========================================================================
# 6 : version strings 3.5 -> 3.6
# ===========================================================================
cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("3.5")', 'latest.equals("3.6")')
W(cp, s)

alp = RES + "/layout/activity_about.xml"
if os.path.exists(alp):
    s = R(alp)
    s = s.replace("Version 3.5", "Version 3.6").replace("Version 3.4", "Version 3.6")
    W(alp, s)

print("S: applied v3.6 changes (FCM push: google-services + firebase-messaging, FcmService, device-token registration, manifest)")
