# ============================================================================
#  gn_aa.py  -  v4.4  (NEW LAST WRITER, runs after gn_z)
# ============================================================================
#  Cuts backend request volume hard so the Cloudflare Workers free-plan daily
#  limit is no longer exceeded. Nothing functional is removed.
#
#   (1) Inbox polling interval 20s -> 60s, in BOTH pollers
#       (MainActivity's foreground loop and MailService's fallback loop).
#   (2) MainActivity stops polling entirely while the app is NOT in the
#       foreground: onPause()/onStop() cancel the Handler/postDelayed
#       callbacks, onResume() restarts them.
#   (3) The background MailService only polls while the app is in the
#       foreground (it keeps its ongoing notification); a backgrounded app
#       therefore makes zero inbox requests. New mail still arrives instantly
#       via FCM push, which is the primary channel.
#   (4) Version bump 4.3 -> 4.4 (self-version + about strings).
#
#  Everything else is unchanged: the same API endpoints and JSON field names,
#  the mail ingest path, FCM pushes, the support feature, the bundled
#  notification sounds, the bottom nav, the ad placements (REAL AdMob ids in
#  the backend panel config), the notification-permission gate, the
#  multi-language support, the install analytics, the OTP precision fix, the
#  tappable links, the premium UI and the remote appearance config.
# ============================================================================
import os, re

ROOT = "android"; APP = ROOT + "/app"
RES = APP + "/src/main/res"
J = APP + "/src/main/java/online/mytempmail/app"


def R(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def W(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def REP(path, old, new, tag):
    s = R(path)
    if s.count(old) != 1:
        raise SystemExit("gn_aa: anchor %s not unique (%d) in %s" % (tag, s.count(old), path))
    W(path, s.replace(old, new, 1))
    print("AA: patched %s (%s)" % (path, tag))


# ---------------------------------------------------------------------------
# 1 : MainActivity - poll every 60s, and pause entirely when backgrounded.
# ---------------------------------------------------------------------------
MAIN = J + "/MainActivity.java"

REP(
    MAIN,
    "    private void startPolling(){\n"
    "        if(pollTask!=null) return;\n"
    "        pollTask=new Runnable(){ @Override public void run(){ loadMessages(); tick(); poll.postDelayed(this,20000); } };\n"
    "        poll.postDelayed(pollTask,10000);\n"
    "    }",
    "    private void startPolling(){\n"
    "        if(pollTask!=null) return;\n"
    "        pollTask=new Runnable(){ @Override public void run(){ loadMessages(); tick(); poll.postDelayed(this,60000); } };\n"
    "        poll.postDelayed(pollTask,60000);\n"
    "    }\n"
    "    private void stopPolling(){\n"
    "        if(pollTask!=null){ try { poll.removeCallbacks(pollTask); } catch(Exception e){} pollTask=null; }\n"
    "    }",
    "poll 60s + stopPolling",
)

REP(
    MAIN,
    "    @Override protected void onResume(){\n"
    "        super.onResume();\n"
    "        enforceNotify();\n"
    "        Config.refreshFeature(this,this::applyFeatureUI);\n"
    "        applyFeatureUI();\n"
    "        Ui.apply(this);\n"
    "        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }\n"
    "    }",
    "    @Override protected void onResume(){\n"
    "        super.onResume();\n"
    "        MailService.appForeground=true;\n"
    "        enforceNotify();\n"
    "        Config.refreshFeature(this,this::applyFeatureUI);\n"
    "        applyFeatureUI();\n"
    "        Ui.apply(this);\n"
    "        if(activeCard!=null&&activeCard.getVisibility()==View.VISIBLE){ loadMessages(); startPolling(); startService(); }\n"
    "    }\n"
    "    @Override protected void onPause(){\n"
    "        super.onPause();\n"
    "        MailService.appForeground=false;\n"
    "        stopPolling();\n"
    "    }\n"
    "    @Override protected void onStop(){\n"
    "        super.onStop();\n"
    "        MailService.appForeground=false;\n"
    "        stopPolling();\n"
    "    }",
    "pause/resume polling",
)

# ---------------------------------------------------------------------------
# 2 : MailService - poll every 60s, and only while the app is in the
#     foreground (FCM push is the primary, always-on channel).
# ---------------------------------------------------------------------------
SVC = J + "/MailService.java"

REP(
    SVC,
    "    private static final long MAIL_MS = 20000L;",
    "    private static final long MAIL_MS = 60000L;\n"
    "    public static volatile boolean appForeground = false;",
    "MAIL_MS 60s + appForeground flag",
)

REP(
    SVC,
    "    private void tick(){\n"
    "        new Thread(()->{\n",
    "    private void tick(){\n"
    "        if(!appForeground) return;\n"
    "        new Thread(()->{\n",
    "skip poll when backgrounded",
)

# ---------------------------------------------------------------------------
# 3 : Version bump 4.3 -> 4.4 (self-version + about strings).
# ---------------------------------------------------------------------------
REP(
    J + "/Config.java",
    'if(latest.equals("4.3")) return;',
    'if(latest.equals("4.4")) return;',
    "self-version 4.4",
)

REP(
    J + "/SupportActivity.java",
    'public static final String VERSION = "4.3";',
    'public static final String VERSION = "4.4";',
    "support self-version 4.4",
)

# About-screen version string, in every bundled locale.
for loc in ["", "-hi", "-es", "-pt", "-ar", "-ru", "-in"]:
    p = RES + "/values" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    s = R(p)
    s2 = re.sub(r'(name="about_version">[^<]*?)4\.3(<)', r"\g<1>4.4\g<2>", s)
    if s2 == s:
        raise SystemExit("gn_aa: about_version 4.3 not found in %s" % p)
    W(p, s2)
    print("AA: patched %s (about_version 4.4)" % p)

# Cosmetic header comment only.
UI = J + "/Ui.java"
s = R(UI)
s2 = s.replace(" * v4.3 - the whole app look", " * v4.4 - the whole app look", 1)
if s2 != s:
    W(UI, s2)
    print("AA: patched %s (header comment)" % UI)

print("AA: done")
