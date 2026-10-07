# ============================================================================
#  gn_af.py  -  v4.9  (NEW LAST WRITER, runs after gn_ae)
# ============================================================================
#  Four user-requested changes, all additive / behaviour-only:
#
#   1. DELETE WITH NO CONFIRMATION.  Tapping Delete in the WebView UI called
#      OffexBridge.deleteInbox(), which popped a native AlertDialog
#      (confirmDelete()).  The bridge now calls deleteActive() directly, so an
#      inbox is deleted immediately.  The native Delete button already called
#      deleteActive() directly, and deleteSavedAddress() never confirmed, so the
#      whole delete path is now confirmation-free.
#
#   2. DEDICATED INBOX SCREEN.  Tapping the Inbox item in the bottom nav used to
#      scroll the single page.  The bundled HTML now carries a real, separate
#      Inbox view - a full-screen overlay section (#inboxScreen) that the nav
#      switches to and a back button leaves.  It lists the received mail (sender,
#      subject, service/OTP tags, time), tapping a row opens that message, and
#      the back arrow returns to the main screen.  The existing CSS/markup of the
#      original page are byte-for-byte unchanged; only additive <style> rules,
#      additive markup and additive wiring were added, and every JS->Java call
#      keeps the SAME argument count the bridge resolves on.
#
#   3. NOTIFICATION OPENS THE MAIL.  The new-mail notification's PendingIntent
#      carried no message id, so a tap always landed on the home screen.  It now
#      carries open_msg_id + open_address and the app opens the reader for that
#      exact message - from a cold start (onCreate) and from the background
#      (onNewIntent, launchMode=singleTop).  Notifier.mail() gained a
#      (msgId, address) overload; the polling paths (MainActivity.loadMessages,
#      MailService.tick) and FCM (FcmService) pass them.
#
#   4. SAMSUNG/VIVO-STYLE TONES.  The three bundled tones were replaced with
#      three new, higher-quality, pleasant two-tone message bells, synthesised
#      here as 16-bit PCM WAV (~1.25 s, soft raised-cosine attack, exponential
#      tail, gentle fade-out - not harsh).  The picker keeps working and the
#      default (index 0, "Bell") is the nicest one.
#
#  Untouched: API endpoints/JSON fields, FCM push, the support screen, the AdMob
#  placements, the notification-permission gate, the multi-language support
#  (English default + Hindi Devanagari + es/pt/ar/ru/in), install analytics, the
#  OTP precision fix, tappable verification links, the circular logo and the
#  remote appearance config.  Version bumped 4.8 -> 4.9.
# ============================================================================
import os, re, math, struct, wave

ROOT = "android"; APP = ROOT + "/app"
RES = APP + "/src/main/res"
J = APP + "/src/main/java/online/mytempmail/app"
ASSETS = APP + "/src/main/assets"
RAW = RES + "/raw"
HTML = ASSETS + "/offex_ui.html"


def R(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def W(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


def REP(path, old, new, tag, count=1):
    s = R(path)
    if s.count(old) != count:
        raise SystemExit("gn_af: anchor %s not unique (%d, expected %d) in %s"
                         % (tag, s.count(old), count, path))
    W(path, s.replace(old, new))
    print("AF: patched %s (%s)" % (os.path.basename(path), tag))


# ===========================================================================
# 4 : synthesise three new pleasant Samsung/Vivo-style message tones.
#     Pure stdlib (no numpy dependency in CI). 22.05 kHz mono 16-bit PCM.
# ===========================================================================
SR = 22050


def _env(t, atk, tau, dec):
    a = (0.5 - 0.5 * math.cos(math.pi * t / atk)) if t < atk else 1.0
    return a * math.exp(-t / (tau * dec))


def _bell(f, dur, amp=1.0, tau=0.30, atk=0.006):
    n = int(dur * SR)
    parts = [(1.0, 1.0, 1.0), (2.0, 0.52, 0.75), (3.0, 0.26, 0.55),
             (4.2, 0.13, 0.40), (5.4, 0.06, 0.30)]
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
            v = int(max(-1.0, min(1.0, x)) * 32767)
            frames += struct.pack("<h", v)
        w.writeframes(bytes(frames))


os.makedirs(RAW, exist_ok=True)
# 0 - Bell: pleasant two-tone "ding" (C6 -> G6). Default / nicest.
_write_wav(RAW + "/notify_1.wav", _finalize(_mix([
    (0.00, _bell(1046.50, 0.95, 1.00, 0.34)),
    (0.13, _bell(1567.98, 1.05, 0.72, 0.30)),
], 1.30)))
# 1 - Chime: bright three-note rising arpeggio (E6 - G6 - C7).
_write_wav(RAW + "/notify_2.wav", _finalize(_mix([
    (0.00, _bell(1318.51, 0.55, 0.85, 0.26)),
    (0.10, _bell(1567.98, 0.60, 0.85, 0.26)),
    (0.20, _bell(2093.00, 0.95, 0.90, 0.30)),
], 1.25)))
# 2 - Note: soft single bell with a light shimmer (A5 + E6).
_write_wav(RAW + "/notify_3.wav", _finalize(_mix([
    (0.00, _bell(880.00, 1.10, 1.00, 0.36)),
    (0.05, _bell(1318.51, 0.85, 0.34, 0.28)),
], 1.25)))
for n in ("notify_1", "notify_2", "notify_3"):
    print("AF: wrote res/raw/%s.wav (%d bytes)" % (n, os.path.getsize(RAW + "/" + n + ".wav")))


# ===========================================================================
# 2 : dedicated Inbox screen - additive CSS + markup + wiring in the bundled
#     HTML.  Every original rule and element is left exactly as it was.
# ===========================================================================
# (a) additive stylesheet, inserted before </head>
REP(HTML,
    "</style>\n</head>",
    "</style>\n"
    "<style>\n"
    "/* v4.9 - additive styles for the dedicated Inbox screen. The rules above are\n"
    "   untouched; these only describe the new overlay view. */\n"
    ".inbox-screen{position:fixed;left:0;right:0;top:0;bottom:0;z-index:15;display:none;"
    "flex-direction:column;padding:22px 16px 104px;overflow-y:auto;\n"
    " background:radial-gradient(330px 430px at 82% 15%,rgba(45,31,160,.85),transparent 67%),\n"
    " radial-gradient(300px 440px at 10% 86%,rgba(0,94,184,.75),transparent 67%),\n"
    " linear-gradient(145deg,#030820,#061544 58%,#06102f);}\n"
    ".inbox-screen.open{display:flex}\n"
    ".inbox-top{display:flex;align-items:center;gap:12px;margin-bottom:10px}\n"
    ".inbox-back{width:44px;height:44px;border-radius:15px;display:grid;place-items:center;flex:none;\n"
    " font-size:26px;line-height:1;color:#fff;background:#17326a99;border:1px solid #3a67ad;"
    "box-shadow:0 0 18px #155cff44;cursor:pointer}\n"
    ".inbox-heading{flex:1;min-width:0}\n"
    ".inbox-heading b{display:block;font-size:20px;font-weight:800;letter-spacing:-.4px}\n"
    ".inbox-heading small{display:block;color:#9caed4;font-size:11px;margin-top:2px;overflow:hidden;"
    "text-overflow:ellipsis;white-space:nowrap}\n"
    ".inbox-screen-list{margin-top:4px}\n"
    ".inbox-empty{color:#9caed4;font-size:11px;margin-top:8px;line-height:1.4}\n"
    "</style>\n</head>",
    "inbox css")

# (b) additive markup for the overlay, inserted just before the bottom nav
REP(HTML,
    "<nav class=\"bottom\">",
    "<div id=\"inboxScreen\" class=\"inbox-screen\" aria-hidden=\"true\">\n"
    " <div class=\"inbox-top\">\n"
    "  <div class=\"inbox-back\" id=\"inboxBackBtn\" role=\"button\" aria-label=\"Back\">\u2039</div>\n"
    "  <div class=\"inbox-heading\"><b id=\"inboxScreenTitle\" data-i18n=\"inbox_title\">Inbox</b>"
    "<small id=\"inboxScreenAddr\"></small></div>\n"
    " </div>\n"
    " <div id=\"inboxScreenList\" class=\"inbox-screen-list\"></div>\n"
    "</div>\n\n"
    "<nav class=\"bottom\">",
    "inbox markup")

# (c) additive behaviour: render + open/close the Inbox screen, expose it.
REP(HTML,
    "  window.OffexUI={ render:render };",
    "  // Dedicated Inbox screen: rendered from the same state push as the rest of\n"
    "  // the page, shown as a separate full-screen view by the Inbox nav item.\n"
    "  function renderInboxScreen(st){\n"
    "    var box=$('inboxScreenList'); if(!box) return;\n"
    "    var ms=(st&&st.messages)||[]; var t=S.strings||{};\n"
    "    var ad=$('inboxScreenAddr'); if(ad) ad.textContent=(st&&st.address)?st.address:'';\n"
    "    if(!ms.length){ box.innerHTML='<div class=\"inbox-empty\">'+esc(t.no_messages||'')+'</div>'; return; }\n"
    "    var html='';\n"
    "    for(var i=0;i<ms.length;i++){\n"
    "      var m=ms[i];\n"
    "      var initial=(m.sender&&m.sender.length)?m.sender.charAt(0).toUpperCase():'?';\n"
    "      var svc=(m.service&&m.service.length)?String(m.service).toUpperCase():(t.message_label||'MAIL');\n"
    "      html+='<div class=\"mail\" data-id=\"'+esc(m.id)+'\">'\n"
    "        +'<div class=\"avatar\">'+esc(initial)+'</div>'\n"
    "        +'<div class=\"mailtext\"><b>'+esc(m.sender)+'</b><div>'+esc(m.subject)+'</div>'\n"
    "        +'<small>'+esc(svc)+'</small>'\n"
    "        +(m.otp?'<small class=\"green\">'+esc(m.otp)+'</small>':'')\n"
    "        +'</div>'\n"
    "        +'<div class=\"time\">'+esc(m.time)+'</div>'\n"
    "        +'<div class=\"arrow\">\u203a</div></div>';\n"
    "    }\n"
    "    box.innerHTML=html;\n"
    "  }\n"
    "  function openInboxScreen(){\n"
    "    try { var e=$('inboxScreen'); if(e){ e.classList.add('open'); e.setAttribute('aria-hidden','false'); } } catch(err){}\n"
    "    setNav('navInbox'); renderInboxScreen(S);\n"
    "  }\n"
    "  function closeInboxScreen(){\n"
    "    try { var e=$('inboxScreen'); if(e){ e.classList.remove('open'); e.setAttribute('aria-hidden','true'); } } catch(err){}\n"
    "  }\n"
    "\n"
    "  window.OffexUI={ render:render, openInbox:openInboxScreen };",
    "inbox js")

# (d) keep the Inbox screen in sync on every state push
REP(HTML,
    "    renderBanner(S);\n    renderMessages(S);\n    renderSaved(S);\n  }",
    "    renderBanner(S);\n    renderMessages(S);\n    renderSaved(S);\n    renderInboxScreen(S);\n  }",
    "inbox render hook")

# (e) nav wiring: Inbox opens the dedicated screen; the other tabs leave it
REP(HTML,
    "    on('navEmail',function(){ setNav('navEmail'); call('nav','email'); });",
    "    on('navEmail',function(){ closeInboxScreen(); setNav('navEmail'); call('nav','email'); });",
    "navEmail")
REP(HTML,
    "    on('navInbox',function(){ setNav('navInbox'); call('nav','inbox'); });",
    "    on('navInbox',function(){ openInboxScreen(); call('nav','inbox'); });",
    "navInbox")
REP(HTML,
    "    on('navSwitch',function(){ setNav('navSwitch'); call('nav','switch'); });",
    "    on('navSwitch',function(){ closeInboxScreen(); setNav('navSwitch'); call('nav','switch'); });",
    "navSwitch")
REP(HTML,
    "    on('navMore',function(){ setNav('navMore'); call('openMore'); });",
    "    on('navMore',function(){ closeInboxScreen(); setNav('navMore'); call('openMore'); });",
    "navMore")

# (f) back button + delegated tap-to-open on the Inbox screen list
REP(HTML,
    "    var sl=$('savedList');\n"
    "    if(sl) sl.addEventListener('click',function(ev){\n"
    "      var t=ev.target;\n"
    "      var del=(t&&t.getAttribute)?t.getAttribute('data-del'):null;\n"
    "      if(del!=null){ if(ev.stopPropagation) ev.stopPropagation(); call('deleteSaved', del); return; }\n"
    "      var el=t;\n"
    "      while(el&&el!==sl&&!(el.getAttribute&&el.getAttribute('data-sw')!=null)) el=el.parentNode;\n"
    "      if(el&&el!==sl) call('switchTo', el.getAttribute('data-sw'));\n"
    "    });\n"
    "  }",
    "    var sl=$('savedList');\n"
    "    if(sl) sl.addEventListener('click',function(ev){\n"
    "      var t=ev.target;\n"
    "      var del=(t&&t.getAttribute)?t.getAttribute('data-del'):null;\n"
    "      if(del!=null){ if(ev.stopPropagation) ev.stopPropagation(); call('deleteSaved', del); return; }\n"
    "      var el=t;\n"
    "      while(el&&el!==sl&&!(el.getAttribute&&el.getAttribute('data-sw')!=null)) el=el.parentNode;\n"
    "      if(el&&el!==sl) call('switchTo', el.getAttribute('data-sw'));\n"
    "    });\n"
    "\n"
    "    // Dedicated Inbox screen: back button and tap-to-open on its list.\n"
    "    on('inboxBackBtn',function(){ closeInboxScreen(); setNav('navEmail'); });\n"
    "    var il=$('inboxScreenList');\n"
    "    if(il) il.addEventListener('click',function(ev){\n"
    "      var el=ev.target;\n"
    "      while(el&&el!==il&&!(el.getAttribute&&el.getAttribute('data-id')!=null)) el=el.parentNode;\n"
    "      if(el&&el!==il) call('openMessage', el.getAttribute('data-id'));\n"
    "    });\n"
    "  }",
    "inbox wiring")


# ===========================================================================
# 1 : delete with no confirmation.
# ===========================================================================
M = J + "/MainActivity.java"
REP(M,
    "        @JavascriptInterface public void deleteInbox(){ runOnUiThread(()->{ try { confirmDelete(); } catch(Exception e){} }); }",
    "        @JavascriptInterface public void deleteInbox(){ runOnUiThread(()->{ try { deleteActive(); } catch(Exception e){} }); }",
    "delete without confirm")


# ===========================================================================
# 3 : notification tap opens the specific mail (cold start + background).
# ===========================================================================
# (a) remember the pending open target
REP(M,
    "    private volatile String stateJson=\"{}\";",
    "    private volatile String stateJson=\"{}\";\n"
    "    private int pendingOpenId = 0;\n"
    "    private String pendingOpenAddr = \"\";",
    "pending fields")

# (b) handle the launch intent
REP(M,
    "        setupWebUi();\n    }",
    "        setupWebUi();\n        handleNotifyIntent(getIntent());\n    }",
    "onCreate notify intent")

# (c) onNewIntent + resolver + opener
REP(M,
    "    private boolean notifGranted(){",
    "    @Override protected void onNewIntent(Intent intent){\n"
    "        super.onNewIntent(intent);\n"
    "        setIntent(intent);\n"
    "        handleNotifyIntent(intent);\n"
    "    }\n"
    "\n"
    "    // A tap on a new-mail notification carries the message id (and address),\n"
    "    // so the app jumps straight to that mail - from a cold start (onCreate) or\n"
    "    // from the background (onNewIntent, launchMode=singleTop).\n"
    "    private void handleNotifyIntent(Intent i){\n"
    "        try {\n"
    "            if(i == null) return;\n"
    "            final int id = i.getIntExtra(\"open_msg_id\", 0);\n"
    "            if(id <= 0) return;\n"
    "            final String addr = i.getStringExtra(\"open_address\");\n"
    "            pendingOpenId = id;\n"
    "            pendingOpenAddr = (addr == null) ? \"\" : addr;\n"
    "            if(!pendingOpenAddr.isEmpty() && !pendingOpenAddr.equals(Prefs.address())){\n"
    "                long exp = 0;\n"
    "                try {\n"
    "                    JSONArray a = new JSONArray(Prefs.history());\n"
    "                    for(int k=0;k<a.length();k++){\n"
    "                        JSONObject o = a.getJSONObject(k);\n"
    "                        if(pendingOpenAddr.equals(o.optString(\"a\"))){ exp = o.optLong(\"e\",0L); break; }\n"
    "                    }\n"
    "                } catch(Exception e){}\n"
    "                Prefs.setAddress(pendingOpenAddr); Prefs.setExpiresAt(exp); Prefs.setLastMsgId(-1);\n"
    "                if(activeCard != null){ activeCard.setVisibility(View.VISIBLE); addrText.setText(pendingOpenAddr); }\n"
    "                mails.clear(); if(adapter != null) adapter.notifyDataSetChanged();\n"
    "                renderHistory(); loadMessages(); startPolling(); startService();\n"
    "            } else if(!Prefs.address().isEmpty()){\n"
    "                loadMessages();\n"
    "            }\n"
    "            openPendingMail();\n"
    "        } catch(Exception e){}\n"
    "    }\n"
    "\n"
    "    private void openPendingMail(){\n"
    "        try {\n"
    "            if(pendingOpenId <= 0) return;\n"
    "            Mail found = null;\n"
    "            for(int k=0;k<mails.size();k++){ if(mails.get(k).id == pendingOpenId){ found = mails.get(k); break; } }\n"
    "            if(found == null) return;\n"
    "            pendingOpenId = 0;\n"
    "            Intent r = new Intent(this, ReaderActivity.class);\n"
    "            r.putExtra(\"id\", found.id);\n"
    "            startActivity(r);\n"
    "        } catch(Exception e){}\n"
    "    }\n"
    "\n"
    "    private boolean notifGranted(){",
    "onNewIntent + resolver")

# (d) open the pending mail as soon as the list arrives
REP(M,
    "                    pushState();\n                    int last=Prefs.lastMsgId();",
    "                    pushState();\n                    openPendingMail();\n                    int last=Prefs.lastMsgId();",
    "loadMessages open pending")

# (e) the polling alert carries the message id + address
REP(M,
    "                        if(topMail!=null) Notifier.mail(this,topMail.sender,topMail.subject);",
    "                        if(topMail!=null) Notifier.mail(this,topMail.sender,topMail.subject,topMail.id,Prefs.address());",
    "loadMessages notify id")

# (f) retry the pending open on resume (e.g. intent delivered while paused)
REP(M,
    "        live=this;\n        pushState();",
    "        live=this;\n        pushState();\n        openPendingMail();",
    "onResume open pending")

# --- Notifier: id-carrying PendingIntent + the new tone names ---------------
N = J + "/Notifier.java"
REP(N,
    "    public static final String[] SND_NAMES = {\"Chime\", \"Ding\", \"Pop\"};",
    "    public static final String[] SND_NAMES = {\"Bell\", \"Chime\", \"Note\"};",
    "sound names")

REP(N,
    "    public static void mail(Context c, String from, String subject){\n"
    "        if(!Prefs.notifyOn()) return;",
    "    public static void mail(Context c, String from, String subject){\n"
    "        mail(c, from, subject, 0, \"\");\n"
    "    }\n"
    "    public static void mail(Context c, String from, String subject, int msgId, String address){\n"
    "        if(!Prefs.notifyOn()) return;",
    "mail overload")

REP(N,
    "            Intent open = new Intent(c, MainActivity.class);\n"
    "            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP);\n"
    "            int flags = PendingIntent.FLAG_UPDATE_CURRENT;\n"
    "            if(Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;\n"
    "            PendingIntent content = PendingIntent.getActivity(c, 0, open, flags);",
    "            Intent open = new Intent(c, MainActivity.class);\n"
    "            open.setFlags(Intent.FLAG_ACTIVITY_NEW_TASK | Intent.FLAG_ACTIVITY_CLEAR_TOP | Intent.FLAG_ACTIVITY_SINGLE_TOP);\n"
    "            if(msgId > 0) open.putExtra(\"open_msg_id\", msgId);\n"
    "            if(address != null && !address.isEmpty()) open.putExtra(\"open_address\", address);\n"
    "            int flags = PendingIntent.FLAG_UPDATE_CURRENT;\n"
    "            if(Build.VERSION.SDK_INT >= 23) flags |= PendingIntent.FLAG_IMMUTABLE;\n"
    "            PendingIntent content = PendingIntent.getActivity(c, msgId > 0 ? msgId : 0, open, flags);",
    "notification intent")

# --- MailService: polling alert carries id + address ------------------------
REP(J + "/MailService.java",
    "                    if(top!=null) Notifier.mail(this,top.optString(\"sender\"),top.optString(\"subject\"));",
    "                    if(top!=null) Notifier.mail(this,top.optString(\"sender\"),top.optString(\"subject\"),top.optInt(\"id\"),addr);",
    "service notify id")

# --- FcmService: forward id/address when the push carries them --------------
REP(J + "/FcmService.java",
    "            // Reuse the app's single notification system (Notifier) so the\n"
    "            // user's selected custom sound + channel are honoured.\n"
    "            Notifier.mail(this, title, body);",
    "            int mid = 0; String addr = null;\n"
    "            if(d != null){\n"
    "                try { mid = Integer.parseInt(String.valueOf(d.get(\"id\")).trim()); } catch(Exception e){}\n"
    "                addr = d.get(\"address\");\n"
    "            }\n"
    "            // Reuse the app's single notification system (Notifier) so the\n"
    "            // user's selected custom sound + channel are honoured.\n"
    "            Notifier.mail(this, title, body, mid, addr == null ? \"\" : addr);",
    "fcm notify id")


# ===========================================================================
# 4 (cont.) : sound-name arrays in every locale, so the picker keeps working.
# ===========================================================================
SOUND = {
    "": ["Bell", "Chime", "Note"],
    "-hi": ["\u092c\u0947\u0932", "\u091a\u093e\u0907\u092e", "\u0928\u094b\u091f"],
    "-es": ["Campana", "Campanilla", "Nota"],
    "-pt": ["Sino", "Campainha", "Nota"],
    "-ar": ["\u062c\u0631\u0633", "\u0631\u0646\u064a\u0646", "\u0646\u063a\u0645\u0629"],
    "-ru": ["\u041a\u043e\u043b\u043e\u043a\u043e\u043b", "\u0417\u0432\u043e\u043d", "\u041d\u043e\u0442\u0430"],
    "-in": ["Lonceng", "Denting", "Nada"],
}
snd_pat = re.compile(r'<string-array name="sound_names">.*?</string-array>', re.S)
for loc, names in SOUND.items():
    p = RES + "/values" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    s = R(p)
    block = ('<string-array name="sound_names">\n'
             + "".join("        <item>%s</item>\n" % n for n in names)
             + "    </string-array>")
    s2, cnt = snd_pat.subn(block, s)
    if cnt != 1:
        raise SystemExit("gn_af: sound_names array not found in %s" % p)
    W(p, s2)
    print("AF: patched %s (sound_names)" % p)


# ===========================================================================
# version bump 4.8 -> 4.9 (self-version + about strings).
# ===========================================================================
REP(J + "/Config.java",
    '            if(latest.equals("4.8")) return;',
    '            if(latest.equals("4.9")) return;',
    "self-version 4.9")

REP(J + "/SupportActivity.java",
    '    public static final String VERSION = "4.8";',
    '    public static final String VERSION = "4.9";',
    "support self-version 4.9")

for loc in ["", "-hi", "-es", "-pt", "-ar", "-ru", "-in"]:
    p = RES + "/values" + loc + "/strings.xml"
    if not os.path.exists(p):
        continue
    s = R(p)
    s2 = re.sub(r'(name="about_version">[^<]*?)4\.8(<)', r"\g<1>4.9\g<2>", s)
    if s2 == s:
        print("AF: (skip) about_version 4.8 not present in %s" % p)
    else:
        W(p, s2)
        print("AF: patched %s (about_version 4.9)" % p)

print("AF: done")
