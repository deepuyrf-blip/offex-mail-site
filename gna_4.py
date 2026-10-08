# ============================================================================
#  gna_4.py  -  Offex Audio, generator 4 of 6  (FCM + tones + google-services)
# ============================================================================
#  * FcmService  : FirebaseMessagingService that reuses Notifier (so the user's
#                  chosen tone + channel are honoured).
#  * DeviceReg   : fetches the FCM token and registers it with the backend
#                  (best effort; never blocks the UI).
#  * res/raw     : three bundled notification tones (pure-stdlib WAV).
#  * google-services.json -> the app module. It carries the Offex Firebase
#    project (thug-5607f) plus a client entry for the new package name so the
#    google-services Gradle plugin resolves a matching client and the build
#    succeeds. NOTE: FCM delivery needs the package added in the Firebase
#    console (a user action) - see the report.
# ============================================================================
import os, math, struct, wave, json

J = "android-audio/app/src/main/java/online/offexaudio/app"
RAW = "android-audio/app/src/main/res/raw"
APP = "android-audio/app"

# ---------------------------------------------------------------- FCM service
FCM = r'''package online.offexaudio.app;

import com.google.firebase.messaging.FirebaseMessagingService;
import com.google.firebase.messaging.RemoteMessage;

import java.util.Map;

/** FCM push -> the app's single Notifier path (custom sound + channel). */
public class FcmService extends FirebaseMessagingService {

    @Override public void onNewToken(String token) {
        try { DeviceReg.send(this, token); } catch (Throwable t) { }
    }

    @Override public void onMessageReceived(RemoteMessage msg) {
        try {
            String title = null, body = null;
            Map<String, String> d = msg.getData();
            if (d != null) {
                title = d.get("title");
                body = d.get("body");
            }
            RemoteMessage.Notification n = msg.getNotification();
            if (title == null || title.trim().isEmpty()) title = (n != null ? n.getTitle() : null);
            if (body == null || body.trim().isEmpty()) body = (n != null ? n.getBody() : null);
            Notifier.job(this, title, body);
            MainActivity.onPush();
        } catch (Throwable t) { }
    }
}
'''

DEVICEREG = r'''package online.offexaudio.app;

import android.content.Context;

import com.google.firebase.messaging.FirebaseMessaging;

import org.json.JSONObject;

import java.io.OutputStream;
import java.net.HttpURLConnection;
import java.net.URL;

/** Registers the FCM token with the backend. Best effort; failures are silent. */
public class DeviceReg {

    public static void start(Context c) {
        try {
            FirebaseMessaging.getInstance().getToken()
                    .addOnCompleteListener(t -> { if (t.isSuccessful()) send(c, t.getResult()); });
        } catch (Throwable t) { }
    }

    static void send(final Context c, final String token) {
        if (token == null || token.isEmpty()) return;
        new Thread(() -> {
            HttpURLConnection conn = null;
            try {
                conn = (HttpURLConnection) new URL("https://api.mytemp-mail.online/api/device").openConnection();
                conn.setConnectTimeout(6000);
                conn.setReadTimeout(6000);
                conn.setRequestMethod("POST");
                conn.setDoOutput(true);
                conn.setRequestProperty("Content-Type", "application/json");
                JSONObject o = new JSONObject();
                o.put("token", token);
                o.put("package", c.getPackageName());
                o.put("platform", "android");
                try (OutputStream os = conn.getOutputStream()) { os.write(o.toString().getBytes("UTF-8")); }
                conn.getResponseCode();
            } catch (Throwable t) { }
            finally { if (conn != null) conn.disconnect(); }
        }).start();
    }
}
'''

for name, body in (("FcmService.java", FCM), ("DeviceReg.java", DEVICEREG)):
    p = os.path.join(J, name)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    with open(p, "w", encoding="utf-8") as f:
        f.write(body)
print("GNA4: wrote FcmService.java + DeviceReg.java")

# ------------------------------------------------------------- notification tones
SR = 22050


def _env(t, atk, tau, dec):
    a = (0.5 - 0.5 * math.cos(math.pi * t / atk)) if t < atk else 1.0
    return a * math.exp(-t / (tau * dec))


def _bell(f, dur, amp=1.0, tau=0.30, atk=0.006):
    n = int(dur * SR)
    parts = [(1.0, 1.0, 1.0), (2.0, 0.52, 0.75), (3.0, 0.26, 0.55), (4.2, 0.13, 0.40)]
    out = [0.0] * n
    for i in range(n):
        t = i / SR
        a = 0.0
        for h, ha, dec in parts:
            a += ha * math.sin(2.0 * math.pi * f * h * t) * _env(t, atk, tau, dec)
        out[i] = amp * a
    return out


def _mix(tracks, dur):
    n = int(dur * SR)
    out = [0.0] * n
    for start, sig in tracks:
        s0 = int(start * SR)
        for i in range(len(sig)):
            j = s0 + i
            if j >= n:
                break
            out[j] += sig[i]
    return out


def _finalize(out, fade=0.05):
    peak = max(1e-9, max(abs(x) for x in out))
    g = 0.92 / peak
    n = len(out)
    fn = max(1, int(fade * SR))
    for i in range(n):
        x = out[i] * g
        if i >= n - fn:
            x *= (n - i) / fn
        out[i] = x
    return out


def _write_wav(path, out):
    with wave.open(path, "w") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        frames = bytearray()
        for x in out:
            frames += struct.pack("<h", int(max(-1.0, min(1.0, x)) * 32767))
        w.writeframes(bytes(frames))


os.makedirs(RAW, exist_ok=True)
_write_wav(RAW + "/notify_1.wav", _finalize(_mix([
    (0.00, _bell(1046.50, 0.95, 1.00, 0.34)),
    (0.13, _bell(1567.98, 1.05, 0.72, 0.30)),
], 1.30)))
_write_wav(RAW + "/notify_2.wav", _finalize(_mix([
    (0.00, _bell(1318.51, 0.55, 0.85, 0.26)),
    (0.10, _bell(1567.98, 0.60, 0.85, 0.26)),
    (0.20, _bell(2093.00, 0.95, 0.90, 0.30)),
], 1.25)))
_write_wav(RAW + "/notify_3.wav", _finalize(_mix([
    (0.00, _bell(880.00, 1.10, 1.00, 0.36)),
    (0.05, _bell(1318.51, 0.85, 0.34, 0.28)),
], 1.25)))
for n in ("notify_1", "notify_2", "notify_3"):
    print("GNA4: res/raw/%s.wav (%d bytes)" % (n, os.path.getsize(RAW + "/" + n + ".wav")))

# ---------------------------------------------------------------- google-services
# Build a google-services.json that keeps the existing Offex Firebase project
# (thug-5607f) and adds a client entry for the new package, so the Gradle plugin
# resolves a matching client. Sourced from the repo copy when present.
src = None
for cand in ("audioapp/google-services.json", "google-services.json"):
    if os.path.exists(cand):
        src = cand
        break

base = None
if src:
    try:
        base = json.load(open(src, encoding="utf-8"))
    except Exception:
        base = None

if base is None:
    base = {
        "project_info": {
            "project_number": "550179658866",
            "project_id": "thug-5607f",
            "storage_bucket": "thug-5607f.firebasestorage.app",
        },
        "client": [],
        "configuration_version": "1",
    }

# Drop any existing client for our package, then add ours (cloned from the
# project's existing api_key so the file is structurally valid).
SYNTHETIC_ID = "1:550179658866:android:0ffeac0de0000000000000"

existing = None
for c in base.get("client", []):
    if c.get("client_info", {}).get("android_client_info", {}).get("package_name") == "online.offexaudio.app":
        existing = c
        break

existing_id = ""
if existing:
    existing_id = str(existing.get("client_info", {}).get("mobilesdk_app_id") or "").strip()

if existing and existing_id and existing_id != SYNTHETIC_ID:
    # A REAL Firebase Android app id for our package is present: the operator
    # added the app in the Firebase console and shipped the real
    # google-services.json. Keep every entry verbatim so FCM can actually
    # deliver pushes to online.offexaudio.app.
    print("GNA4: google-services.json already has a REAL entry for "
          "online.offexaudio.app (%s) - kept as-is" % existing_id)
else:
    # No real entry yet: synthesise a structurally valid one so the Gradle
    # plugin resolves a matching client and the build succeeds. NOTE: a
    # synthetic mobilesdk_app_id will NOT deliver FCM pushes. Add the app in
    # the Firebase console (project thug-5607f) and drop the real
    # google-services.json into the repo (audioapp/google-services.json or the
    # repo root) to replace this.
    clients = [c for c in base.get("client", [])
               if c.get("client_info", {}).get("android_client_info", {}).get("package_name") != "online.offexaudio.app"]
    tmpl = None
    for c in base.get("client", []):
        if c.get("client_info", {}).get("android_client_info", {}).get("package_name") == "online.mytempmail.app":
            tmpl = c
            break
    if tmpl is None and base.get("client"):
        tmpl = base["client"][0]
    key = "AIzaSyA7QwXJArY2yDfArTssuCTHm1X6pVh1SCU"
    if tmpl is not None:
        try:
            key = tmpl["api_key"][0]["current_key"]
        except Exception:
            pass

    newc = {
        "client_info": {
            "mobilesdk_app_id": SYNTHETIC_ID,
            "android_client_info": {"package_name": "online.offexaudio.app"},
        },
        "oauth_client": [],
        "api_key": [{"current_key": key}],
        "services": {"appinvite_service": {"other_platform_oauth_client": []}},
    }
    clients.append(newc)
    base["client"] = clients
    print("GNA4: WARNING - online.offexaudio.app uses a SYNTHETIC mobilesdk_app_id; "
          "FCM will NOT deliver until the real google-services.json is added "
          "(Firebase console, project thug-5607f)")

os.makedirs(APP, exist_ok=True)
with open(APP + "/google-services.json", "w", encoding="utf-8") as f:
    json.dump(base, f, indent=2)
print("GNA4: wrote android-audio/app/google-services.json (%d client entries)" % len(base.get("client", [])))
