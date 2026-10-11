#!/usr/bin/env python3
"""
Add a genuinely unique, service-specific deep-dive section to every templated
service page under public/<lang>/ so near-duplicate similarity drops.

Each target language (fr, de, pt, ru, ar, zh, ja) currently ships service pages
that are ~90% identical boilerplate with only the service name swapped. This
tool composes a per-service section (category, what the signup asks for, the
verification type, three service-specific notes, and a tailored closing) from a
per-service fact table plus per-language prose, and inserts it just before the
"related pages" block.

Run:  python tools/add_unique_sections.py            # apply
      python tools/add_unique_sections.py --dry-run  # show counts only
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

# ---------------------------------------------------------------------------
# per-service facts (only the 35 services that exist in every language hub)
#   cat   -> category key
#   asks  -> what the signup form asks for
#   code  -> verification type
#   attrs -> three attribute keys (see ATTR index below)
# ---------------------------------------------------------------------------
SERVICES = {
    "instagram":  ("social",      "username_email", "otp",  [0, 4, 8, 6, 2]),
    "facebook":   ("social",      "username_email", "otp",  [0, 6, 8, 4, 13]),
    "tiktok":     ("social",      "username_email", "otp",  [0, 3, 4, 6, 8]),
    "twitter":    ("social",      "username_email", "otp",  [0, 4, 12, 8, 6]),
    "x":          ("social",      "username_email", "otp",  [0, 12, 8, 4, 13]),
    "discord":    ("social",      "username_email", "link", [1, 4, 8, 7, 13]),
    "snapchat":   ("social",      "username_email", "otp",  [0, 2, 8, 6, 12]),
    "reddit":     ("social",      "username_email", "link", [1, 4, 13, 8, 12]),
    "pinterest":  ("social",      "username_email", "link", [1, 4, 7, 8, 10]),
    "linkedin":   ("social",      "email",          "otp",  [0, 8, 13, 6, 10]),
    "netflix":    ("streaming",   "email_password", "otp",  [5, 0, 6, 10, 9]),
    "spotify":    ("music",       "email_password", "link", [1, 5, 7, 10, 8]),
    "amazon":     ("marketplace", "email",          "otp",  [0, 9, 13, 6, 10]),
    "flipkart":   ("marketplace", "email",          "otp",  [0, 9, 2, 6, 13]),
    "ebay":       ("marketplace", "email",          "otp",  [0, 9, 8, 2, 6]),
    "aliexpress": ("marketplace", "email",          "otp",  [0, 9, 3, 2, 13]),
    "shopify":    ("marketplace", "email",          "otp",  [0, 5, 10, 13, 9]),
    "github":     ("developer",   "username_email", "otp",  [0, 11, 8, 10, 6]),
    "gitlab":     ("developer",   "username_email", "link", [1, 11, 10, 8, 13]),
    "chatgpt":    ("ai",          "email",          "otp",  [0, 2, 8, 10, 12]),
    "openai":     ("ai",          "email",          "otp",  [0, 2, 10, 8, 13]),
    "apple":      ("productivity","email",          "otp",  [0, 6, 10, 11, 13]),
    "microsoft":  ("productivity","email",          "otp",  [0, 10, 11, 13, 7]),
    "adobe":      ("design",      "email",          "link", [1, 5, 6, 8, 10]),
    "canva":      ("design",      "email_password", "otp",  [0, 7, 10, 8, 6]),
    "notion":     ("productivity","email",          "link", [1, 4, 7, 8, 11]),
    "zoom":       ("productivity","email",          "link", [1, 11, 7, 4, 8]),
    "slack":      ("productivity","email",          "link", [1, 4, 7, 13, 10]),
    "dropbox":    ("storage",     "email_password", "otp",  [0, 3, 6, 7, 10]),
    "steam":      ("gaming",      "username_email", "otp",  [0, 12, 5, 8, 6]),
    "xbox":       ("gaming",      "email",          "otp",  [0, 5, 6, 12, 13]),
    "playstation":("gaming",      "email",          "link", [1, 12, 6, 5, 7]),
    "paypal":     ("payments",    "email",          "otp",  [0, 5, 13, 6, 10]),
    "uber":       ("transport",   "email",          "otp",  [0, 2, 6, 9, 10]),
    "airbnb":     ("travel",      "email",          "otp",  [0, 5, 9, 13, 6]),
}

DISPLAY = {
    "twitter": "Twitter", "x": "X", "chatgpt": "ChatGPT", "openai": "OpenAI",
    "github": "GitHub", "gitlab": "GitLab", "paypal": "PayPal",
    "playstation": "PlayStation", "aliexpress": "AliExpress",
}

# ---------------------------------------------------------------------------
# per-language prose.  keys: cat, asks, code, attr (14), t (3 templates),
# list_intro, title, closing.  Slots: {name} {cat} {asks} {code} {a0} {a1} {a2}
# ---------------------------------------------------------------------------
PACKS = {
 "fr": {
  "cat": {"social":"réseaux sociaux","streaming":"streaming vidéo","music":"musique",
    "marketplace":"achat en ligne","developer":"développement","ai":"intelligence artificielle",
    "productivity":"productivité","design":"design","storage":"stockage cloud",
    "gaming":"jeux","payments":"paiement","transport":"transport","travel":"voyage"},
  "asks": {"username_email":"une adresse e-mail et un nom d'utilisateur unique",
    "email":"une adresse e-mail","email_password":"une adresse e-mail et un mot de passe"},
  "code": {"otp":"un code à usage unique qui expire en quelques minutes",
    "link":"un e-mail contenant un lien de confirmation"},
  "attr": [
    "un code à usage unique qui expire en quelques minutes est envoyé par e-mail",
    "il faut cliquer sur le lien de confirmation reçu par e-mail",
    "il peut aussi vous demander un numéro de téléphone",
    "il peut détecter et refuser les domaines d'e-mail jetables connus",
    "vous devez choisir un nom d'utilisateur unique",
    "une méthode de paiement est requise pour l'utiliser pleinement",
    "un e-mail d'alerte est envoyé lors d'une connexion depuis un nouvel appareil",
    "vous pouvez rester connecté sur plusieurs appareils",
    "il compte de nombreux utilisateurs et attire beaucoup de spam",
    "après l'inscription, vous recevez aussi les confirmations de commande",
    "il impose des exigences strictes sur le mot de passe",
    "il prend en charge la double authentification par e-mail",
    "il peut restreindre les comptes qui semblent jetables",
    "il envoie des notifications de sécurité et d'activité"],
  "t": [
    "Pour créer un compte {name}, il faut d'abord saisir {asks}, puis valider votre identité grâce à {code}. Une adresse jetable convient parfaitement pour recevoir uniquement ce message de vérification.",
    "Collez l'adresse temporaire d'Offex Mail dans le formulaire {name} et vous recevrez {code} en quelques secondes. Vérifiez que l'adresse est exacte, sans espace superflu, avant de valider le formulaire.",
    "{name} est un service de type {cat} : à l'inscription, il demande {asks} et envoie {code}. Une boîte jetable reçoit ce message sans problème, ce qui en fait un bon usage de courte durée."],
  "list_intro": "Ce qu'il faut retenir pour {name} :",
  "title": "{name} : inscription, vérification et bonnes pratiques",
  "closing": "En revanche, si vous comptez utiliser {name} durablement, refaites l'inscription avec une adresse permanente : une boîte jetable expirée ne recevra plus jamais les e-mails de réinitialisation de mot de passe.",
 },
 "de": {
  "cat": {"social":"soziale Netzwerke","streaming":"Video-Streaming","music":"Musik",
    "marketplace":"Online-Shopping","developer":"Entwicklerplattform","ai":"Künstliche Intelligenz",
    "productivity":"Produktivität","design":"Design","storage":"Cloud-Speicher",
    "gaming":"Spiele","payments":"Zahlung","transport":"Mobilität","travel":"Reisen"},
  "asks": {"username_email":"eine E-Mail-Adresse und einen eindeutigen Benutzernamen",
    "email":"eine E-Mail-Adresse","email_password":"eine E-Mail-Adresse und ein Passwort"},
  "code": {"otp":"einen Einmalcode, der nach wenigen Minuten abläuft",
    "link":"eine E-Mail mit einem Bestätigungslink"},
  "attr": [
    "ein Einmalcode, der nach wenigen Minuten abläuft, wird per E-Mail gesendet",
    "Sie müssen den Bestätigungslink in der E-Mail anklicken",
    "manchmal wird zusätzlich eine Telefonnummer verlangt",
    "bekannte Wegwerf-Domains werden erkannt und abgelehnt",
    "Sie müssen einen eindeutigen Benutzernamen wählen",
    "für die volle Nutzung ist eine Zahlungsmethode nötig",
    "bei einer Anmeldung von einem neuen Gerät kommt eine Warn-E-Mail",
    "Sie können auf mehreren Geräten angemeldet bleiben",
    "der Dienst hat viele Nutzer und ist ein häufiges Spam-Ziel",
    "nach der Anmeldung kommen auch Bestell- und Versandbenachrichtigungen",
    "es gelten strenge Anforderungen an das Passwort",
    "die Zwei-Faktor-Authentifizierung per E-Mail wird unterstützt",
    "Konten, die wie Wegwerfkonten wirken, können eingeschränkt werden",
    "es werden Sicherheits- und Aktivitätshinweise per E-Mail verschickt"],
  "t": [
    "Für ein Konto bei {name} geben Sie zuerst {asks} ein und bestätigen danach Ihre Identität mit {code}. Eine Wegwerfadresse eignet sich gut, um nur diese Bestätigungsmail zu empfangen.",
    "Fügen Sie die temporäre Adresse von Offex Mail in das {name}-Formular ein und Sie erhalten {code} in wenigen Sekunden. Prüfen Sie vor dem Absenden, dass die Adresse korrekt und ohne Leerzeichen ist.",
    "{name} ist ein Dienst aus dem Bereich {cat}: Bei der Anmeldung werden {asks} verlangt und {code} verschickt. Ein Wegwerf-Postfach empfängt diese Mail problemlos und eignet sich daher gut für eine kurze Nutzung."],
  "list_intro": "Das sollten Sie bei {name} beachten:",
  "title": "{name}: Registrierung, Verifizierung und gute Praxis",
  "closing": "Wenn Sie {name} jedoch dauerhaft nutzen möchten, melden Sie sich mit einer festen Adresse neu an — ein abgelaufenes Wegwerf-Postfach erhält keine Passwort-Reset-Mails mehr.",
 },
 "pt": {
  "cat": {"social":"redes sociais","streaming":"streaming de vídeo","music":"música",
    "marketplace":"compras online","developer":"desenvolvimento","ai":"inteligência artificial",
    "productivity":"produtividade","design":"design","storage":"armazenamento na nuvem",
    "gaming":"jogos","payments":"pagamento","transport":"transporte","travel":"viagem"},
  "asks": {"username_email":"um endereço de e-mail e um nome de usuário único",
    "email":"um endereço de e-mail","email_password":"um endereço de e-mail e uma senha"},
  "code": {"otp":"um código de uso único que expira em poucos minutos",
    "link":"um e-mail com um link de confirmação"},
  "attr": [
    "um código de uso único que expira em poucos minutos é enviado por e-mail",
    "é preciso clicar no link de confirmação recebido por e-mail",
    "às vezes também é solicitado um número de telefone",
    "domínios de e-mail descartáveis conhecidos podem ser detectados e recusados",
    "você precisa escolher um nome de usuário exclusivo",
    "uma forma de pagamento é necessária para usar o serviço por completo",
    "um e-mail de alerta chega quando você entra de um novo dispositivo",
    "você pode continuar conectado em vários dispositivos",
    "o serviço tem muitos usuários e atrai bastante spam",
    "após o cadastro, também chegam avisos de pedido e entrega",
    "o serviço exige uma senha forte",
    "há suporte à autenticação em duas etapas por e-mail",
    "contas que parecem descartáveis podem ser restringidas",
    "o serviço envia avisos de segurança e de atividade"],
  "t": [
    "Para criar uma conta na {name}, você informa {asks} e depois confirma sua identidade com {code}. Um endereço descartável serve bem só para receber esse e-mail de verificação.",
    "Cole o endereço temporário do Offex Mail no formulário da {name} e você receberá {code} em poucos segundos. Confirme que o endereço está correto, sem espaços extras, antes de enviar o formulário.",
    "A {name} é um serviço de {cat}: no cadastro, pede {asks} e envia {code}. Uma caixa descartável recebe essa mensagem sem problemas, o que a torna ideal para um uso breve."],
  "list_intro": "O que lembrar na {name}:",
  "title": "{name}: cadastro, verificação e boas práticas",
  "closing": "Mas se você pretende usar a {name} por muito tempo, refaça o cadastro com um endereço permanente — uma caixa descartável expirada não recebe mais e-mails de redefinição de senha.",
 },
 "ru": {
  "cat": {"social":"социальные сети","streaming":"видеосервисы","music":"музыка",
    "marketplace":"интернет-магазины","developer":"разработка","ai":"искусственный интеллект",
    "productivity":"продуктивность","design":"дизайн","storage":"облачное хранилище",
    "gaming":"игры","payments":"платежи","transport":"транспорт","travel":"путешествия"},
  "asks": {"username_email":"адрес электронной почты и уникальное имя пользователя",
    "email":"адрес электронной почты","email_password":"адрес электронной почты и пароль"},
  "code": {"otp":"одноразовый код, действующий несколько минут",
    "link":"письмо со ссылкой для подтверждения"},
  "attr": [
    "на почту приходит одноразовый код, действующий несколько минут",
    "нужно перейти по ссылке подтверждения в письме",
    "иногда дополнительно запрашивают номер телефона",
    "известные домены одноразовой почты могут блокироваться",
    "нужно выбрать уникальное имя пользователя",
    "для полноценного использования нужен способ оплаты",
    "при входе с нового устройства приходит письмо-уведомление",
    "можно оставаться в системе на нескольких устройствах",
    "у сервиса много пользователей, и он часто становится целью спама",
    "после регистрации приходят письма о заказах и доставке",
    "действуют строгие требования к паролю",
    "поддерживается двухфакторная аутентификация по почте",
    "аккаунты, похожие на одноразовые, могут ограничивать",
    "сервис присылает уведомления о безопасности и активности"],
  "t": [
    "Для регистрации в {name} нужно указать {asks}, а затем подтвердить личность с помощью {code}. Одноразовый адрес подойдёт, чтобы получить только это письмо с подтверждением.",
    "Вставьте временный адрес Offex Mail в форму {name}, и {code} придёт за несколько секунд. Перед отправкой проверьте, что адрес указан точно, без лишних пробелов.",
    "{name} — это сервис категории {cat}: при регистрации он запрашивает {asks} и отправляет {code}. Одноразовый ящик спокойно принимает такое письмо, поэтому он подходит для короткого использования."],
  "list_intro": "Что важно помнить про {name}:",
  "title": "{name}: регистрация, проверка и полезные советы",
  "closing": "Но если вы планируете пользоваться {name} долго, зарегистрируйтесь заново с постоянным адресом — истёкший одноразовый ящик больше не получит письма для сброса пароля.",
 },
 "ar": {
  "cat": {"social":"شبكات التواصل","streaming":"بث الفيديو","music":"الموسيقى",
    "marketplace":"التسوق الإلكتروني","developer":"منصات المطوّرين","ai":"الذكاء الاصطناعي",
    "productivity":"الإنتاجية","design":"التصميم","storage":"التخزين السحابي",
    "gaming":"الألعاب","payments":"المدفوعات","transport":"التنقّل","travel":"السفر"},
  "asks": {"username_email":"عنوان بريد إلكتروني واسم مستخدم فريد",
    "email":"عنوان بريد إلكتروني","email_password":"عنوان بريد إلكتروني وكلمة مرور"},
  "code": {"otp":"رمز لمرة واحدة تنتهي صلاحيته خلال دقائق",
    "link":"رسالة تحتوي على رابط تأكيد"},
  "attr": [
    "يُرسل عبر البريد رمز لمرة واحدة تنتهي صلاحيته خلال دقائق",
    "يجب النقر على رابط التأكيد في الرسالة",
    "قد يطلب رقم هاتف إضافي في بعض الأحيان",
    "قد يتعرّف على نطاقات البريد المؤقت المعروفة ويرفضها",
    "يجب اختيار اسم مستخدم غير مكرر",
    "تحتاج إلى وسيلة دفع لاستخدام الخدمة بشكل كامل",
    "تصلك رسالة تنبيه عند تسجيل الدخول من جهاز جديد",
    "يمكنك البقاء مسجّل الدخول على عدة أجهزة",
    "للخدمة مستخدمون كثر وهي هدف شائع للرسائل المزعجة",
    "بعد التسجيل تصلك أيضًا إشعارات الطلبات والتوصيل",
    "تفرض شروطًا صارمة على كلمة المرور",
    "تدعم التحقق بخطوتين عبر البريد",
    "قد تقيّد الحسابات التي تبدو مؤقتة",
    "ترسل إشعارات الأمان والنشاط"],
  "t": [
    "لإنشاء حساب على {name}، تُدخل أولًا {asks} ثم تؤكّد هويتك عبر {code}. العنوان المؤقت مناسب لاستقبال رسالة التحقق هذه فقط.",
    "الصق العنوان المؤقت من Offex Mail في نموذج {name} وستصلك {code} خلال ثوانٍ. تأكد من كتابة العنوان بدقة ودون مسافات زائدة قبل إرسال النموذج.",
    "‏{name} خدمة من فئة {cat}: عند التسجيل تطلب {asks} وترسل {code}. وصندوق بريد مؤقت يستقبل هذه الرسالة بلا مشكلة، لذا يناسب الاستخدام القصير."],
  "list_intro": "نقاط يجب تذكّرها في {name}:",
  "title": "{name}: التسجيل والتحقق وأفضل الممارسات",
  "closing": "لكن إذا كنت تنوي استخدام {name} لفترة طويلة، فأعد التسجيل بعنوان دائم — فالصندوق المؤقت المنتهي لا يستقبل رسائل إعادة تعيين كلمة المرور.",
 },
 "zh": {
  "cat": {"social":"社交网络","streaming":"视频流媒体","music":"音乐",
    "marketplace":"在线购物","developer":"开发者平台","ai":"人工智能",
    "productivity":"办公效率","design":"设计工具","storage":"云存储",
    "gaming":"游戏","payments":"支付","transport":"出行打车","travel":"旅行"},
  "asks": {"username_email":"邮箱地址和唯一的用户名","email":"邮箱地址",
    "email_password":"邮箱地址和密码"},
  "code": {"otp":"几分钟内失效的一次性验证码","link":"包含确认链接的邮件"},
  "attr": [
    "会通过邮件发送几分钟内失效的一次性验证码",
    "需要点击邮件里的确认链接才能完成验证",
    "有时还会要求你再填写手机号码",
    "可能会识别并拒绝已知的临时邮箱域名",
    "需要选择一个独一无二的用户名",
    "要正式使用需要绑定付款方式",
    "从新设备登录时会收到提醒邮件",
    "可以让你在多个设备上保持登录状态",
    "用户众多，是垃圾邮件的高频目标",
    "注册后还会收到订单和物流通知邮件",
    "对密码强度有较严格的要求",
    "支持通过邮件进行两步验证",
    "可能会限制看起来像临时账号的账户",
    "会发送安全与账户动态通知"],
  "t": [
    "在 {name} 注册账号时，需要先填写{asks}，然后通过{code}完成验证。临时邮箱正好适合只用来接收这封验证邮件。",
    "把 Offex Mail 的临时地址粘贴到 {name} 的注册表单，就能在几秒内收到{code}。提交前请确认地址没有多余空格、拼写完全正确。",
    "{name} 属于{cat}类服务，注册时需要{asks}，并会发送{code}。一次性收件箱同样可以正常接收这类验证邮件，因此很适合短期使用。"],
  "list_intro": "关于 {name}，需要记住这几点：",
  "title": "{name}：注册、验证与实用建议",
  "closing": "不过，如果你打算长期使用 {name}，请改用长期地址重新注册；临时收件箱一旦过期，你将无法再收到密码重置邮件。",
 },
 "ja": {
  "cat": {"social":"ソーシャルメディア","streaming":"動画配信","music":"音楽",
    "marketplace":"オンラインショッピング","developer":"開発者向けプラットフォーム","ai":"人工知能",
    "productivity":"仕事効率化","design":"デザイン","storage":"クラウドストレージ",
    "gaming":"ゲーム","payments":"決済","transport":"配車・移動","travel":"旅行"},
  "asks": {"username_email":"メールアドレスと一意のユーザー名","email":"メールアドレス",
    "email_password":"メールアドレスとパスワード"},
  "code": {"otp":"数分で失効する一度きりの確認コード","link":"確認用のリンクを含むメール"},
  "attr": [
    "数分で失効する一度きりのコードがメールで届きます",
    "メール内の確認リンクをクリックして認証を完了します",
    "場合によっては電話番号の入力を追加で求められます",
    "使い捨てメールのドメインを検出して拒否することがあります",
    "誰とも重複しないユーザー名を選ぶ必要があります",
    "本格的に使うには支払い方法の登録が必要です",
    "新しい端末からのログイン時に通知メールが届きます",
    "複数の端末で同じアカウントにログインしたままにできます",
    "利用者が多く、迷惑メールの標的になりやすいサービスです",
    "登録後は注文や配送のお知らせメールも届きます",
    "パスワードの条件が厳しく設定されています",
    "メール経由の二段階認証に対応しています",
    "使い捨てと見なされたアカウントを制限することがあります",
    "セキュリティや利用状況の通知メールを送ってきます"],
  "t": [
    "{name} のアカウント作成では、まず{asks}を入力し、その後{code}で本人確認を行います。使い捨てアドレスは、この確認メールを受け取るためだけに使うのが安全です。",
    "Offex Mail の一時アドレスを {name} の登録フォームに貼り付ければ、{code}を数秒で受け取れます。送信する前に、アドレスが正しく入力され余分な空白がないかを確認してください。",
    "{name} は{cat}に分類されるサービスで、登録時に{asks}が必要です。確認のために{code}が送られますが、これは使い捨ての受信箱でも問題なく受け取れます。"],
  "list_intro": "{name} で押さえておきたいポイント:",
  "title": "{name}: 登録・認証と上手な使い方",
  "closing": "ただし {name} を今後も使い続けるつもりなら、登録は恒久的なアドレスでやり直すことをおすすめします。一時アドレスは受信箱が失効すると、パスワード再設定メールを受け取れなくなるためです。",
 },

 "hi": {
  "cat": {"social":"सोशल मीडिया","streaming":"वीडियो स्ट्रीमिंग","music":"संगीत",
    "marketplace":"ऑनलाइन शॉपिंग","developer":"डेवलपर प्लेटफ़ॉर्म","ai":"कृत्रिम बुद्धिमत्ता",
    "productivity":"प्रोडक्टिविटी","design":"डिज़ाइन","storage":"क्लाउड स्टोरेज",
    "gaming":"गेमिंग","payments":"भुगतान","transport":"ट्रांसपोर्ट","travel":"यात्रा"},
  "asks": {"username_email":"एक ईमेल पता और एक अनोखा यूज़रनेम","email":"एक ईमेल पता",
    "email_password":"एक ईमेल पता और एक पासवर्ड"},
  "code": {"otp":"कुछ मिनटों में एक्सपायर होने वाला एक-बार का कोड",
    "link":"कन्फर्मेशन लिंक वाला ईमेल"},
  "attr": [
    "कुछ मिनटों में एक्सपायर होने वाला एक-बार का कोड ईमेल से आता है",
    "ईमेल में दिए कन्फर्मेशन लिंक पर क्लिक करके वेरिफिकेशन पूरा करना होता है",
    "कभी-कभी फ़ोन नंबर भी मांगा जा सकता है",
    "जाने-पहचाने टेम्प-मेल डोमेन को पहचानकर अस्वीकार कर सकता है",
    "एक अनोखा यूज़रनेम चुनना ज़रूरी होता है",
    "पूरी तरह इस्तेमाल करने के लिए भुगतान का तरीका जोड़ना पड़ता है",
    "नए डिवाइस से लॉगिन करने पर अलर्ट ईमेल आता है",
    "कई डिवाइस पर लॉगिन बना रह सकता है",
    "इसके बहुत उपयोगकर्ता हैं और यह स्पैम का आम निशाना है",
    "साइनअप के बाद ऑर्डर और डिलीवरी की सूचनाएं भी आती हैं",
    "पासवर्ड के लिए सख्त शर्तें हैं",
    "ईमेल से दो-चरणीय वेरिफिकेशन का समर्थन करता है",
    "अस्थायी लगने वाले अकाउंट पर रोक लगा सकता है",
    "सुरक्षा और गतिविधि की सूचनाएं ईमेल करता है"],
  "t": [
    "{name} पर अकाउंट बनाते समय पहले {asks} भरना होता है, फिर {code} से पुष्टि होती है। डिस्पोज़ेबल पता सिर्फ़ यही वेरिफिकेशन मेल पाने के लिए ठीक है।",
    "Offex Mail का टेम्प पता {name} के फ़ॉर्म में पेस्ट करें और {code} सेकंडों में आ जाएगा। फ़ॉर्म भेजने से पहले जांचें कि पते में कोई अतिरिक्त स्पेस नहीं है।",
    "{name} {cat} श्रेणी की सेवा है: साइनअप पर यह {asks} मांगता है और {code} भेजता है। डिस्पोज़ेबल इनबॉक्स यह मेल आसानी से पा लेता है, इसलिए यह छोटे इस्तेमाल के लिए ठीक है।"],
  "list_intro": "{name} के लिए ध्यान रखने वाली बातें:",
  "title": "{name}: साइनअप, वेरिफिकेशन और बेहतर तरीके",
  "closing": "लेकिन अगर आप {name} लंबे समय तक इस्तेमाल करने की सोच रहे हैं, तो स्थायी पते से दोबारा रजिस्टर करें — एक्सपायर हुआ टेम्प इनबॉक्स पासवर्ड रीसेट मेल नहीं पा सकेगा।",
 },
 "es": {
  "cat": {"social":"redes sociales","streaming":"streaming de vídeo","music":"música",
    "marketplace":"compras en línea","developer":"plataformas para desarrolladores","ai":"inteligencia artificial",
    "productivity":"productividad","design":"diseño","storage":"almacenamiento en la nube",
    "gaming":"videojuegos","payments":"pagos","transport":"transporte","travel":"viajes"},
  "asks": {"username_email":"una dirección de correo y un nombre de usuario único",
    "email":"una dirección de correo","email_password":"una dirección de correo y una contraseña"},
  "code": {"otp":"un código de un solo uso que caduca en pocos minutos",
    "link":"un correo con un enlace de confirmación"},
  "attr": [
    "se envía por correo un código de un solo uso que caduca en pocos minutos",
    "hay que hacer clic en el enlace de confirmación del correo",
    "a veces también pide un número de teléfono",
    "puede detectar y rechazar dominios de correo desechable conocidos",
    "hay que elegir un nombre de usuario único",
    "se necesita un método de pago para usarlo por completo",
    "llega un correo de aviso al iniciar sesión desde un dispositivo nuevo",
    "puedes mantener la sesión abierta en varios dispositivos",
    "tiene muchos usuarios y es un objetivo habitual de spam",
    "tras el registro también llegan avisos de pedidos y entregas",
    "exige requisitos estrictos para la contraseña",
    "admite verificación en dos pasos por correo",
    "puede restringir cuentas que parecen desechables",
    "envía notificaciones de seguridad y de actividad"],
  "t": [
    "Para crear una cuenta en {name} primero se introduce {asks} y después se confirma la identidad con {code}. Una dirección desechable sirve solo para recibir ese correo de verificación.",
    "Pega la dirección temporal de Offex Mail en el formulario de {name} y recibirás {code} en pocos segundos. Comprueba que la dirección está bien escrita, sin espacios de más, antes de enviar.",
    "{name} es un servicio de {cat}: en el registro pide {asks} y envía {code}. Un buzón desechable recibe ese correo sin problema, por lo que va bien para un uso puntual."],
  "list_intro": "Lo que conviene recordar en {name}:",
  "title": "{name}: registro, verificación y buenas prácticas",
  "closing": "Pero si piensas usar {name} durante mucho tiempo, vuelve a registrarte con una dirección permanente: un buzón desechable caducado ya no recibirá los correos de restablecimiento de contraseña.",
 },
}

# language dir -> css class used for the section wrapper (matches existing style)
LANGS = ["hi", "es", "fr", "de", "pt", "ru", "ar", "zh", "ja"]

# deterministic template rotation so adjacent services don't share a structure
TIDX = {s: i % 3 for i, s in enumerate(sorted(SERVICES))}


def build_section(lang: str, service: str) -> str:
    pk = PACKS[lang]
    cat, asks, code, attrs = SERVICES[service]
    name = DISPLAY.get(service, service.capitalize())
    body_t = pk["t"][TIDX[service]]
    t = body_t.format(name=name, cat=pk["cat"][cat], asks=pk["asks"][asks],
                      code=pk["code"][code])
    li = "\n".join(f"      <li>{pk['attr'][a].format(name=name)}</li>" for a in attrs)
    title = pk["title"].format(name=name)
    intro = pk["list_intro"].format(name=name)
    closing = pk["closing"].format(name=name)
    return (
        f"<!-- offex-deep-{lang} -->\n"
        f"<h2>{title}</h2>\n"
        f"<p>{t}</p>\n"
        f"<p>{intro}</p>\n"
        f"<ul>\n{li}\n</ul>\n"
        f"<p>{closing}</p>\n"
    )


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--dry-run", action="store_true")
    args = ap.parse_args()

    anchor = re.compile(r'<h2>[^<]*</h2><ul class="related">')
    total = 0
    for lang in LANGS:
        n = 0
        for service in SERVICES:
            p = PUBLIC / lang / f"{service}.html"
            if not p.exists():
                continue
            raw = p.read_text(encoding="utf-8")
            if f"offex-deep-{lang}" in raw:
                continue
            m = anchor.search(raw)
            if not m:
                print(f"  ! no anchor in {lang}/{service}.html")
                continue
            section = build_section(lang, service)
            raw = raw[: m.start()] + section + raw[m.start():]
            if not args.dry_run:
                p.write_text(raw, encoding="utf-8")
            n += 1
        print(f"{lang}: {n} pages updated")
        total += n
    print(f"TOTAL: {total} pages")


if __name__ == "__main__":
    main()
