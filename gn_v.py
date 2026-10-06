import os, re

# ---------------------------------------------------------------------------
# gn_v.py  (runs LAST, after gn_u, in the android.yml pipeline)
#
# v3.9 changes:
#   1. MULTI-LANGUAGE: every remaining user-facing hardcoded string (Java + XML)
#      is moved into res/values/strings.xml (English default) and translated
#      into values-hi (natural roman Hinglish), values-es, values-pt, values-ar
#      (RTL-aware), values-ru and values-in.
#   2. In-app LANGUAGE SWITCHER (More menu) that persists the choice in
#      SharedPreferences and applies it via a locale-wrapping BaseActivity on
#      every API level (plus Locale.setDefault for the process).
#   3. APP ANALYTICS: Install.java reports a stable install id + device model,
#      Android version/SDK, app version/versionCode, locale, screen size and
#      first/last-seen timestamps to POST /api/app/install on every launch.
#   4. Version 3.8 -> 3.9.
#
# Everything emitted by gn_a..gn_u is preserved: API endpoints/JSON fields, the
# mail ingest path, FCM pushes, the support feature, the bundled notification
# sounds, the bottom nav, the ad placements, the mandatory notification gate,
# the circular logo, the Create-button loading animation and the features
# section.
# ---------------------------------------------------------------------------

J   = "android/app/src/main/java/online/mytempmail/app"
RES = "android/app/src/main/res"
LAY = RES + "/layout"

def W(p, c):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "w", encoding="utf-8").write(c)

def WB(p, b):
    os.makedirs(os.path.dirname(p), exist_ok=True)
    open(p, "wb").write(b)

def R(p):
    return open(p, encoding="utf-8").read()

def rep(s, old, new, name):
    if old not in s:
        raise SystemExit("gn_v: FATAL anchor missing (%s)" % name)
    return s.replace(old, new, 1)

def xml_escape(t):
    t = t.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")
    t = t.replace("'", "\\'").replace('"', '\\"')
    return t

# ===========================================================================
# 1 : NEW English string keys (existing keys are already in strings.xml)
# ===========================================================================
NEW_EN = [
    ("domain_random", "Random (auto)"),
    ("toast_inbox_ready", "Inbox ready"),
    ("toast_inbox_deleted", "Inbox deleted"),
    ("toast_saved", "Saved"),
    ("err_network", "network error"),
    ("support_prefill_error", "I hit this error: %1$s"),
    ("dlg_dismiss", "Dismiss"),
    ("dlg_later", "Later"),
    ("update_title", "Update available"),
    ("update_message", "Offex Mail %1$s is here. Update to get the new features."),
    ("update_now", "Update now"),
    ("sponsored", "Sponsored"),
    ("updater_title", "Offex Mail update"),
    ("updater_desc", "Downloading the new version"),
    ("updater_starting", "Starting download..."),
    ("updater_downloading_title", "Downloading update"),
    ("updater_progress", "Downloading... %1$d%%"),
    ("updater_failed", "Download failed. Please try again."),
    ("allow_install_title", "Allow install"),
    ("allow_install_body", "To install the update, allow Offex Mail to install unknown apps, then open the update again."),
    ("open_settings", "Open settings"),
    ("about_body1", "Offex Mail is a free temporary email service. Create a disposable inbox in one tap for OTPs, verification links and test emails - no signup, no password."),
    ("about_body2", "Every inbox expires automatically after a while. Nothing is kept forever, and you never have to share your real email address."),
    ("about_version", "Version 3.9"),
    ("contact_title", "Contact us"),
    ("contact_sub", "Koi dikkat, sawal ya suggestion? Hum se rabta karo - hum jaldi reply karte hain."),
    ("contact_support_label", "Support email"),
    ("contact_send_email", "Send email"),
    ("contact_website_label", "Website"),
    ("contact_open_website", "Open website"),
    ("splash_loading", "Loading..."),
    ("item_mail_label", "MAIL"),
    ("admin_sub", "Push the announcement banner, ads and update prompt to every installed device."),
    ("admin_announcement", "Announcement"),
    ("admin_show_banner", "Show banner in app"),
    ("admin_banner_hint", "Banner message"),
    ("admin_ads", "Ads"),
    ("admin_enable_ads", "Enable AdMob ads"),
    ("admin_app_update", "App update"),
    ("admin_latest_hint", "Latest version (e.g. 3.9)"),
    ("admin_url_hint", "Download URL"),
    ("admin_force", "Force update (block old app)"),
    ("admin_save", "Save"),
    ("admin_stats_prefix", "Inboxes: %1$d   Mails: %2$d"),
    ("menu_title", "More"),
    ("menu_chat_support", "Chat Support"),
    ("menu_about", "About Offex Mail"),
    ("menu_rate", "Rate us"),
    ("menu_privacy", "Privacy Policy"),
    ("menu_terms", "Terms of Use"),
    ("menu_contact", "Contact us"),
    ("menu_language", "Language"),
    ("menu_theme", "Theme: %1$s"),
    ("menu_theme_dark", "Dark"),
    ("menu_theme_light", "Light"),
    ("menu_notif", "Notifications: %1$s"),
    ("menu_on", "ON"),
    ("menu_off", "OFF"),
    ("menu_sound", "Notification sound: %1$s"),
    ("menu_sound_title", "Notification sound"),
    ("menu_done", "Done"),
    ("lang_title", "Choose language"),
    ("lang_en", "English"),
    ("lang_hi", "Hinglish"),
    ("lang_es", "Espanol"),
    ("lang_pt", "Portugues"),
    ("lang_ar", "العربية"),
    ("lang_ru", "Русский"),
    ("lang_in", "Bahasa Indonesia"),
]

# ===========================================================================
# 2 : translations (fall back to English for any key omitted here)
# ===========================================================================
HI = {
    "tagline": "Temp Mail - Instant Inbox",
    "ob1_title": "Turant disposable inbox",
    "ob1_body": "Ek tap me private disposable inbox - OTP, verification link aur test email ke liye.",
    "ob2_title": "Naye mail ki notification",
    "ob2_body": "App background me check karta rehta hai, isliye naya mail aate hi turant notification milti hai.",
    "ob3_title": "Free - No signup",
    "ob3_body": "Na account, na password. Har inbox kuch der baad khud expire ho jaata hai.",
    "ob4_title": "Apni email, apne tarike se",
    "ob4_body": "Inbox banane se pehle naam chuno aur apna pasandida domain select karo.",
    "ob5_title": "Inbox tak quick access",
    "ob5_body": "Saved inboxes ke beech switch karo aur naya mail aate hi padho.",
    "ob_next": "Aage",
    "ob_start": "Shuru karo",
    "ob_skip": "Skip",
    "new_inbox": "Naya inbox",
    "hint_name": "Naam (optional)",
    "create_inbox": "Inbox banao",
    "creating": "Ban raha hai...",
    "your_address": "Aapka temporary address",
    "copy": "Copy",
    "refresh": "Refresh",
    "delete": "Delete",
    "copied": "Address copy ho gaya",
    "messages": "Messages",
    "inbox_title": "Inbox",
    "switch_title": "Email switch karo",
    "choose_email": "Apna email address chuno",
    "create_new_email": "Naya email banao",
    "nav_email": "Email",
    "nav_inbox": "Inbox",
    "nav_switch": "Switch",
    "nav_more": "More",
    "message_label": "MESSAGE",
    "history": "History",
    "history_empty": "Aapke purane inbox yahan dikhenge. Switch karne ke liye kisi pe tap karo.",
    "no_messages": "Abhi koi mail nahi. Yeh address jahan chahiye paste karo, mail yahan aa jayega.",
    "notif_on": "Notifications",
    "notif_channel": "Naya mail",
    "admin": "Admin panel",
    "admin_hint": "Admin code",
    "unlock": "Unlock",
    "wrong_code": "Galat code",
    "expires_in": "Expire hone me",
    "version": "Version",
    "notif_service": "Background sync",
    "features_title": "Offex Mail kyun",
    "features_sub": "Temporary inbox ke liye sab kuch jo chahiye",
    "feat1_t": "Turant inbox",
    "feat1_d": "Ek tap me private address - na signup, na password.",
    "feat2_t": "OTP auto-detect",
    "feat2_d": "Hum verification code dhoondh ke ek tap me copy kar dete hain.",
    "feat3_t": "Verification links",
    "feat3_d": "Links seedha browser me khulte hain, turant confirm karo.",
    "feat4_t": "Naye mail ke alerts",
    "feat4_d": "Mail aate hi notify hote ho, background me bhi.",
    "feat5_t": "Custom domains",
    "feat5_d": "Shuru karne se pehle naam aur pasandida domain chuno.",
    "feat6_t": "Auto-expiry",
    "feat6_d": "Inbox khud clear ho jaate hain - kuch hamesha ke liye nahi rakha jaata.",
    "otp_found": "VERIFICATION CODE",
    "copy_code": "Code copy karo",
    "code_copied": "Code copy ho gaya",
    "support_title": "Chat Support",
    "support_sub": "Koi dikkat aa gayi? Apna message likh ke bhejo - hum admin panel me dekh kar jaldi help karte hain.",
    "support_greeting": "Hi! Batao kya problem hui aur Send dabao. Aapka message turant hamari team tak pahunchta hai.",
    "support_hint": "Apna message likho…",
    "support_send": "Send",
    "support_retry": "Retry",
    "support_sending": "Bhej rahe hain…",
    "support_sent": "Sent ✓",
    "support_failed": "Send nahi hua: ",
    "support_empty": "Pehle apna message likho",
    "support_contact": "Support se baat karo",
    "support_error_title": "Kuch galat ho gaya",
    "notif_gate_title": "Notifications zaroori hain",
    "notif_gate_body": "Offex Mail ka poora kaam notifications par chalta hai - naya mail ya OTP aate hi hum turant batate hain. Notification allow kiye bina app use nahi ho sakta. Tap Allow notifications and choose Allow to continue.",
    "notif_gate_allow": "Allow notifications",
    "notif_gate_settings": "Open settings",
    "feature_whats_new": "Naya kya hai",
    "feature_ok": "Samajh gaya",
    "domain_random": "Random (auto)",
    "toast_inbox_ready": "Inbox ready",
    "toast_inbox_deleted": "Inbox delete ho gaya",
    "toast_saved": "Save ho gaya",
    "err_network": "network error",
    "support_prefill_error": "Mujhe yeh error aaya: %1$s",
    "dlg_dismiss": "Band karo",
    "dlg_later": "Baad me",
    "update_title": "Update available",
    "update_message": "Offex Mail %1$s aa gaya hai. Naye features ke liye update karo.",
    "update_now": "Abhi update karo",
    "sponsored": "Sponsored",
    "updater_title": "Offex Mail update",
    "updater_desc": "Naya version download ho raha hai",
    "updater_starting": "Download shuru ho raha hai...",
    "updater_downloading_title": "Update download ho raha hai",
    "updater_progress": "Download ho raha hai... %1$d%%",
    "updater_failed": "Download fail ho gaya. Phir se try karo.",
    "allow_install_title": "Install ki permission do",
    "allow_install_body": "Update install karne ke liye Offex Mail ko unknown apps install karne ki permission do, phir update dobara kholo.",
    "open_settings": "Settings kholo",
    "about_body1": "Offex Mail ek free temporary email service hai. OTP, verification link aur test email ke liye ek tap me disposable inbox banao - na signup, na password.",
    "about_body2": "Har inbox kuch der baad khud expire ho jaata hai. Kuch hamesha ke liye nahi rakha jaata, aur aapko apni asli email kabhi deni nahi padti.",
    "about_version": "Version 3.9",
    "contact_title": "Hum se rabta karo",
    "contact_sub": "Koi dikkat, sawal ya suggestion? Hum se rabta karo - hum jaldi reply karte hain.",
    "contact_support_label": "Support email",
    "contact_send_email": "Email bhejo",
    "contact_website_label": "Website",
    "contact_open_website": "Website kholo",
    "splash_loading": "Load ho raha hai...",
    "item_mail_label": "MAIL",
    "admin_sub": "Announcement banner, ads aur update prompt har installed device pe bhejo.",
    "admin_announcement": "Announcement",
    "admin_show_banner": "App me banner dikhao",
    "admin_banner_hint": "Banner message",
    "admin_ads": "Ads",
    "admin_enable_ads": "AdMob ads enable karo",
    "admin_app_update": "App update",
    "admin_latest_hint": "Latest version (jaise 3.9)",
    "admin_url_hint": "Download URL",
    "admin_force": "Force update (purani app block karo)",
    "admin_save": "Save",
    "admin_stats_prefix": "Inboxes: %1$d   Mails: %2$d",
    "menu_title": "More",
    "menu_chat_support": "Chat Support",
    "menu_about": "Offex Mail ke baare me",
    "menu_rate": "Rate us",
    "menu_privacy": "Privacy Policy",
    "menu_terms": "Terms of Use",
    "menu_contact": "Hum se rabta karo",
    "menu_language": "Language",
    "menu_theme": "Theme: %1$s",
    "menu_theme_dark": "Dark",
    "menu_theme_light": "Light",
    "menu_notif": "Notifications: %1$s",
    "menu_on": "ON",
    "menu_off": "OFF",
    "menu_sound": "Notification sound: %1$s",
    "menu_sound_title": "Notification sound",
    "menu_done": "Done",
    "lang_title": "Language chuno",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

ES = {
    "tagline": "Correo temporal - bandeja al instante",
    "ob1_title": "Bandeja desechable al instante",
    "ob1_body": "Consigue una bandeja privada y desechable con un toque, para OTP, enlaces de verificacion y correos de prueba.",
    "ob2_title": "Avisos de correo nuevo",
    "ob2_body": "La app sigue comprobando en segundo plano, asi recibes un aviso en cuanto llega correo nuevo.",
    "ob3_title": "Gratis - sin registro",
    "ob3_body": "Sin cuenta y sin contrasena. Cada bandeja caduca sola despues de un tiempo.",
    "ob4_title": "Tu correo, a tu manera",
    "ob4_body": "Elige un nombre y el dominio que quieras antes de crear tu bandeja.",
    "ob5_title": "Acceso rapido a la bandeja",
    "ob5_body": "Cambia entre bandejas guardadas y lee el correo nuevo en cuanto llega.",
    "ob_next": "Continuar",
    "ob_start": "Empezar",
    "ob_skip": "Omitir",
    "new_inbox": "Nueva bandeja",
    "hint_name": "Nombre (opcional)",
    "create_inbox": "Crear bandeja",
    "creating": "Creando...",
    "your_address": "Tu direccion temporal",
    "copy": "Copiar",
    "refresh": "Actualizar",
    "delete": "Borrar",
    "copied": "Direccion copiada",
    "messages": "Mensajes",
    "inbox_title": "Bandeja",
    "switch_title": "Cambiar correo",
    "choose_email": "Elige tu direccion de correo",
    "create_new_email": "Crear correo nuevo",
    "nav_email": "Correo",
    "nav_inbox": "Bandeja",
    "nav_switch": "Cambiar",
    "nav_more": "Mas",
    "message_label": "MENSAJE",
    "history": "Historial",
    "history_empty": "Tus bandejas anteriores apareceran aqui. Toca una para volver a ella.",
    "no_messages": "Aun no hay correo. Pega esta direccion donde la necesites y el correo llegara aqui.",
    "notif_on": "Notificaciones",
    "notif_channel": "Correo nuevo",
    "admin": "Panel de admin",
    "admin_hint": "Codigo de admin",
    "unlock": "Desbloquear",
    "wrong_code": "Codigo incorrecto",
    "expires_in": "Caduca en",
    "version": "Version",
    "notif_service": "Sincronizacion en segundo plano",
    "features_title": "Por que Offex Mail",
    "features_sub": "Todo lo que necesitas de una bandeja temporal",
    "feat1_t": "Bandeja al instante",
    "feat1_d": "Una direccion privada con un toque, sin registro ni contrasena.",
    "feat2_t": "Deteccion de OTP",
    "feat2_d": "Detectamos el codigo de verificacion y lo copiamos con un toque.",
    "feat3_t": "Enlaces de verificacion",
    "feat3_d": "Los enlaces se abren en tu navegador para confirmar rapido.",
    "feat4_t": "Avisos de correo nuevo",
    "feat4_d": "Te avisamos en cuanto llega correo, incluso en segundo plano.",
    "feat5_t": "Dominios personalizados",
    "feat5_d": "Elige un nombre y el dominio que quieras antes de empezar.",
    "feat6_t": "Caducidad automatica",
    "feat6_d": "Las bandejas se limpian solas, nada se guarda para siempre.",
    "otp_found": "CODIGO DE VERIFICACION",
    "copy_code": "Copiar codigo",
    "code_copied": "Codigo copiado",
    "support_title": "Soporte por chat",
    "support_sub": "Algo salio mal? Escribe tu mensaje y envialo: lo vemos en el panel y te ayudamos rapido.",
    "support_greeting": "Hola! Cuentanos que paso y pulsa Enviar. Tu mensaje llega al equipo al instante.",
    "support_hint": "Escribe tu mensaje…",
    "support_send": "Enviar",
    "support_retry": "Reintentar",
    "support_sending": "Enviando…",
    "support_sent": "Enviado ✓",
    "support_failed": "No se pudo enviar: ",
    "support_empty": "Escribe primero tu mensaje",
    "support_contact": "Contactar con soporte",
    "support_error_title": "Algo salio mal",
    "notif_gate_title": "Las notificaciones son obligatorias",
    "notif_gate_body": "Offex Mail depende de las notificaciones: te avisamos en cuanto llega correo nuevo o un OTP. Sin permitir las notificaciones no puedes usar la app. Pulsa Permitir notificaciones y elige Permitir para continuar.",
    "notif_gate_allow": "Permitir notificaciones",
    "notif_gate_settings": "Abrir ajustes",
    "feature_whats_new": "Novedades",
    "feature_ok": "Entendido",
    "domain_random": "Aleatorio (auto)",
    "toast_inbox_ready": "Bandeja lista",
    "toast_inbox_deleted": "Bandeja borrada",
    "toast_saved": "Guardado",
    "err_network": "error de red",
    "support_prefill_error": "Me salio este error: %1$s",
    "dlg_dismiss": "Cerrar",
    "dlg_later": "Mas tarde",
    "update_title": "Actualizacion disponible",
    "update_message": "Offex Mail %1$s ya esta aqui. Actualiza para tener las novedades.",
    "update_now": "Actualizar ahora",
    "sponsored": "Patrocinado",
    "updater_title": "Actualizacion de Offex Mail",
    "updater_desc": "Descargando la nueva version",
    "updater_starting": "Iniciando descarga...",
    "updater_downloading_title": "Descargando actualizacion",
    "updater_progress": "Descargando... %1$d%%",
    "updater_failed": "La descarga fallo. Intentalo de nuevo.",
    "allow_install_title": "Permitir instalacion",
    "allow_install_body": "Para instalar la actualizacion, permite que Offex Mail instale apps desconocidas y vuelve a abrir la actualizacion.",
    "open_settings": "Abrir ajustes",
    "about_body1": "Offex Mail es un servicio gratuito de correo temporal. Crea una bandeja desechable con un toque para OTP, enlaces de verificacion y correos de prueba, sin registro ni contrasena.",
    "about_body2": "Cada bandeja caduca automaticamente despues de un tiempo. Nada se guarda para siempre y nunca tienes que dar tu correo real.",
    "about_version": "Version 3.9",
    "contact_title": "Contactanos",
    "contact_sub": "Alguna duda, pregunta o sugerencia? Escribenos, respondemos rapido.",
    "contact_support_label": "Correo de soporte",
    "contact_send_email": "Enviar correo",
    "contact_website_label": "Sitio web",
    "contact_open_website": "Abrir sitio web",
    "splash_loading": "Cargando...",
    "item_mail_label": "CORREO",
    "admin_sub": "Envia el banner de anuncio, los anuncios y el aviso de actualizacion a todos los dispositivos instalados.",
    "admin_announcement": "Anuncio",
    "admin_show_banner": "Mostrar banner en la app",
    "admin_banner_hint": "Mensaje del banner",
    "admin_ads": "Anuncios",
    "admin_enable_ads": "Activar anuncios AdMob",
    "admin_app_update": "Actualizacion de la app",
    "admin_latest_hint": "Ultima version (p. ej. 3.9)",
    "admin_url_hint": "URL de descarga",
    "admin_force": "Forzar actualizacion (bloquear app antigua)",
    "admin_save": "Guardar",
    "admin_stats_prefix": "Bandejas: %1$d   Correos: %2$d",
    "menu_title": "Mas",
    "menu_chat_support": "Soporte por chat",
    "menu_about": "Acerca de Offex Mail",
    "menu_rate": "Valoranos",
    "menu_privacy": "Politica de privacidad",
    "menu_terms": "Terminos de uso",
    "menu_contact": "Contactanos",
    "menu_language": "Idioma",
    "menu_theme": "Tema: %1$s",
    "menu_theme_dark": "Oscuro",
    "menu_theme_light": "Claro",
    "menu_notif": "Notificaciones: %1$s",
    "menu_on": "ON",
    "menu_off": "OFF",
    "menu_sound": "Sonido de notificacion: %1$s",
    "menu_sound_title": "Sonido de notificacion",
    "menu_done": "Listo",
    "lang_title": "Elige idioma",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

PT = {
    "tagline": "Email temporario - caixa de entrada instantanea",
    "ob1_title": "Caixa descartavel instantanea",
    "ob1_body": "Tenha uma caixa privada e descartavel com um toque, para OTP, links de verificacao e emails de teste.",
    "ob2_title": "Avisos de novo email",
    "ob2_body": "O app continua checando em segundo plano, entao voce recebe um aviso assim que chega email novo.",
    "ob3_title": "Gratis - sem cadastro",
    "ob3_body": "Sem conta e sem senha. Cada caixa expira sozinha depois de um tempo.",
    "ob4_title": "Seu email, do seu jeito",
    "ob4_body": "Escolha um nome e o dominio que quiser antes de criar sua caixa.",
    "ob5_title": "Acesso rapido a caixa",
    "ob5_body": "Alterne entre caixas salvas e leia o email novo assim que chegar.",
    "ob_next": "Continuar",
    "ob_start": "Comecar",
    "ob_skip": "Pular",
    "new_inbox": "Nova caixa",
    "hint_name": "Nome (opcional)",
    "create_inbox": "Criar caixa",
    "creating": "Criando...",
    "your_address": "Seu endereco temporario",
    "copy": "Copiar",
    "refresh": "Atualizar",
    "delete": "Excluir",
    "copied": "Endereco copiado",
    "messages": "Mensagens",
    "inbox_title": "Caixa de entrada",
    "switch_title": "Trocar email",
    "choose_email": "Escolha seu endereco de email",
    "create_new_email": "Criar novo email",
    "nav_email": "Email",
    "nav_inbox": "Caixa",
    "nav_switch": "Trocar",
    "nav_more": "Mais",
    "message_label": "MENSAGEM",
    "history": "Historico",
    "history_empty": "Suas caixas anteriores aparecerao aqui. Toque em uma para voltar a ela.",
    "no_messages": "Ainda nao ha email. Cole este endereco onde precisar e o email chegara aqui.",
    "notif_on": "Notificacoes",
    "notif_channel": "Email novo",
    "admin": "Painel do admin",
    "admin_hint": "Codigo do admin",
    "unlock": "Desbloquear",
    "wrong_code": "Codigo incorreto",
    "expires_in": "Expira em",
    "version": "Versao",
    "notif_service": "Sincronizacao em segundo plano",
    "features_title": "Por que o Offex Mail",
    "features_sub": "Tudo que voce precisa de uma caixa temporaria",
    "feat1_t": "Caixa instantanea",
    "feat1_d": "Um endereco privado com um toque, sem cadastro e sem senha.",
    "feat2_t": "Deteccao de OTP",
    "feat2_d": "Detectamos o codigo de verificacao e copiamos com um toque.",
    "feat3_t": "Links de verificacao",
    "feat3_d": "Os links abrem no seu navegador para confirmar rapido.",
    "feat4_t": "Avisos de novo email",
    "feat4_d": "Avisamos assim que o email chega, mesmo em segundo plano.",
    "feat5_t": "Dominios personalizados",
    "feat5_d": "Escolha um nome e o dominio que quiser antes de comecar.",
    "feat6_t": "Expiracao automatica",
    "feat6_d": "As caixas se limpam sozinhas, nada fica para sempre.",
    "otp_found": "CODIGO DE VERIFICACAO",
    "copy_code": "Copiar codigo",
    "code_copied": "Codigo copiado",
    "support_title": "Suporte por chat",
    "support_sub": "Algo deu errado? Escreva sua mensagem e envie: vemos no painel e ajudamos rapido.",
    "support_greeting": "Oi! Conte o que aconteceu e toque em Enviar. Sua mensagem chega na equipe na hora.",
    "support_hint": "Digite sua mensagem…",
    "support_send": "Enviar",
    "support_retry": "Tentar de novo",
    "support_sending": "Enviando…",
    "support_sent": "Enviado ✓",
    "support_failed": "Nao foi possivel enviar: ",
    "support_empty": "Escreva sua mensagem primeiro",
    "support_contact": "Falar com o suporte",
    "support_error_title": "Algo deu errado",
    "notif_gate_title": "As notificacoes sao obrigatorias",
    "notif_gate_body": "O Offex Mail depende das notificacoes: avisamos assim que chega email novo ou um OTP. Sem permitir as notificacoes voce nao pode usar o app. Toque em Permitir notificacoes e escolha Permitir para continuar.",
    "notif_gate_allow": "Permitir notificacoes",
    "notif_gate_settings": "Abrir configuracoes",
    "feature_whats_new": "Novidades",
    "feature_ok": "Entendi",
    "domain_random": "Aleatorio (auto)",
    "toast_inbox_ready": "Caixa pronta",
    "toast_inbox_deleted": "Caixa excluida",
    "toast_saved": "Salvo",
    "err_network": "erro de rede",
    "support_prefill_error": "Recebi este erro: %1$s",
    "dlg_dismiss": "Fechar",
    "dlg_later": "Mais tarde",
    "update_title": "Atualizacao disponivel",
    "update_message": "O Offex Mail %1$s chegou. Atualize para ter as novidades.",
    "update_now": "Atualizar agora",
    "sponsored": "Patrocinado",
    "updater_title": "Atualizacao do Offex Mail",
    "updater_desc": "Baixando a nova versao",
    "updater_starting": "Iniciando download...",
    "updater_downloading_title": "Baixando atualizacao",
    "updater_progress": "Baixando... %1$d%%",
    "updater_failed": "O download falhou. Tente de novo.",
    "allow_install_title": "Permitir instalacao",
    "allow_install_body": "Para instalar a atualizacao, permita que o Offex Mail instale apps desconhecidos e abra a atualizacao de novo.",
    "open_settings": "Abrir configuracoes",
    "about_body1": "O Offex Mail e um servico gratuito de email temporario. Crie uma caixa descartavel com um toque para OTP, links de verificacao e emails de teste, sem cadastro e sem senha.",
    "about_body2": "Cada caixa expira automaticamente depois de um tempo. Nada fica para sempre e voce nunca precisa dar seu email real.",
    "about_version": "Versao 3.9",
    "contact_title": "Fale conosco",
    "contact_sub": "Alguma duvida, pergunta ou sugestao? Fale com a gente, respondemos rapido.",
    "contact_support_label": "Email de suporte",
    "contact_send_email": "Enviar email",
    "contact_website_label": "Site",
    "contact_open_website": "Abrir site",
    "splash_loading": "Carregando...",
    "item_mail_label": "EMAIL",
    "admin_sub": "Envie o banner de anuncio, os anuncios e o aviso de atualizacao para todos os dispositivos instalados.",
    "admin_announcement": "Anuncio",
    "admin_show_banner": "Mostrar banner no app",
    "admin_banner_hint": "Mensagem do banner",
    "admin_ads": "Anuncios",
    "admin_enable_ads": "Ativar anuncios AdMob",
    "admin_app_update": "Atualizacao do app",
    "admin_latest_hint": "Ultima versao (ex. 3.9)",
    "admin_url_hint": "URL de download",
    "admin_force": "Forcar atualizacao (bloquear app antigo)",
    "admin_save": "Salvar",
    "admin_stats_prefix": "Caixas: %1$d   Emails: %2$d",
    "menu_title": "Mais",
    "menu_chat_support": "Suporte por chat",
    "menu_about": "Sobre o Offex Mail",
    "menu_rate": "Avalie a gente",
    "menu_privacy": "Politica de privacidade",
    "menu_terms": "Termos de uso",
    "menu_contact": "Fale conosco",
    "menu_language": "Idioma",
    "menu_theme": "Tema: %1$s",
    "menu_theme_dark": "Escuro",
    "menu_theme_light": "Claro",
    "menu_notif": "Notificacoes: %1$s",
    "menu_on": "ON",
    "menu_off": "OFF",
    "menu_sound": "Som de notificacao: %1$s",
    "menu_sound_title": "Som de notificacao",
    "menu_done": "Pronto",
    "lang_title": "Escolha o idioma",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

RU = {
    "tagline": "Временная почта - мгновенный ящик",
    "ob1_title": "Мгновенный одноразовый ящик",
    "ob1_body": "Приватный одноразовый ящик в один тап - для OTP, ссылок подтверждения и тестовых писем.",
    "ob2_title": "Уведомления о новых письмах",
    "ob2_body": "Приложение проверяет в фоне, поэтому вы получаете уведомление сразу при появлении нового письма.",
    "ob3_title": "Бесплатно - без регистрации",
    "ob3_body": "Без аккаунта и пароля. Каждый ящик сам истекает через некоторое время.",
    "ob4_title": "Ваша почта по-вашему",
    "ob4_body": "Выберите имя и домен, который нравится, перед созданием ящика.",
    "ob5_title": "Быстрый доступ к ящику",
    "ob5_body": "Переключайтесь между сохранёнными ящиками и читайте новые письма сразу.",
    "ob_next": "Далее",
    "ob_start": "Начать",
    "ob_skip": "Пропустить",
    "new_inbox": "Новый ящик",
    "hint_name": "Имя (необязательно)",
    "create_inbox": "Создать ящик",
    "creating": "Создание...",
    "your_address": "Ваш временный адрес",
    "copy": "Копировать",
    "refresh": "Обновить",
    "delete": "Удалить",
    "copied": "Адрес скопирован",
    "messages": "Сообщения",
    "inbox_title": "Входящие",
    "switch_title": "Сменить почту",
    "choose_email": "Выберите ваш адрес почты",
    "create_new_email": "Создать новую почту",
    "nav_email": "Почта",
    "nav_inbox": "Ящик",
    "nav_switch": "Сменить",
    "nav_more": "Ещё",
    "message_label": "СООБЩЕНИЕ",
    "history": "История",
    "history_empty": "Здесь появятся ваши прошлые ящики. Нажмите на любой, чтобы вернуться.",
    "no_messages": "Писем пока нет. Вставьте этот адрес где нужно, и письмо придёт сюда.",
    "notif_on": "Уведомления",
    "notif_channel": "Новое письмо",
    "admin": "Панель админа",
    "admin_hint": "Код админа",
    "unlock": "Открыть",
    "wrong_code": "Неверный код",
    "expires_in": "Истекает через",
    "version": "Версия",
    "notif_service": "Фоновая синхронизация",
    "features_title": "Почему Offex Mail",
    "features_sub": "Всё, что нужно от временного ящика",
    "feat1_t": "Мгновенный ящик",
    "feat1_d": "Приватный адрес в один тап - без регистрации и пароля.",
    "feat2_t": "Автопоиск OTP",
    "feat2_d": "Мы находим код подтверждения и копируем его в один тап.",
    "feat3_t": "Ссылки подтверждения",
    "feat3_d": "Ссылки открываются сразу в браузере, чтобы подтвердить быстро.",
    "feat4_t": "Оповещения о письмах",
    "feat4_d": "Сообщаем сразу при появлении письма, даже в фоне.",
    "feat5_t": "Свои домены",
    "feat5_d": "Выберите имя и домен, который нравится, перед началом.",
    "feat6_t": "Автоистечение",
    "feat6_d": "Ящики очищаются сами - ничего не хранится вечно.",
    "otp_found": "КОД ПОДТВЕРЖДЕНИЯ",
    "copy_code": "Копировать код",
    "code_copied": "Код скопирован",
    "support_title": "Чат поддержки",
    "support_sub": "Что-то не так? Напишите сообщение и отправьте - мы видим его в панели и быстро помогаем.",
    "support_greeting": "Привет! Расскажите, что случилось, и нажмите Отправить. Сообщение сразу дойдёт до команды.",
    "support_hint": "Введите сообщение…",
    "support_send": "Отправить",
    "support_retry": "Повторить",
    "support_sending": "Отправка…",
    "support_sent": "Отправлено ✓",
    "support_failed": "Не удалось отправить: ",
    "support_empty": "Сначала введите сообщение",
    "support_contact": "Связаться с поддержкой",
    "support_error_title": "Что-то пошло не так",
    "notif_gate_title": "Уведомления обязательны",
    "notif_gate_body": "Вся работа Offex Mail зависит от уведомлений: мы сообщаем сразу при появлении письма или OTP. Без разрешения уведомлений приложением пользоваться нельзя. Нажмите Разрешить уведомления и выберите Разрешить, чтобы продолжить.",
    "notif_gate_allow": "Разрешить уведомления",
    "notif_gate_settings": "Открыть настройки",
    "feature_whats_new": "Что нового",
    "feature_ok": "Понятно",
    "domain_random": "Случайно (авто)",
    "toast_inbox_ready": "Ящик готов",
    "toast_inbox_deleted": "Ящик удалён",
    "toast_saved": "Сохранено",
    "err_network": "ошибка сети",
    "support_prefill_error": "У меня такая ошибка: %1$s",
    "dlg_dismiss": "Закрыть",
    "dlg_later": "Позже",
    "update_title": "Доступно обновление",
    "update_message": "Вышла Offex Mail %1$s. Обновитесь, чтобы получить новые функции.",
    "update_now": "Обновить сейчас",
    "sponsored": "Реклама",
    "updater_title": "Обновление Offex Mail",
    "updater_desc": "Загрузка новой версии",
    "updater_starting": "Начало загрузки...",
    "updater_downloading_title": "Загрузка обновления",
    "updater_progress": "Загрузка... %1$d%%",
    "updater_failed": "Загрузка не удалась. Попробуйте снова.",
    "allow_install_title": "Разрешить установку",
    "allow_install_body": "Чтобы установить обновление, разрешите Offex Mail устанавливать неизвестные приложения, затем снова откройте обновление.",
    "open_settings": "Открыть настройки",
    "about_body1": "Offex Mail - бесплатный сервис временной почты. Создайте одноразовый ящик в один тап для OTP, ссылок подтверждения и тестовых писем - без регистрации и пароля.",
    "about_body2": "Каждый ящик автоматически истекает через некоторое время. Ничего не хранится вечно, и вам никогда не нужно давать свою настоящую почту.",
    "about_version": "Версия 3.9",
    "contact_title": "Связаться с нами",
    "contact_sub": "Есть вопрос или предложение? Напишите нам - мы быстро отвечаем.",
    "contact_support_label": "Почта поддержки",
    "contact_send_email": "Отправить письмо",
    "contact_website_label": "Сайт",
    "contact_open_website": "Открыть сайт",
    "splash_loading": "Загрузка...",
    "item_mail_label": "ПИСЬМО",
    "admin_sub": "Отправьте баннер-объявление, рекламу и запрос обновления на все установленные устройства.",
    "admin_announcement": "Объявление",
    "admin_show_banner": "Показать баннер в приложении",
    "admin_banner_hint": "Текст баннера",
    "admin_ads": "Реклама",
    "admin_enable_ads": "Включить рекламу AdMob",
    "admin_app_update": "Обновление приложения",
    "admin_latest_hint": "Последняя версия (напр. 3.9)",
    "admin_url_hint": "URL загрузки",
    "admin_force": "Принудительное обновление (блокировать старую версию)",
    "admin_save": "Сохранить",
    "admin_stats_prefix": "Ящики: %1$d   Письма: %2$d",
    "menu_title": "Ещё",
    "menu_chat_support": "Чат поддержки",
    "menu_about": "О Offex Mail",
    "menu_rate": "Оценить",
    "menu_privacy": "Политика конфиденциальности",
    "menu_terms": "Условия использования",
    "menu_contact": "Связаться с нами",
    "menu_language": "Язык",
    "menu_theme": "Тема: %1$s",
    "menu_theme_dark": "Тёмная",
    "menu_theme_light": "Светлая",
    "menu_notif": "Уведомления: %1$s",
    "menu_on": "ВКЛ",
    "menu_off": "ВЫКЛ",
    "menu_sound": "Звук уведомления: %1$s",
    "menu_sound_title": "Звук уведомления",
    "menu_done": "Готово",
    "lang_title": "Выберите язык",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

AR = {
    "tagline": "بريد مؤقت - صندوق فوري",
    "ob1_title": "صندوق مؤقت فوري",
    "ob1_body": "احصل على صندوق خاص لمرة واحدة بلمسة واحدة - لرموز OTP وروابط التحقق ورسائل الاختبار.",
    "ob2_title": "تنبيهات البريد الجديد",
    "ob2_body": "يواصل التطبيق الفحص في الخلفية، لذلك يصلك تنبيه فور وصول بريد جديد.",
    "ob3_title": "مجاني - بدون تسجيل",
    "ob3_body": "بدون حساب وبدون كلمة مرور. ينتهي كل صندوق تلقائيا بعد فترة.",
    "ob4_title": "بريدك بطريقتك",
    "ob4_body": "اختر اسما والنطاق الذي تحبه قبل إنشاء صندوقك.",
    "ob5_title": "وصول سريع إلى الصندوق",
    "ob5_body": "تنقل بين الصناديق المحفوظة واقرأ البريد الجديد فور وصوله.",
    "ob_next": "متابعة",
    "ob_start": "ابدأ",
    "ob_skip": "تخطي",
    "new_inbox": "صندوق جديد",
    "hint_name": "الاسم (اختياري)",
    "create_inbox": "إنشاء صندوق",
    "creating": "جارٍ الإنشاء...",
    "your_address": "عنوانك المؤقت",
    "copy": "نسخ",
    "refresh": "تحديث",
    "delete": "حذف",
    "copied": "تم نسخ العنوان",
    "messages": "الرسائل",
    "inbox_title": "الصندوق",
    "switch_title": "تبديل البريد",
    "choose_email": "اختر عنوان بريدك",
    "create_new_email": "إنشاء بريد جديد",
    "nav_email": "البريد",
    "nav_inbox": "الصندوق",
    "nav_switch": "تبديل",
    "nav_more": "المزيد",
    "message_label": "رسالة",
    "history": "السجل",
    "history_empty": "ستظهر صناديقك السابقة هنا. اضغط على أي منها للعودة إليه.",
    "no_messages": "لا يوجد بريد بعد. الصق هذا العنوان حيث تحتاجه وسيصل البريد هنا.",
    "notif_on": "الإشعارات",
    "notif_channel": "بريد جديد",
    "admin": "لوحة المسؤول",
    "admin_hint": "رمز المسؤول",
    "unlock": "فتح",
    "wrong_code": "رمز خاطئ",
    "expires_in": "ينتهي خلال",
    "version": "الإصدار",
    "notif_service": "المزامنة في الخلفية",
    "features_title": "لماذا Offex Mail",
    "features_sub": "كل ما تحتاجه من صندوق مؤقت",
    "feat1_t": "صندوق فوري",
    "feat1_d": "عنوان خاص بلمسة واحدة - بدون تسجيل أو كلمة مرور.",
    "feat2_t": "كشف OTP تلقائيا",
    "feat2_d": "نكتشف رمز التحقق وننسخه بلمسة واحدة.",
    "feat3_t": "روابط التحقق",
    "feat3_d": "تُفتح الروابط مباشرة في المتصفح لتأكيد سريع.",
    "feat4_t": "تنبيهات البريد الجديد",
    "feat4_d": "نخبرك فور وصول البريد، حتى في الخلفية.",
    "feat5_t": "نطاقات مخصصة",
    "feat5_d": "اختر اسما والنطاق الذي تحبه قبل البدء.",
    "feat6_t": "انتهاء تلقائي",
    "feat6_d": "تُنظّف الصناديق نفسها - لا شيء يُحفظ للأبد.",
    "otp_found": "رمز التحقق",
    "copy_code": "نسخ الرمز",
    "code_copied": "تم نسخ الرمز",
    "support_title": "دعم الدردشة",
    "support_sub": "حدثت مشكلة؟ اكتب رسالتك وأرسلها - نراها في اللوحة ونساعدك بسرعة.",
    "support_greeting": "مرحبا! أخبرنا بما حدث واضغط إرسال. تصل رسالتك إلى فريقنا فورا.",
    "support_hint": "اكتب رسالتك…",
    "support_send": "إرسال",
    "support_retry": "إعادة المحاولة",
    "support_sending": "جارٍ الإرسال…",
    "support_sent": "تم الإرسال ✓",
    "support_failed": "تعذر الإرسال: ",
    "support_empty": "اكتب رسالتك أولا",
    "support_contact": "تواصل مع الدعم",
    "support_error_title": "حدث خطأ ما",
    "notif_gate_title": "الإشعارات مطلوبة",
    "notif_gate_body": "يعتمد Offex Mail كليا على الإشعارات: نخبرك فور وصول بريد جديد أو OTP. لا يمكن استخدام التطبيق دون السماح بالإشعارات. اضغط السماح بالإشعارات واختر السماح للمتابعة.",
    "notif_gate_allow": "السماح بالإشعارات",
    "notif_gate_settings": "فتح الإعدادات",
    "feature_whats_new": "الجديد",
    "feature_ok": "فهمت",
    "domain_random": "عشوائي (تلقائي)",
    "toast_inbox_ready": "الصندوق جاهز",
    "toast_inbox_deleted": "تم حذف الصندوق",
    "toast_saved": "تم الحفظ",
    "err_network": "خطأ في الشبكة",
    "support_prefill_error": "ظهر لي هذا الخطأ: %1$s",
    "dlg_dismiss": "إغلاق",
    "dlg_later": "لاحقا",
    "update_title": "يتوفر تحديث",
    "update_message": "أصبح Offex Mail %1$s متاحا. حدّث للحصول على الميزات الجديدة.",
    "update_now": "حدّث الآن",
    "sponsored": "برعاية",
    "updater_title": "تحديث Offex Mail",
    "updater_desc": "جارٍ تنزيل الإصدار الجديد",
    "updater_starting": "بدء التنزيل...",
    "updater_downloading_title": "تنزيل التحديث",
    "updater_progress": "جارٍ التنزيل... %1$d%%",
    "updater_failed": "فشل التنزيل. حاول مرة أخرى.",
    "allow_install_title": "السماح بالتثبيت",
    "allow_install_body": "لتثبيت التحديث، اسمح لـ Offex Mail بتثبيت تطبيقات غير معروفة، ثم افتح التحديث مرة أخرى.",
    "open_settings": "فتح الإعدادات",
    "about_body1": "Offex Mail خدمة بريد مؤقت مجانية. أنشئ صندوقا لمرة واحدة بلمسة واحدة لرموز OTP وروابط التحقق ورسائل الاختبار - بدون تسجيل أو كلمة مرور.",
    "about_body2": "ينتهي كل صندوق تلقائيا بعد فترة. لا شيء يُحفظ للأبد، ولا تحتاج أبدا لمشاركة بريدك الحقيقي.",
    "about_version": "الإصدار 3.9",
    "contact_title": "تواصل معنا",
    "contact_sub": "هل لديك سؤال أو اقتراح؟ راسلنا - نرد بسرعة.",
    "contact_support_label": "بريد الدعم",
    "contact_send_email": "إرسال بريد",
    "contact_website_label": "الموقع",
    "contact_open_website": "فتح الموقع",
    "splash_loading": "جارٍ التحميل...",
    "item_mail_label": "بريد",
    "admin_sub": "أرسل لافتة الإعلان والإعلانات ومطالبة التحديث إلى كل جهاز مثبّت.",
    "admin_announcement": "إعلان",
    "admin_show_banner": "إظهار اللافتة في التطبيق",
    "admin_banner_hint": "نص اللافتة",
    "admin_ads": "الإعلانات",
    "admin_enable_ads": "تفعيل إعلانات AdMob",
    "admin_app_update": "تحديث التطبيق",
    "admin_latest_hint": "أحدث إصدار (مثل 3.9)",
    "admin_url_hint": "رابط التنزيل",
    "admin_force": "تحديث إجباري (حجب الإصدار القديم)",
    "admin_save": "حفظ",
    "admin_stats_prefix": "الصناديق: %1$d   الرسائل: %2$d",
    "menu_title": "المزيد",
    "menu_chat_support": "دعم الدردشة",
    "menu_about": "حول Offex Mail",
    "menu_rate": "قيّمنا",
    "menu_privacy": "سياسة الخصوصية",
    "menu_terms": "شروط الاستخدام",
    "menu_contact": "تواصل معنا",
    "menu_language": "اللغة",
    "menu_theme": "المظهر: %1$s",
    "menu_theme_dark": "داكن",
    "menu_theme_light": "فاتح",
    "menu_notif": "الإشعارات: %1$s",
    "menu_on": "مفعّل",
    "menu_off": "متوقف",
    "menu_sound": "صوت الإشعار: %1$s",
    "menu_sound_title": "صوت الإشعار",
    "menu_done": "تم",
    "lang_title": "اختر اللغة",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

IN = {
    "tagline": "Email sementara - inbox instan",
    "ob1_title": "Inbox sekali pakai instan",
    "ob1_body": "Dapatkan inbox pribadi sekali pakai dengan satu ketukan - untuk OTP, tautan verifikasi dan email uji.",
    "ob2_title": "Notifikasi email baru",
    "ob2_body": "Aplikasi terus memeriksa di latar belakang, jadi kamu dapat notifikasi begitu email baru masuk.",
    "ob3_title": "Gratis - tanpa daftar",
    "ob3_body": "Tanpa akun, tanpa kata sandi. Setiap inbox kedaluwarsa sendiri setelah beberapa saat.",
    "ob4_title": "Emailmu, caramu",
    "ob4_body": "Pilih nama dan domain yang kamu suka sebelum inbox dibuat.",
    "ob5_title": "Akses inbox cepat",
    "ob5_body": "Beralih antar inbox tersimpan dan baca email baru begitu masuk.",
    "ob_next": "Lanjut",
    "ob_start": "Mulai",
    "ob_skip": "Lewati",
    "new_inbox": "Inbox baru",
    "hint_name": "Nama (opsional)",
    "create_inbox": "Buat inbox",
    "creating": "Membuat...",
    "your_address": "Alamat sementaramu",
    "copy": "Salin",
    "refresh": "Muat ulang",
    "delete": "Hapus",
    "copied": "Alamat disalin",
    "messages": "Pesan",
    "inbox_title": "Inbox",
    "switch_title": "Ganti email",
    "choose_email": "Pilih alamat emailmu",
    "create_new_email": "Buat email baru",
    "nav_email": "Email",
    "nav_inbox": "Inbox",
    "nav_switch": "Ganti",
    "nav_more": "Lainnya",
    "message_label": "PESAN",
    "history": "Riwayat",
    "history_empty": "Inbox lamamu akan muncul di sini. Ketuk salah satu untuk kembali.",
    "no_messages": "Belum ada email. Tempel alamat ini di mana pun kamu perlu dan email akan masuk ke sini.",
    "notif_on": "Notifikasi",
    "notif_channel": "Email baru",
    "admin": "Panel admin",
    "admin_hint": "Kode admin",
    "unlock": "Buka",
    "wrong_code": "Kode salah",
    "expires_in": "Kedaluwarsa dalam",
    "version": "Versi",
    "notif_service": "Sinkronisasi latar belakang",
    "features_title": "Kenapa Offex Mail",
    "features_sub": "Semua yang kamu butuhkan dari inbox sementara",
    "feat1_t": "Inbox instan",
    "feat1_d": "Alamat pribadi dengan satu ketukan - tanpa daftar, tanpa kata sandi.",
    "feat2_t": "Deteksi OTP otomatis",
    "feat2_d": "Kami menemukan kode verifikasi dan menyalinnya dengan satu ketukan.",
    "feat3_t": "Tautan verifikasi",
    "feat3_d": "Tautan terbuka langsung di browser agar kamu cepat konfirmasi.",
    "feat4_t": "Peringatan email baru",
    "feat4_d": "Kami beri tahu begitu email masuk, bahkan di latar belakang.",
    "feat5_t": "Domain khusus",
    "feat5_d": "Pilih nama dan domain yang kamu suka sebelum mulai.",
    "feat6_t": "Kedaluwarsa otomatis",
    "feat6_d": "Inbox membersihkan diri sendiri - tidak ada yang disimpan selamanya.",
    "otp_found": "KODE VERIFIKASI",
    "copy_code": "Salin kode",
    "code_copied": "Kode disalin",
    "support_title": "Dukungan Chat",
    "support_sub": "Ada masalah? Tulis pesanmu dan kirim - kami melihatnya di panel dan cepat membantu.",
    "support_greeting": "Hai! Ceritakan apa yang salah dan ketuk Kirim. Pesanmu langsung sampai ke tim kami.",
    "support_hint": "Tulis pesanmu…",
    "support_send": "Kirim",
    "support_retry": "Coba lagi",
    "support_sending": "Mengirim…",
    "support_sent": "Terkirim ✓",
    "support_failed": "Gagal mengirim: ",
    "support_empty": "Tulis dulu pesanmu",
    "support_contact": "Hubungi dukungan",
    "support_error_title": "Terjadi kesalahan",
    "notif_gate_title": "Notifikasi wajib",
    "notif_gate_body": "Seluruh kerja Offex Mail bergantung pada notifikasi: kami beri tahu begitu email baru atau OTP masuk. Tanpa mengizinkan notifikasi aplikasi tidak bisa dipakai. Ketuk Izinkan notifikasi dan pilih Izinkan untuk melanjutkan.",
    "notif_gate_allow": "Izinkan notifikasi",
    "notif_gate_settings": "Buka pengaturan",
    "feature_whats_new": "Apa yang baru",
    "feature_ok": "Mengerti",
    "domain_random": "Acak (otomatis)",
    "toast_inbox_ready": "Inbox siap",
    "toast_inbox_deleted": "Inbox dihapus",
    "toast_saved": "Tersimpan",
    "err_network": "kesalahan jaringan",
    "support_prefill_error": "Saya kena error ini: %1$s",
    "dlg_dismiss": "Tutup",
    "dlg_later": "Nanti",
    "update_title": "Pembaruan tersedia",
    "update_message": "Offex Mail %1$s sudah hadir. Perbarui untuk fitur baru.",
    "update_now": "Perbarui sekarang",
    "sponsored": "Bersponsor",
    "updater_title": "Pembaruan Offex Mail",
    "updater_desc": "Mengunduh versi baru",
    "updater_starting": "Memulai unduhan...",
    "updater_downloading_title": "Mengunduh pembaruan",
    "updater_progress": "Mengunduh... %1$d%%",
    "updater_failed": "Unduhan gagal. Coba lagi.",
    "allow_install_title": "Izinkan instalasi",
    "allow_install_body": "Untuk memasang pembaruan, izinkan Offex Mail memasang aplikasi tak dikenal, lalu buka pembaruan lagi.",
    "open_settings": "Buka pengaturan",
    "about_body1": "Offex Mail adalah layanan email sementara gratis. Buat inbox sekali pakai dengan satu ketukan untuk OTP, tautan verifikasi dan email uji - tanpa daftar, tanpa kata sandi.",
    "about_body2": "Setiap inbox kedaluwarsa otomatis setelah beberapa saat. Tidak ada yang disimpan selamanya, dan kamu tak perlu membagikan email aslimu.",
    "about_version": "Versi 3.9",
    "contact_title": "Hubungi kami",
    "contact_sub": "Ada masalah, pertanyaan atau saran? Hubungi kami - kami cepat membalas.",
    "contact_support_label": "Email dukungan",
    "contact_send_email": "Kirim email",
    "contact_website_label": "Situs web",
    "contact_open_website": "Buka situs web",
    "splash_loading": "Memuat...",
    "item_mail_label": "EMAIL",
    "admin_sub": "Kirim banner pengumuman, iklan dan perintah pembaruan ke setiap perangkat terpasang.",
    "admin_announcement": "Pengumuman",
    "admin_show_banner": "Tampilkan banner di aplikasi",
    "admin_banner_hint": "Pesan banner",
    "admin_ads": "Iklan",
    "admin_enable_ads": "Aktifkan iklan AdMob",
    "admin_app_update": "Pembaruan aplikasi",
    "admin_latest_hint": "Versi terbaru (mis. 3.9)",
    "admin_url_hint": "URL unduhan",
    "admin_force": "Paksa pembaruan (blokir aplikasi lama)",
    "admin_save": "Simpan",
    "admin_stats_prefix": "Inbox: %1$d   Email: %2$d",
    "menu_title": "Lainnya",
    "menu_chat_support": "Dukungan Chat",
    "menu_about": "Tentang Offex Mail",
    "menu_rate": "Beri nilai",
    "menu_privacy": "Kebijakan Privasi",
    "menu_terms": "Ketentuan Penggunaan",
    "menu_contact": "Hubungi kami",
    "menu_language": "Bahasa",
    "menu_theme": "Tema: %1$s",
    "menu_theme_dark": "Gelap",
    "menu_theme_light": "Terang",
    "menu_notif": "Notifikasi: %1$s",
    "menu_on": "AKTIF",
    "menu_off": "MATI",
    "menu_sound": "Suara notifikasi: %1$s",
    "menu_sound_title": "Suara notifikasi",
    "menu_done": "Selesai",
    "lang_title": "Pilih bahasa",
    "lang_en": "English",
    "lang_hi": "Hinglish",
    "lang_es": "Espanol",
    "lang_pt": "Portugues",
    "lang_ar": "العربية",
    "lang_ru": "Русский",
    "lang_in": "Bahasa Indonesia",
}

LOCALES = [("hi", HI), ("es", ES), ("pt", PT), ("ar", AR), ("ru", RU), ("in", IN)]

SOUND_NAMES_EN = ["Chime", "Ding", "Pop"]
SOUND_NAMES = {
    "hi": ["Chime", "Ding", "Pop"],
    "es": ["Campanilla", "Timbre", "Pop"],
    "pt": ["Campainha", "Sino", "Pop"],
    "ar": ["رنين", "دينغ", "بوب"],
    "ru": ["Звон", "Динь", "Поп"],
    "in": ["Lonceng", "Ding", "Pop"],
}

# ===========================================================================
# 3 : strings.xml -- add new English keys + sound_names array
# ===========================================================================
sp = RES + "/values/strings.xml"
s = R(sp)
block = ""
for k, v in NEW_EN:
    if ('name="%s"' % k) not in s:
        block += '    <string name="%s">%s</string>\n' % (k, xml_escape(v))
if 'name="sound_names"' not in s:
    block += ('    <string-array name="sound_names">\n'
              + "".join('        <item>%s</item>\n' % x for x in SOUND_NAMES_EN)
              + '    </string-array>\n')
if block:
    s = s.replace("</resources>", block + "</resources>")
    W(sp, s)
    print("V: strings.xml -> new v3.9 keys + sound array")

# master key -> raw (already-escaped) English value
master = {}
for m in re.finditer(r'<string name="([^"]+)">(.*?)</string>', s, re.S):
    master[m.group(1)] = m.group(2)

# ===========================================================================
# 4 : locale resource files
# ===========================================================================
for code, tr in LOCALES:
    lines = ['<?xml version="1.0" encoding="utf-8"?>', "<resources>"]
    for k in master:
        if k in tr:
            lines.append('    <string name="%s">%s</string>' % (k, xml_escape(tr[k])))
        else:
            lines.append('    <string name="%s">%s</string>' % (k, master[k]))
    names = SOUND_NAMES.get(code, SOUND_NAMES_EN)
    lines.append('    <string-array name="sound_names">')
    for x in names:
        lines.append("        <item>%s</item>" % xml_escape(x))
    lines.append("    </string-array>")
    lines.append("</resources>")
    W(RES + "/values-%s/strings.xml" % code, "\n".join(lines) + "\n")
    print("V: values-%s/strings.xml written" % code)

# ===========================================================================
# 5 : LocaleHelper.java + BaseActivity.java
# ===========================================================================
LOCALE_HELPER = r'''package online.mytempmail.app;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.res.Configuration;
import android.os.Build;
import java.util.Locale;

/**
 * v3.9 - multi-language support. Persists the chosen language in
 * SharedPreferences ("offex") and applies it everywhere by wrapping the
 * Activity base context (works on every API level, not just API 33+).
 */
public class LocaleHelper {
    // Supported languages. "en" is the default; "hi" carries natural roman
    // Hinglish strings (values-hi). Order matches the switcher list.
    public static final String[] CODES = {"en", "hi", "es", "pt", "ar", "ru", "in"};
    public static final int[] LABELS = {
        R.string.lang_en, R.string.lang_hi, R.string.lang_es,
        R.string.lang_pt, R.string.lang_ar, R.string.lang_ru, R.string.lang_in
    };

    private static SharedPreferences sp(Context c){
        return c.getSharedPreferences("offex", Context.MODE_PRIVATE);
    }

    public static String current(Context c){
        try { String v = sp(c).getString("lang", ""); return v == null ? "" : v; }
        catch(Exception e){ return ""; }
    }

    public static void set(Context c, String code){
        try { sp(c).edit().putString("lang", code == null ? "" : code).apply(); }
        catch(Exception e){}
    }

    // The locale actually in use: the saved choice, else the device locale if
    // we support it, else English.
    public static Locale locale(Context c){
        String code = current(c);
        if(code == null || code.isEmpty()){
            try {
                Locale d = Locale.getDefault();
                String dc = (d == null) ? "" : d.getLanguage();
                for(String s : CODES) if(s.equals(dc)) return d;
            } catch(Exception e){}
            return new Locale("en");
        }
        return new Locale(code);
    }

    public static int index(Context c){
        String code = current(c);
        for(int i = 0; i < CODES.length; i++) if(CODES[i].equals(code)) return i;
        return 0;
    }

    // Wrap a context so its resources resolve in the chosen language.
    public static Context wrap(Context c){
        try {
            Locale l = locale(c);
            Locale.setDefault(l);
            Configuration cfg = new Configuration(c.getResources().getConfiguration());
            cfg.setLocale(l);
            cfg.setLayoutDirection(l);
            return c.createConfigurationContext(cfg);
        } catch(Exception e){
            return c;
        }
    }
}
'''
W(J + "/LocaleHelper.java", LOCALE_HELPER)
print("V: LocaleHelper.java written")

BASE_ACTIVITY = r'''package online.mytempmail.app;
import android.app.Activity;
import android.content.Context;

/**
 * v3.9 - base Activity that applies the user's chosen language to the whole
 * screen (resources + layout direction) before the layout is inflated.
 */
public class BaseActivity extends Activity {
    @Override protected void attachBaseContext(Context base){
        super.attachBaseContext(LocaleHelper.wrap(base));
    }
}
'''
W(J + "/BaseActivity.java", BASE_ACTIVITY)
print("V: BaseActivity.java written")

# Route every Activity through BaseActivity so the chosen locale is applied.
for name in ["SplashActivity", "MainActivity", "OnboardingActivity", "ReaderActivity",
             "AboutActivity", "ContactActivity", "SupportActivity", "AdminActivity"]:
    p = J + "/" + name + ".java"
    if not os.path.exists(p):
        continue
    s = R(p)
    if ("class %s extends Activity" % name) in s:
        s = s.replace("class %s extends Activity" % name,
                      "class %s extends BaseActivity" % name, 1)
        W(p, s)
        print("V: %s -> extends BaseActivity" % name)

# ===========================================================================
# 6 : Menu.java -- resource strings + Language switcher
# ===========================================================================
MENU = r'''package online.mytempmail.app;
import android.app.Activity;
import android.app.AlertDialog;
import android.content.Intent;
import android.net.Uri;
import android.widget.Toast;
public class Menu {
    public static void open(final Activity a){
        final String theme = a.getString(R.string.menu_theme,
                a.getString(Prefs.isDark() ? R.string.menu_theme_dark : R.string.menu_theme_light));
        final String notif = a.getString(R.string.menu_notif,
                a.getString(Prefs.notifyOn() ? R.string.menu_on : R.string.menu_off));
        final String[] snd = soundNames(a);
        final String sound = a.getString(R.string.menu_sound, snd[Notifier.soundIndex()]);
        final String[] items = {
            a.getString(R.string.menu_chat_support),
            a.getString(R.string.menu_about),
            a.getString(R.string.menu_rate),
            a.getString(R.string.menu_privacy),
            a.getString(R.string.menu_terms),
            a.getString(R.string.menu_contact),
            a.getString(R.string.menu_language),
            sound, theme, notif
        };
        new AlertDialog.Builder(a)
            .setTitle(a.getString(R.string.menu_title))
            .setItems(items, (d,w)->{
                try {
                    if(w==0) a.startActivity(new Intent(a, SupportActivity.class));
                    else if(w==1) a.startActivity(new Intent(a, AboutActivity.class));
                    else if(w==2) openUrl(a,"https://play.google.com/store/apps/details?id=online.mytempmail.app");
                    else if(w==3) openUrl(a,"https://mytemp-mail.online/privacy");
                    else if(w==4) openUrl(a,"https://mytemp-mail.online/terms");
                    else if(w==5) a.startActivity(new Intent(a, ContactActivity.class));
                    else if(w==6) pickLanguage(a);
                    else if(w==7) pickSound(a);
                    else if(w==8) { Prefs.setThemeMode(Prefs.isDark() ? "light" : "dark"); a.recreate(); }
                    else {
                        Prefs.setNotify(!Prefs.notifyOn());
                        if(Prefs.notifyOn()) Notifier.ensure(a);
                        Toast.makeText(a, a.getString(R.string.menu_notif,
                                a.getString(Prefs.notifyOn() ? R.string.menu_on : R.string.menu_off)),
                                Toast.LENGTH_SHORT).show();
                    }
                } catch(Exception e){}
            })
            .show();
    }

    private static String[] soundNames(Activity a){
        try {
            String[] v = a.getResources().getStringArray(R.array.sound_names);
            if(v != null && v.length == Notifier.SND_NAMES.length) return v;
        } catch(Exception e){}
        return Notifier.SND_NAMES;
    }

    private static void pickLanguage(final Activity a){
        try {
            final String[] codes = LocaleHelper.CODES;
            final String[] labels = new String[codes.length];
            for(int i = 0; i < codes.length; i++) labels[i] = a.getString(LocaleHelper.LABELS[i]);
            new AlertDialog.Builder(a)
                .setTitle(a.getString(R.string.lang_title))
                .setSingleChoiceItems(labels, LocaleHelper.index(a), (d,w)->{
                    LocaleHelper.set(a, codes[w]);
                    try { d.dismiss(); } catch(Exception e){}
                    try { a.recreate(); } catch(Exception e){}
                })
                .setNegativeButton(a.getString(R.string.dlg_dismiss), (d,w)->{})
                .show();
        } catch(Exception e){}
    }

    private static void pickSound(final Activity a){
        try {
            new AlertDialog.Builder(a)
                .setTitle(a.getString(R.string.menu_sound_title))
                .setSingleChoiceItems(soundNames(a), Notifier.soundIndex(), (d,w)->{ Prefs.setNotifSound(w); Notifier.preview(a, w); })
                .setPositiveButton(a.getString(R.string.menu_done), (d,w)->{})
                .show();
        } catch(Exception e){}
    }

    private static void openUrl(Activity a,String url){
        try { a.startActivity(new Intent(Intent.ACTION_VIEW, Uri.parse(url))); } catch(Exception e){}
    }
}
'''
W(J + "/Menu.java", MENU)
print("V: Menu.java rewritten (resource strings + language switcher)")

# ===========================================================================
# 7 : Java hardcoded string replacements
# ===========================================================================
# MainActivity.java
p = J + "/MainActivity.java"; s = R(p)
s = rep(s, 'domains.add("Random (auto)");',
        'domains.add(getString(R.string.domain_random));', "MainActivity domain_random")
s = rep(s, 'Toast.makeText(this,"Inbox ready",Toast.LENGTH_SHORT).show();',
        'Toast.makeText(this,getString(R.string.toast_inbox_ready),Toast.LENGTH_SHORT).show();', "MainActivity inbox_ready")
s = rep(s, '(e.getMessage()==null) ? "network error" : e.getMessage();',
        '(e.getMessage()==null) ? getString(R.string.err_network) : e.getMessage();', "MainActivity err_network")
s = rep(s, 'si.putExtra("prefill", "I hit this error: "+em);',
        'si.putExtra("prefill", getString(R.string.support_prefill_error, em));', "MainActivity prefill")
s = rep(s, '.setNegativeButton("Dismiss", (d,w)->{})',
        '.setNegativeButton(getString(R.string.dlg_dismiss), (d,w)->{})', "MainActivity dismiss")
s = rep(s, 'Toast.makeText(this,"Inbox deleted",Toast.LENGTH_SHORT).show();',
        'Toast.makeText(this,getString(R.string.toast_inbox_deleted),Toast.LENGTH_SHORT).show();', "MainActivity inbox_deleted")
W(p, s); print("V: MainActivity.java strings -> resources")

# Config.java (update prompt)
p = J + "/Config.java"; s = R(p)
s = rep(s, 'b.setTitle("Update available");', 'b.setTitle(a.getString(R.string.update_title));', "Config update_title")
s = rep(s, 'b.setMessage("Offex Mail " + latest + " aa gaya hai. Naye features ke liye update karo.");',
        'b.setMessage(a.getString(R.string.update_message, latest));', "Config update_message")
s = rep(s, 'b.setPositiveButton("Update now",', 'b.setPositiveButton(a.getString(R.string.update_now),', "Config update_now")
s = rep(s, 'if(!force) b.setNegativeButton("Later", (d, w) -> {});',
        'if(!force) b.setNegativeButton(a.getString(R.string.dlg_later), (d, w) -> {});', "Config later")
W(p, s); print("V: Config.java update prompt -> resources")

# Ads.java (native "Sponsored")
p = J + "/Ads.java"; s = R(p)
if 'label.setText("Sponsored");' in s:
    s = s.replace('label.setText("Sponsored");', 'label.setText(a.getString(R.string.sponsored));', 1)
    W(p, s); print("V: Ads.java sponsored -> resource")

# Updater.java
p = J + "/Updater.java"; s = R(p)
s = rep(s, 'req.setTitle("Offex Mail update");', 'req.setTitle(a.getString(R.string.updater_title));', "Updater title")
s = rep(s, 'req.setDescription("Downloading the new version");', 'req.setDescription(a.getString(R.string.updater_desc));', "Updater desc")
s = rep(s, 'pct.setText("Starting download...");', 'pct.setText(a.getString(R.string.updater_starting));', "Updater starting")
s = rep(s, '.setTitle("Downloading update")', '.setTitle(a.getString(R.string.updater_downloading_title))', "Updater dl title")
s = rep(s, 'pct.setText("Downloading... " + p + "%");', 'pct.setText(a.getString(R.string.updater_progress, p));', "Updater progress")
s = rep(s, 'Toast.makeText(a, "Download failed. Please try again.", Toast.LENGTH_LONG).show();',
        'Toast.makeText(a, a.getString(R.string.updater_failed), Toast.LENGTH_LONG).show();', "Updater failed")
s = rep(s, '.setTitle("Allow install")', '.setTitle(a.getString(R.string.allow_install_title))', "Updater allow title")
s = rep(s, '.setMessage("To install the update, allow Offex Mail to install unknown apps, then open the update again.")',
        '.setMessage(a.getString(R.string.allow_install_body))', "Updater allow body")
s = rep(s, '.setPositiveButton("Open settings", (d,w)->{', '.setPositiveButton(a.getString(R.string.open_settings), (d,w)->{', "Updater open settings")
s = rep(s, '.setNegativeButton("Later", (d,w)->{})', '.setNegativeButton(a.getString(R.string.dlg_later), (d,w)->{})', "Updater later")
W(p, s); print("V: Updater.java strings -> resources")

# AdminActivity.java
p = J + "/AdminActivity.java"; s = R(p)
s = rep(s, 'statsText.setText("Inboxes: "+st.optInt("inboxes")+"   Mails: "+st.optInt("messages"));',
        'statsText.setText(getString(R.string.admin_stats_prefix, st.optInt("inboxes"), st.optInt("messages")));', "Admin stats")
s = rep(s, 'Toast.makeText(this,"Saved",Toast.LENGTH_SHORT).show());',
        'Toast.makeText(this,getString(R.string.toast_saved),Toast.LENGTH_SHORT).show());', "Admin saved")
W(p, s); print("V: AdminActivity.java strings -> resources")

# ===========================================================================
# 8 : XML hardcoded string replacements
# ===========================================================================
def swap(path, pairs):
    s = R(path)
    for old, new, nm in pairs:
        if old in s:
            s = s.replace(old, new)
        else:
            print("V: note - %s anchor not found (%s)" % (os.path.basename(path), nm))
    W(path, s)
    print("V: %s localised" % os.path.basename(path))

swap(LAY + "/activity_about.xml", [
    ('android:text="Offex Mail is a free temporary email service. Create a disposable inbox in one tap for OTPs, verification links and test emails - no signup, no password."', 'android:text="@string/about_body1"', "about_body1"),
    ('android:text="Every inbox expires automatically after a while. Nothing is kept forever, and you never have to share your real email address."', 'android:text="@string/about_body2"', "about_body2"),
    ('android:text="Version 3.8"', 'android:text="@string/about_version"', "about_version"),
])

swap(LAY + "/activity_contact.xml", [
    ('android:text="Contact us"', 'android:text="@string/contact_title"', "contact_title"),
    ('android:text="Koi dikkat, sawal ya suggestion? Hum se rabta karo - hum jaldi reply karte hain."', 'android:text="@string/contact_sub"', "contact_sub"),
    ('android:text="Support email"', 'android:text="@string/contact_support_label"', "contact_support_label"),
    ('android:text="Send email"', 'android:text="@string/contact_send_email"', "contact_send_email"),
    ('android:text="Website"', 'android:text="@string/contact_website_label"', "contact_website_label"),
    ('android:text="Open website"', 'android:text="@string/contact_open_website"', "contact_open_website"),
])

swap(LAY + "/activity_splash.xml", [
    ('android:text="Loading..."', 'android:text="@string/splash_loading"', "splash_loading"),
])

swap(LAY + "/item_message.xml", [
    ('android:text="MAIL"', 'android:text="@string/item_mail_label"', "item_mail_label"),
])

swap(LAY + "/activity_admin.xml", [
    ('android:text="Push the announcement banner, ads and update prompt to every installed device."', 'android:text="@string/admin_sub"', "admin_sub"),
    ('android:text="Announcement"', 'android:text="@string/admin_announcement"', "admin_announcement"),
    ('android:text="Show banner in app"', 'android:text="@string/admin_show_banner"', "admin_show_banner"),
    ('android:hint="Banner message"', 'android:hint="@string/admin_banner_hint"', "admin_banner_hint"),
    ('android:text="Ads"', 'android:text="@string/admin_ads"', "admin_ads"),
    ('android:text="Enable AdMob ads"', 'android:text="@string/admin_enable_ads"', "admin_enable_ads"),
    ('android:text="App update"', 'android:text="@string/admin_app_update"', "admin_app_update"),
    ('android:hint="Latest version (e.g. 3.1)"', 'android:hint="@string/admin_latest_hint"', "admin_latest_hint"),
    ('android:hint="Download URL"', 'android:hint="@string/admin_url_hint"', "admin_url_hint"),
    ('android:text="Force update (block old app)"', 'android:text="@string/admin_force"', "admin_force"),
    ('android:text="Save"', 'android:text="@string/admin_save"', "admin_save"),
])

# ===========================================================================
# 9 : Install.java -- launch/install analytics report
# ===========================================================================
INSTALL = r'''package online.mytempmail.app;
import android.content.Context;
import android.content.SharedPreferences;
import android.content.pm.PackageInfo;
import android.os.Build;
import org.json.JSONObject;
import java.util.Locale;
import java.util.UUID;

/**
 * v3.9 - app install / usage analytics. Generates a stable install id once,
 * persists it, and reports device + build details to POST /api/app/install on
 * every launch (upserted by install_id) so the admin panel can show total
 * installs, active users and device/Android/app-version breakdowns.
 */
public class Install {
    private static SharedPreferences sp(Context c){
        return c.getSharedPreferences("offex", Context.MODE_PRIVATE);
    }

    public static String id(Context c){
        try {
            String v = sp(c).getString("install_id", "");
            if(v == null || v.trim().isEmpty()){
                v = UUID.randomUUID().toString();
                sp(c).edit().putString("install_id", v).apply();
            }
            return v;
        } catch(Exception e){ return ""; }
    }

    public static long firstSeen(Context c){
        try {
            long v = sp(c).getLong("install_first_seen", 0L);
            if(v <= 0){ v = System.currentTimeMillis() / 1000L; sp(c).edit().putLong("install_first_seen", v).apply(); }
            return v;
        } catch(Exception e){ return 0L; }
    }

    public static void report(final Context c){
        try {
            final Context app = c.getApplicationContext();
            new Thread(()->{
                try {
                    JSONObject b = new JSONObject();
                    b.put("install_id", id(app));
                    String mfr = Build.MANUFACTURER == null ? "" : Build.MANUFACTURER;
                    String model = Build.MODEL == null ? "" : Build.MODEL;
                    b.put("manufacturer", mfr);
                    b.put("model", model);
                    b.put("brand", Build.BRAND == null ? "" : Build.BRAND);
                    b.put("device", (mfr + " " + model).trim());
                    b.put("android_version", Build.VERSION.RELEASE == null ? "" : Build.VERSION.RELEASE);
                    b.put("sdk", Build.VERSION.SDK_INT);
                    try {
                        PackageInfo pi = app.getPackageManager().getPackageInfo(app.getPackageName(), 0);
                        b.put("app_version", pi.versionName == null ? "" : pi.versionName);
                        b.put("version_code", pi.versionCode);
                    } catch(Exception e){
                        b.put("app_version", SupportActivity.VERSION);
                        b.put("version_code", 0);
                    }
                    try {
                        Locale l = Locale.getDefault();
                        b.put("locale", l == null ? "" : l.toString());
                    } catch(Exception e){ b.put("locale", ""); }
                    try {
                        int wdp = app.getResources().getConfiguration().screenWidthDp;
                        int hdp = app.getResources().getConfiguration().screenHeightDp;
                        b.put("screen", wdp + "x" + hdp);
                    } catch(Exception e){ b.put("screen", ""); }
                    b.put("first_seen", firstSeen(app));
                    b.put("last_seen", System.currentTimeMillis() / 1000L);
                    ApiClient.post("/api/app/install", b.toString());
                } catch(Exception e){}
            }).start();
        } catch(Exception e){}
    }
}
'''
W(J + "/Install.java", INSTALL)
print("V: Install.java written")

# Wire the report into app launch (App.onCreate already registers FCM).
p = J + "/App.java"; s = R(p)
s = rep(s, 'Prefs.init(this); DeviceReg.register(this);',
        'Prefs.init(this); DeviceReg.register(this); Install.report(this);', "App install report")
W(p, s); print("V: App.java -> Install.report on launch")

# ===========================================================================
# 10 : AndroidManifest -- RTL support (for Arabic)
# ===========================================================================
mf = "android/app/src/main/AndroidManifest.xml"
s = R(mf)
if "supportsRtl" not in s:
    s = rep(s, '        android:name=".App"',
            '        android:name=".App"\n        android:supportsRtl="true"', "manifest supportsRtl")
    W(mf, s)
    print("V: manifest -> supportsRtl")

# ===========================================================================
# 11 : version 3.8 -> 3.9
# ===========================================================================
bp = "android/app/build.gradle"
s = R(bp)
s = re.sub(r"versionCode \d+", "versionCode 29", s)
s = re.sub(r'versionName "[^"]*"', 'versionName "3.9"', s)
W(bp, s)

cp = J + "/Config.java"; s = R(cp)
s = s.replace('latest.equals("3.8")', 'latest.equals("3.9")')
W(cp, s)

sup = J + "/SupportActivity.java"
if os.path.exists(sup):
    s = R(sup)
    s = s.replace('public static final String VERSION = "3.8";', 'public static final String VERSION = "3.9";')
    W(sup, s)

print("V: applied v3.9 (multi-language + language switcher + install analytics; version 3.8 -> 3.9)")
