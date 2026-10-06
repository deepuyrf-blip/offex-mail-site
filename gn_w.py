import os, re

# ---------------------------------------------------------------------------
# gn_w.py  (runs LAST, after gn_v, in the android.yml pipeline)
#
# v4.0 changes:
#   1. DEFAULT (English) RESOURCES ARE PURE ENGLISH. Every roman-Hindi
#      ("Hinglish") string that leaked into res/values/strings.xml (the default
#      locale) is replaced with clean, natural English.
#   2. The old roman-"Hinglish" locale is GONE. values-hi is regenerated from
#      scratch with proper Hindi in Devanagari script (the FULL key set).
#      The language picker label becomes "हिन्दी (Hindi)" and the LocaleHelper
#      mapping still uses the code "hi" for Hindi.
#   3. All other locales (es, pt, ar, ru, in) and Arabic RTL are untouched.
#   4. Version 3.9 -> 4.0 (versionName / versionCode / self-version / strings).
#
# Everything emitted by gn_a..gn_v is preserved: API endpoints/JSON fields, the
# mail ingest path, FCM pushes, the support feature, the bundled notification
# sounds, the bottom nav, the ad placements, the mandatory notification gate,
# the circular logo, the Create-button loading animation, the features section
# and the install-analytics reporting.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"

NEW_VERSION      = "4.0"
NEW_VERSION_CODE = "30"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def R(p):
    return open(p, encoding="utf-8").read()

def xml_escape(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace("'", "\\'").replace('"', '\\"')
    return t

def set_string(xml, key, value):
    """Replace the value of <string name="key">...</string>, keeping the key."""
    pat = re.compile(r'(<string name="%s">).*?(</string>)' % re.escape(key), re.S)
    if not pat.search(xml):
        raise SystemExit("gn_w: FATAL string key missing: %s" % key)
    return pat.sub(lambda m: m.group(1) + xml_escape(value) + m.group(2), xml, count=1)

# ===========================================================================
# 1 : clean, natural ENGLISH for every Hinglish string in the DEFAULT locale
# ===========================================================================
EN_FIXES = {
    "support_sub":
        "Something went wrong? Type your message and send it - we check it in "
        "the admin panel and help you quickly.",
    "notif_gate_body":
        "Offex Mail depends entirely on notifications - we alert you the moment "
        "new mail or an OTP arrives. The app cannot be used without allowing "
        "notifications. Tap Allow notifications and choose Allow to continue.",
    "contact_sub":
        "Any problem, question or suggestion? Get in touch with us - we reply quickly.",
    # The picker label for the Hindi option (shown in every locale).
    "lang_hi": "हिन्दी (Hindi)",
}

sp = RES + "/values/strings.xml"
s = R(sp)
for k, v in EN_FIXES.items():
    s = set_string(s, k, v)
# version strings that live inside the default resources
s = s.replace("3.9", NEW_VERSION)
W(sp, s)
print("W: values/strings.xml -> Hinglish removed, clean English + Hindi label")

# master key -> value map (used only to confirm parity below)
master = {}
for m in re.finditer(r'<string name="([^"]+)">(.*?)</string>', s, re.S):
    master[m.group(1)] = m.group(2)
print("W: default English key count = %d" % len(master))

# ===========================================================================
# 2 : PROPER HINDI (Devanagari) -- the FULL key set for values-hi
# ===========================================================================
HI_DEV = {
    "app_name": "Offex Mail",
    "tagline": "टेम्प मेल - तुरंत इनबॉक्स",
    "ob1_title": "तुरंत अस्थायी इनबॉक्स",
    "ob1_body": "एक टैप में निजी अस्थायी इनबॉक्स पाएं - OTP, वेरिफिकेशन लिंक और टेस्ट ईमेल के लिए।",
    "ob2_title": "नए मेल की सूचनाएं",
    "ob2_body": "ऐप बैकग्राउंड में जांच करता रहता है, इसलिए नया मेल आते ही आपको तुरंत सूचना मिलती है।",
    "ob3_title": "मुफ़्त - कोई साइनअप नहीं",
    "ob3_body": "न खाता, न पासवर्ड। हर इनबॉक्स कुछ समय बाद अपने आप समाप्त हो जाता है।",
    "ob4_title": "आपका ईमेल, आपके तरीके से",
    "ob4_body": "इनबॉक्स बनने से पहले नाम चुनें और अपनी पसंद का डोमेन चुनें।",
    "ob5_title": "इनबॉक्स तक तुरंत पहुंच",
    "ob5_body": "सेव किए गए इनबॉक्स के बीच स्विच करें और नया मेल आते ही पढ़ें।",
    "ob_next": "आगे बढ़ें",
    "ob_start": "शुरू करें",
    "ob_skip": "छोड़ें",
    "new_inbox": "नया इनबॉक्स",
    "hint_name": "नाम (वैकल्पिक)",
    "create_inbox": "इनबॉक्स बनाएं",
    "creating": "बन रहा है...",
    "your_address": "आपका अस्थायी पता",
    "copy": "कॉपी",
    "refresh": "रिफ्रेश",
    "delete": "हटाएं",
    "copied": "पता कॉपी हो गया",
    "messages": "संदेश",
    "inbox_title": "इनबॉक्स",
    "switch_title": "ईमेल बदलें",
    "choose_email": "अपना ईमेल पता चुनें",
    "create_new_email": "नया ईमेल बनाएं",
    "nav_email": "ईमेल",
    "nav_inbox": "इनबॉक्स",
    "nav_switch": "स्विच",
    "nav_more": "और",
    "message_label": "संदेश",
    "history": "इतिहास",
    "history_empty": "आपके पुराने इनबॉक्स यहां दिखेंगे। वापस जाने के लिए किसी एक पर टैप करें।",
    "no_messages": "अभी कोई मेल नहीं। यह पता जहां चाहिए वहां पेस्ट करें, मेल यहां आ जाएगा।",
    "notif_on": "सूचनाएं",
    "notif_channel": "नया मेल",
    "admin": "एडमिन पैनल",
    "admin_hint": "एडमिन कोड",
    "unlock": "अनलॉक",
    "wrong_code": "गलत कोड",
    "expires_in": "समाप्त होने में",
    "version": "संस्करण",
    "notif_service": "बैकग्राउंड सिंक",
    "features_title": "Offex Mail क्यों",
    "features_sub": "अस्थायी इनबॉक्स से जो चाहिए, सब कुछ",
    "feat1_t": "तुरंत इनबॉक्स",
    "feat1_d": "एक टैप में निजी पता - न साइनअप, न पासवर्ड।",
    "feat2_t": "OTP ऑटो-डिटेक्ट",
    "feat2_d": "हम वेरिफिकेशन कोड ढूंढकर एक टैप में कॉपी कर देते हैं।",
    "feat3_t": "वेरिफिकेशन लिंक",
    "feat3_d": "लिंक सीधे आपके ब्राउज़र में खुलते हैं ताकि आप तुरंत पुष्टि कर सकें।",
    "feat4_t": "नए मेल के अलर्ट",
    "feat4_d": "मेल आते ही सूचना पाएं, बैकग्राउंड में भी।",
    "feat5_t": "कस्टम डोमेन",
    "feat5_d": "शुरू करने से पहले नाम चुनें और अपनी पसंद का डोमेन चुनें।",
    "feat6_t": "ऑटो-एक्सपायरी",
    "feat6_d": "इनबॉक्स अपने आप खाली हो जाते हैं - कुछ भी हमेशा के लिए नहीं रखा जाता।",
    "otp_found": "वेरिफिकेशन कोड",
    "copy_code": "कोड कॉपी करें",
    "code_copied": "कोड कॉपी हो गया",
    "support_title": "चैट सपोर्ट",
    "support_sub": "कोई दिक्कत आई? अपना संदेश लिखकर भेजें - हम एडमिन पैनल में देखकर जल्दी मदद करते हैं।",
    "support_greeting": "नमस्ते! बताएं क्या दिक्कत हुई और Send दबाएं। आपका संदेश तुरंत हमारी टीम तक पहुंचता है।",
    "support_hint": "अपना संदेश लिखें…",
    "support_send": "भेजें",
    "support_retry": "फिर कोशिश करें",
    "support_sending": "भेजा जा रहा है…",
    "support_sent": "भेज दिया ✓",
    "support_failed": "भेज नहीं सके: ",
    "support_empty": "कृपया पहले अपना संदेश लिखें",
    "support_contact": "सपोर्ट से संपर्क करें",
    "support_error_title": "कुछ गलत हो गया",
    "notif_gate_title": "सूचनाएं ज़रूरी हैं",
    "notif_gate_body": "Offex Mail का पूरा काम सूचनाओं पर चलता है - नया मेल या OTP आते ही हम तुरंत बताते हैं। सूचना की अनुमति के बिना ऐप इस्तेमाल नहीं हो सकता। Allow notifications पर टैप करें और जारी रखने के लिए Allow चुनें।",
    "notif_gate_allow": "सूचनाएं अनुमति दें",
    "notif_gate_settings": "सेटिंग्स खोलें",
    "feature_whats_new": "नया क्या है",
    "feature_ok": "समझ गया",
    "domain_random": "रैंडम (ऑटो)",
    "toast_inbox_ready": "इनबॉक्स तैयार",
    "toast_inbox_deleted": "इनबॉक्स हटा दिया",
    "toast_saved": "सेव हो गया",
    "err_network": "नेटवर्क त्रुटि",
    "support_prefill_error": "मुझे यह त्रुटि मिली: %1$s",
    "dlg_dismiss": "बंद करें",
    "dlg_later": "बाद में",
    "update_title": "अपडेट उपलब्ध",
    "update_message": "Offex Mail %1$s आ गया है। नई सुविधाओं के लिए अपडेट करें।",
    "update_now": "अभी अपडेट करें",
    "sponsored": "प्रायोजित",
    "updater_title": "Offex Mail अपडेट",
    "updater_desc": "नया संस्करण डाउनलोड हो रहा है",
    "updater_starting": "डाउनलोड शुरू हो रहा है...",
    "updater_downloading_title": "अपडेट डाउनलोड हो रहा है",
    "updater_progress": "डाउनलोड हो रहा है... %1$d%%",
    "updater_failed": "डाउनलोड विफल रहा। कृपया फिर कोशिश करें।",
    "allow_install_title": "इंस्टॉल की अनुमति दें",
    "allow_install_body": "अपडेट इंस्टॉल करने के लिए Offex Mail को अज्ञात ऐप्स इंस्टॉल करने की अनुमति दें, फिर अपडेट दोबारा खोलें।",
    "open_settings": "सेटिंग्स खोलें",
    "about_body1": "Offex Mail एक मुफ़्त अस्थायी ईमेल सेवा है। OTP, वेरिफिकेशन लिंक और टेस्ट ईमेल के लिए एक टैप में अस्थायी इनबॉक्स बनाएं - न साइनअप, न पासवर्ड।",
    "about_body2": "हर इनबॉक्स कुछ समय बाद अपने आप समाप्त हो जाता है। कुछ भी हमेशा के लिए नहीं रखा जाता, और आपको अपना असली ईमेल पता कभी साझा नहीं करना पड़ता।",
    "about_version": "संस्करण 4.0",
    "contact_title": "संपर्क करें",
    "contact_sub": "कोई दिक्कत, सवाल या सुझाव? हमसे संपर्क करें - हम जल्दी जवाब देते हैं।",
    "contact_support_label": "सपोर्ट ईमेल",
    "contact_send_email": "ईमेल भेजें",
    "contact_website_label": "वेबसाइट",
    "contact_open_website": "वेबसाइट खोलें",
    "splash_loading": "लोड हो रहा है...",
    "item_mail_label": "मेल",
    "admin_sub": "हर इंस्टॉल किए गए डिवाइस पर घोषणा बैनर, विज्ञापन और अपडेट प्रॉम्प्ट भेजें।",
    "admin_announcement": "घोषणा",
    "admin_show_banner": "ऐप में बैनर दिखाएं",
    "admin_banner_hint": "बैनर संदेश",
    "admin_ads": "विज्ञापन",
    "admin_enable_ads": "AdMob विज्ञापन सक्षम करें",
    "admin_app_update": "ऐप अपडेट",
    "admin_latest_hint": "नवीनतम संस्करण (जैसे 4.0)",
    "admin_url_hint": "डाउनलोड URL",
    "admin_force": "फोर्स अपडेट (पुराना ऐप ब्लॉक करें)",
    "admin_save": "सेव करें",
    "admin_stats_prefix": "इनबॉक्स: %1$d   मेल: %2$d",
    "menu_title": "और",
    "menu_chat_support": "चैट सपोर्ट",
    "menu_about": "Offex Mail के बारे में",
    "menu_rate": "हमें रेट करें",
    "menu_privacy": "गोपनीयता नीति",
    "menu_terms": "उपयोग की शर्तें",
    "menu_contact": "संपर्क करें",
    "menu_language": "भाषा",
    "menu_theme": "थीम: %1$s",
    "menu_theme_dark": "डार्क",
    "menu_theme_light": "लाइट",
    "menu_notif": "सूचनाएं: %1$s",
    "menu_on": "चालू",
    "menu_off": "बंद",
    "menu_sound": "सूचना ध्वनि: %1$s",
    "menu_sound_title": "सूचना ध्वनि",
    "menu_done": "हो गया",
    "lang_title": "भाषा चुनें",
    "lang_en": "English",
    "lang_hi": "हिन्दी (Hindi)",
    "lang_es": "Español",
    "lang_pt": "Português",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

HI_SOUND_NAMES = ["चाइम", "डिंग", "पॉप"]

# key-parity guard: the Hindi locale must cover the exact same key set.
missing = [k for k in master if k not in HI_DEV]
extra   = [k for k in HI_DEV if k not in master]
if missing or extra:
    raise SystemExit("gn_w: FATAL Hindi key mismatch missing=%s extra=%s" % (missing, extra))

lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
for k in master:
    lines.append('    <string name="%s">%s</string>' % (k, xml_escape(HI_DEV[k])))
lines.append('    <string-array name="sound_names">')
for x in HI_SOUND_NAMES:
    lines.append("        <item>%s</item>" % xml_escape(x))
lines.append("    </string-array>")
lines.append("</resources>")
W(RES + "/values-hi/strings.xml", "\n".join(lines) + "\n")
print("W: values-hi/strings.xml -> proper Devanagari Hindi (%d strings)" % len(master))

# ===========================================================================
# 3 : other locales -- Hindi label + version strings only (translations kept)
# ===========================================================================
for code in ["es", "pt", "ar", "ru", "in"]:
    p = RES + "/values-%s/strings.xml" % code
    t = R(p)
    t = set_string(t, "lang_hi", "हिन्दी (Hindi)")
    t = t.replace("3.9", NEW_VERSION)
    W(p, t)
    print("W: values-%s/strings.xml -> Hindi label + v%s" % (code, NEW_VERSION))

# ===========================================================================
# 4 : LocaleHelper comment -- Hindi, not Hinglish
# ===========================================================================
p = J + "/LocaleHelper.java"
s = R(p)
s = s.replace("carries natural roman\n    // Hinglish strings (values-hi).",
              "carries Hindi (Devanagari)\n    // strings (values-hi).")
s = s.replace("Hinglish strings (values-hi)", "Hindi (Devanagari) strings (values-hi)")
W(p, s)
print("W: LocaleHelper.java -> comment updated (Hindi)")

# ===========================================================================
# 5 : version 3.9 -> 4.0
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = re.sub(r"versionCode \d+", "versionCode %s" % NEW_VERSION_CODE, s)
s = re.sub(r'versionName "[^"]*"', 'versionName "%s"' % NEW_VERSION, s)
W(bp, s)

cp = J + "/Config.java"
s = R(cp)
s = s.replace('latest.equals("3.9")', 'latest.equals("%s")' % NEW_VERSION)
W(cp, s)

sup = J + "/SupportActivity.java"
s = R(sup)
s = s.replace('public static final String VERSION = "3.9";',
              'public static final String VERSION = "%s";' % NEW_VERSION)
W(sup, s)

print("W: applied v4.0 (clean English default, Hinglish locale removed, "
      "Devanagari Hindi added; version 3.9 -> 4.0)")
