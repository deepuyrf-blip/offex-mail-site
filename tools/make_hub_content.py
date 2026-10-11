#!/usr/bin/env python3
"""
Add a translated "what is temp mail / how it works / FAQ" content block to each
of the nine language hubs (public/<lang>/index.html) so every hub is substantial,
not just the English homepage.

Run: python tools/make_hub_content.py
"""
from __future__ import annotations

from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
PUBLIC = ROOT / "public"

BLOCKS = {
 "hi": """
<h2>टेम्प मेल क्या है?</h2>
<p>टेम्प मेल या डिस्पोज़ेबल ईमेल एक ऐसा ईमेल पता है जिसे आप तुरंत इस्तेमाल कर सकते हैं और फिर छोड़ सकते हैं। इसमें कोई साइनअप नहीं, कोई पासवर्ड नहीं और कोई ऐसा अकाउंट नहीं जिसे बनाए रखना पड़े। Offex Mail खोलें, एक पता तुरंत बन जाता है, और आप सेकंडों में उस पर मेल पाना शुरू कर सकते हैं। काम खत्म होने पर टैब बंद करें — इनबॉक्स और उसका सारा मेल अपने आप हट जाता है।</p>
<p>यहां हर पता हमारे अपने डोमेन <strong>mytemp-mail.online</strong> पर चलता है, इसलिए यह एक असली, मेल पाने वाला पता है — न कि ऐसा कुछ जो सिर्फ़ ईमेल जैसा दिखता है।</p>
<h2>यह कैसे काम करता है?</h2>
<ol>
<li><strong>इनबॉक्स बनाएं।</strong> Offex Mail खोलें — तुरंत एक ताज़ा पता तैयार मिलता है, या आप अपना नाम चुन सकते हैं।</li>
<li><strong>पता कॉपी करें।</strong> पेज के ऊपर दिख रहा ईमेल पता कॉपी करें।</li>
<li><strong>इसे इस्तेमाल करें।</strong> जिस साइट पर वेरिफिकेशन या OTP चाहिए वहां यह पता पेस्ट करें और फ़ॉर्म भेजें।</li>
<li><strong>मेल पाएं।</strong> इनबॉक्स अपने आप रीफ़्रेश होता है और नए मेल पर आवाज़ भी करता है — कोड कॉपी करके वेरिफिकेशन पूरा करें।</li>
</ol>
<h2>टेम्प मेल — आम सवाल</h2>
<dl class="faq">
<dt>क्या टेम्प मेल मुफ़्त है?</dt><dd>हां। कोई अकाउंट, कोई भुगतान और कोई छिपा शुल्क नहीं।</dd>
<dt>टेम्प इनबॉक्स कितनी देर चलता है?</dt><dd>हर इनबॉक्स कुछ समय के लिए सक्रिय रहता है; काम तुरंत कर लें और मेल को बाद के लिए न रखें।</dd>
<dt>क्या टेम्प मेल इस्तेमाल करना सुरक्षित है?</dt><dd>एक-बार के साइनअप, OTP और ट्रायल के लिए हां। बैंक या सरकारी अकाउंट के लिए कभी नहीं।</dd>
<dt>क्या मैं अपना नाम चुन सकता हूं?</dt><dd>हां। इनबॉक्स बनाने से पहले कोई नाम टाइप करें; अगर वह खाली है तो वही मिल जाएगा।</dd>
</dl>
""",
 "es": """
<h2>&iquest;Qu&eacute; es un correo temporal?</h2>
<p>Un correo temporal o desechable es una direcci&oacute;n de correo que puedes usar al instante y luego tirar. No requiere registro, ni contrase&ntilde;a, ni una cuenta que mantener. Abres Offex Mail, se genera una direcci&oacute;n al momento y puedes empezar a recibir mensajes en segundos. Cuando terminas, cierras la pesta&ntilde;a y el buz&oacute;n desaparece con todo lo que conten&iacute;a.</p>
<p>Cada direcci&oacute;n funciona en nuestro propio dominio, <strong>mytemp-mail.online</strong>, as&iacute; que es un buz&oacute;n real y entregable, no algo que solo lo parece.</p>
<h2>&iquest;C&oacute;mo funciona?</h2>
<ol>
<li><strong>Crea un buz&oacute;n.</strong> Abre Offex Mail y tendr&aacute;s una direcci&oacute;n lista al instante, o elige tu propio nombre.</li>
<li><strong>Copia la direcci&oacute;n.</strong> Copia la direcci&oacute;n que aparece en la parte superior de la p&aacute;gina.</li>
<li><strong>&Uacute;sala.</strong> Pega la direcci&oacute;n donde el sitio pida un correo para verificar o enviar un c&oacute;digo, y env&iacute;a el formulario.</li>
<li><strong>Recibe el correo.</strong> El buz&oacute;n se actualiza solo y avisa con un sonido; copia el c&oacute;digo y completa la verificaci&oacute;n.</li>
</ol>
<h2>Preguntas frecuentes sobre el correo temporal</h2>
<dl class="faq">
<dt>&iquest;Es gratis?</dt><dd>S&iacute;. Sin cuenta, sin pago y sin cargos ocultos.</dd>
<dt>&iquest;Cu&aacute;nto dura un buz&oacute;n temporal?</dt><dd>Cada buz&oacute;n permanece activo un tiempo limitado; haz lo que necesites enseguida y no guardes el correo para despu&eacute;s.</dd>
<dt>&iquest;Es seguro usarlo?</dt><dd>Para registros puntuales, c&oacute;digos y pruebas, s&iacute;. Nunca para cuentas bancarias o de gobierno.</dd>
<dt>&iquest;Puedo elegir mi propio nombre?</dt><dd>S&iacute;. Escribe un nombre antes de crear el buz&oacute;n; si est&aacute; libre, es tuyo.</dd>
</dl>
""",
 "fr": """
<h2>Qu&rsquo;est-ce qu&rsquo;un e-mail temporaire&nbsp;?</h2>
<p>Un e-mail temporaire, ou jetable, est une adresse que vous pouvez utiliser imm&eacute;diatement puis abandonner. Aucune inscription, aucun mot de passe, aucun compte &agrave; entretenir. Vous ouvrez Offex Mail, une adresse est cr&eacute;&eacute;e sur-le-champ et vous pouvez recevoir du courrier en quelques secondes. Quand vous avez termin&eacute;, vous fermez l&rsquo;onglet&nbsp;: la bo&icirc;te et son contenu disparaissent d&rsquo;eux-m&ecirc;mes.</p>
<p>Chaque adresse fonctionne sur notre propre domaine, <strong>mytemp-mail.online</strong>&nbsp;: c&rsquo;est donc une vraie bo&icirc;te joignable, pas quelque chose qui y ressemble seulement.</p>
<h2>Comment &ccedil;a marche&nbsp;?</h2>
<ol>
<li><strong>Cr&eacute;ez une bo&icirc;te.</strong> Ouvrez Offex Mail&nbsp;: une adresse est pr&ecirc;te imm&eacute;diatement, ou choisissez votre propre nom.</li>
<li><strong>Copiez l&rsquo;adresse.</strong> Copiez l&rsquo;adresse affich&eacute;e en haut de la page.</li>
<li><strong>Utilisez-la.</strong> Collez-la l&agrave; o&ugrave; un site demande un e-mail pour v&eacute;rifier ou envoyer un code, puis validez le formulaire.</li>
<li><strong>Recevez le message.</strong> La bo&icirc;te s&rsquo;actualise seule et sonne &agrave; chaque nouveau message&nbsp;; copiez le code et terminez la v&eacute;rification.</li>
</ol>
<h2>Questions fr&eacute;quentes sur l&rsquo;e-mail temporaire</h2>
<dl class="faq">
<dt>Est-ce gratuit&nbsp;?</dt><dd>Oui. Sans compte, sans paiement et sans frais cach&eacute;s.</dd>
<dt>Combien de temps dure une bo&icirc;te temporaire&nbsp;?</dt><dd>Chaque bo&icirc;te reste active un temps limit&eacute;&nbsp;; faites le n&eacute;cessaire tout de suite et ne gardez pas le message pour plus tard.</dd>
<dt>Est-ce s&ucirc;r&nbsp;?</dt><dd>Pour des inscriptions ponctuelles, des codes et des essais, oui. Jamais pour un compte bancaire ou administratif.</dd>
<dt>Puis-je choisir mon nom&nbsp;?</dt><dd>Oui. Saisissez un nom avant de cr&eacute;er la bo&icirc;te&nbsp;; s&rsquo;il est libre, il est &agrave; vous.</dd>
</dl>
""",
 "de": """
<h2>Was ist eine tempor&auml;re E-Mail?</h2>
<p>Eine tempor&auml;re oder Wegwerf-E-Mail ist eine Adresse, die Sie sofort nutzen und danach verwerfen k&ouml;nnen. Keine Anmeldung, kein Passwort, kein Konto, das gepflegt werden muss. Sie &ouml;ffnen Offex Mail, eine Adresse entsteht auf der Stelle, und schon nach Sekunden k&ouml;nnen Sie Post empfangen. Wenn Sie fertig sind, schlie&szlig;en Sie den Tab &mdash; das Postfach und sein Inhalt verschwinden von selbst.</p>
<p>Jede Adresse l&auml;uft auf unserer eigenen Domain <strong>mytemp-mail.online</strong>, ist also ein echtes, erreichbares Postfach und nicht nur etwas, das so aussieht.</p>
<h2>Wie funktioniert es?</h2>
<ol>
<li><strong>Postfach anlegen.</strong> &Ouml;ffnen Sie Offex Mail &mdash; sofort ist eine Adresse bereit, oder Sie w&auml;hlen einen eigenen Namen.</li>
<li><strong>Adresse kopieren.</strong> Kopieren Sie die oben auf der Seite angezeigte Adresse.</li>
<li><strong>Verwenden.</strong> F&uuml;gen Sie die Adresse dort ein, wo eine Seite eine E-Mail zur Best&auml;tigung oder f&uuml;r einen Code verlangt, und senden Sie das Formular ab.</li>
<li><strong>Mail empfangen.</strong> Das Postfach aktualisiert sich selbst und ert&ouml;nt bei neuer Post &mdash; kopieren Sie den Code und schlie&szlig;en Sie die Best&auml;tigung ab.</li>
</ol>
<h2>H&auml;ufige Fragen zur tempor&auml;ren E-Mail</h2>
<dl class="faq">
<dt>Ist es kostenlos?</dt><dd>Ja. Ohne Konto, ohne Zahlung und ohne versteckte Kosten.</dd>
<dt>Wie lange h&auml;lt ein tempor&auml;res Postfach?</dt><dd>Jedes Postfach bleibt nur eine begrenzte Zeit aktiv &mdash; erledigen Sie alles sofort und heben Sie die Mail nicht auf.</dd>
<dt>Ist es sicher?</dt><dd>F&uuml;r einmalige Anmeldungen, Codes und Tests ja. Niemals f&uuml;r Bank- oder Beh&ouml;rdenkonten.</dd>
<dt>Kann ich meinen Namen w&auml;hlen?</dt><dd>Ja. Geben Sie vor dem Anlegen einen Namen ein &mdash; ist er frei, geh&ouml;rt er Ihnen.</dd>
</dl>
""",
 "pt": """
<h2>O que &eacute; um e-mail tempor&aacute;rio?</h2>
<p>Um e-mail tempor&aacute;rio, ou descart&aacute;vel, &eacute; um endere&ccedil;o que voc&ecirc; pode usar na hora e depois abandonar. Sem cadastro, sem senha e sem uma conta para manter. Voc&ecirc; abre o Offex Mail, um endere&ccedil;o &eacute; criado na hora e, em segundos, come&ccedil;a a receber mensagens. Quando termina, fecha a aba e a caixa desaparece junto com tudo o que havia nela.</p>
<p>Cada endere&ccedil;o funciona no nosso pr&oacute;prio dom&iacute;nio, <strong>mytemp-mail.online</strong>, ou seja, &eacute; uma caixa real e entreg&aacute;vel, e n&atilde;o algo que apenas se parece com um e-mail.</p>
<h2>Como funciona?</h2>
<ol>
<li><strong>Crie uma caixa.</strong> Abra o Offex Mail e um endere&ccedil;o fica pronto na hora, ou escolha o seu pr&oacute;prio nome.</li>
<li><strong>Copie o endere&ccedil;o.</strong> Copie o endere&ccedil;o mostrado no topo da p&aacute;gina.</li>
<li><strong>Use-o.</strong> Cole o endere&ccedil;o onde o site pedir um e-mail para verificar ou enviar um c&oacute;digo e envie o formul&aacute;rio.</li>
<li><strong>Receba o e-mail.</strong> A caixa atualiza sozinha e toca um som a cada nova mensagem &mdash; copie o c&oacute;digo e conclua a verifica&ccedil;&atilde;o.</li>
</ol>
<h2>Perguntas frequentes sobre e-mail tempor&aacute;rio</h2>
<dl class="faq">
<dt>&Eacute; gr&aacute;tis?</dt><dd>Sim. Sem conta, sem pagamento e sem taxas escondidas.</dd>
<dt>Quanto tempo dura uma caixa tempor&aacute;ria?</dt><dd>Cada caixa fica ativa por um tempo limitado &mdash; fa&ccedil;a o que precisa na hora e n&atilde;o guarde a mensagem para depois.</dd>
<dt>&Eacute; seguro?</dt><dd>Para cadastros pontuais, c&oacute;digos e testes, sim. Nunca para contas banc&aacute;rias ou de governo.</dd>
<dt>Posso escolher meu pr&oacute;prio nome?</dt><dd>Sim. Digite um nome antes de criar a caixa; se estiver livre, &eacute; seu.</dd>
</dl>
""",
 "ru": """
<h2>Что такое временная почта?</h2>
<p>Временная или одноразовая почта — это адрес, которым можно сразу воспользоваться, а затем выбросить. Ни регистрации, ни пароля, ни аккаунта, который нужно поддерживать. Вы открываете Offex Mail, адрес создаётся на месте, и уже через секунды вы получаете письма. Когда всё готово, закройте вкладку — ящик и всё его содержимое исчезнут сами.</p>
<p>Каждый адрес работает на нашем собственном домене <strong>mytemp-mail.online</strong> — это настоящий ящик, который действительно принимает письма, а не что-то лишь похожее на адрес.</p>
<h2>Как это работает?</h2>
<ol>
<li><strong>Создайте ящик.</strong> Откройте Offex Mail — адрес готов сразу, или выберите своё имя.</li>
<li><strong>Скопируйте адрес.</strong> Скопируйте адрес, показанный вверху страницы.</li>
<li><strong>Используйте его.</strong> Вставьте адрес там, где сайт просит почту для проверки или кода, и отправьте форму.</li>
<li><strong>Получите письмо.</strong> Ящик обновляется сам и звучит при новом письме — скопируйте код и завершите проверку.</li>
</ol>
<h2>Частые вопросы о временной почте</h2>
<dl class="faq">
<dt>Это бесплатно?</dt><dd>Да. Без аккаунта, без оплаты и без скрытых платежей.</dd>
<dt>Сколько живёт временный ящик?</dt><dd>Каждый ящик активен ограниченное время — делайте всё сразу и не откладывайте письмо на потом.</dd>
<dt>Это безопасно?</dt><dd>Для разовых регистраций, кодов и тестов — да. Никогда для банковских или государственных аккаунтов.</dd>
<dt>Можно ли выбрать своё имя?</dt><dd>Да. Введите имя перед созданием ящика; если оно свободно — оно ваше.</dd>
</dl>
""",
 "ar": """
<h2>ما هو البريد المؤقت؟</h2>
<p>البريد المؤقت أو البريد الذي يُستخدم مرة واحدة هو عنوان بريد إلكتروني يمكنك استخدامه فورًا ثم التخلّي عنه. لا تسجيل، ولا كلمة مرور، ولا حساب يحتاج إلى رعاية. تفتح Offex Mail فيُنشأ عنوان في الحال، وتبدأ في استقبال الرسائل خلال ثوانٍ. وعندما تنتهي تُغلق التبويب، فيختفي الصندوق وكل ما فيه من تلقاء نفسه.</p>
<p>يعمل كل عنوان على نطاقنا الخاص <strong>mytemp-mail.online</strong>، فهو صندوق حقيقي قابل للتسليم، وليس شيئًا يشبه البريد الإلكتروني في الشكل فقط.</p>
<h2>كيف يعمل؟</h2>
<ol>
<li><strong>أنشئ صندوقًا.</strong> افتح Offex Mail فيكون العنوان جاهزًا فورًا، أو اختر اسمك الخاص.</li>
<li><strong>انسخ العنوان.</strong> انسخ العنوان الظاهر أعلى الصفحة.</li>
<li><strong>استخدمه.</strong> الصق العنوان حيث يطلب الموقع بريدًا للتحقق أو لإرسال رمز، ثم أرسل النموذج.</li>
<li><strong>استلم الرسالة.</strong> يُحدّث الصندوق نفسه ويصدر صوتًا عند وصول رسالة جديدة — انسخ الرمز وأكمل التحقق.</li>
</ol>
<h2>أسئلة شائعة عن البريد المؤقت</h2>
<dl class="faq">
<dt>هل هو مجاني؟</dt><dd>نعم. بلا حساب وبلا دفع وبلا رسوم خفية.</dd>
<dt>كم يدوم الصندوق المؤقت؟</dt><dd>يبقى كل صندوق نشطًا لمدة محدودة، فأنجز ما تحتاجه فورًا ولا تحفظ الرسالة لوقت لاحق.</dd>
<dt>هل استخدامه آمن؟</dt><dd>للتسجيلات المؤقتة والرموز والتجارب نعم. أما الحسابات البنكية أو الحكومية فلا تستخدمه لها أبدًا.</dd>
<dt>هل يمكنني اختيار اسمي؟</dt><dd>نعم. اكتب اسمًا قبل إنشاء الصندوق؛ فإن كان متاحًا فسيكون لك.</dd>
</dl>
""",
 "zh": """
<h2>什么是临时邮箱？</h2>
<p>临时邮箱（也叫一次性邮箱）是一个可以立刻使用、随后丢弃的邮箱地址。无需注册、无需密码，也没有需要维护的账号。打开 Offex Mail，地址即刻生成，几秒钟内你就能开始收信。用完之后关闭标签页，收件箱和里面的邮件会自动消失。</p>
<p>每个地址都运行在我们自己的域名 <strong>mytemp-mail.online</strong> 上，因此是真实可投递的邮箱，而不只是看起来像邮箱的东西。</p>
<h2>它是如何工作的？</h2>
<ol>
<li><strong>创建收件箱。</strong> 打开 Offex Mail，地址立即就绪，也可以自己指定名字。</li>
<li><strong>复制地址。</strong> 复制页面顶部显示的邮箱地址。</li>
<li><strong>使用地址。</strong> 在需要验证或接收验证码的网站中粘贴该地址，然后提交表单。</li>
<li><strong>收取邮件。</strong> 收件箱会自动刷新并在新邮件到达时发出提示音——复制验证码完成验证。</li>
</ol>
<h2>临时邮箱常见问题</h2>
<dl class="faq">
<dt>是免费的吗？</dt><dd>是的。无需账号、无需付费，也没有隐藏费用。</dd>
<dt>临时收件箱能用多久？</dt><dd>每个收件箱只在有限时间内有效，所以请立即完成操作，不要把邮件留到以后再看。</dd>
<dt>使用它安全吗？</dt><dd>用于一次性注册、验证码和测试是安全的。切勿用于银行或政府账户。</dd>
<dt>我可以自己选名字吗？</dt><dd>可以。创建收件箱前输入名字，如果没有被占用就归你使用。</dd>
</dl>
""",
 "ja": """
<h2>Temp Mail（使い捨てメール）とは？</h2>
<p>Temp Mail とは、すぐに使えてそのまま捨てられるメールアドレスのことです。登録もパスワードも、維持すべきアカウントもありません。Offex Mail を開くとアドレスがその場で生成され、数秒でメールを受け取れます。用が済んだらタブを閉じるだけ — 受信箱と中身は自動的に消えます。</p>
<p>どのアドレスも自社ドメイン <strong>mytemp-mail.online</strong> で動くので、見た目だけのものではなく、実際に受信できる本物のメールボックスです。</p>
<h2>使い方</h2>
<ol>
<li><strong>受信箱を作る。</strong> Offex Mail を開くとすぐにアドレスが用意されます。自分で名前を選ぶこともできます。</li>
<li><strong>アドレスをコピーする。</strong> ページ上部に表示されたアドレスをコピーします。</li>
<li><strong>使う。</strong> 認証やコードが必要なサイトでこのアドレスを貼り付け、フォームを送信します。</li>
<li><strong>メールを受け取る。</strong> 受信箱は自動で更新され、新着時に音が鳴ります — コードをコピーして認証を完了しましょう。</li>
</ol>
<h2>Temp Mail のよくある質問</h2>
<dl class="faq">
<dt>無料ですか？</dt><dd>はい。アカウントも支払いも隠れた料金もありません。</dd>
<dt>使い捨て受信箱はどのくらい使えますか？</dt><dd>各受信箱は限られた時間だけ有効です。必要な作業はすぐに済ませ、メールを後回しにしないでください。</dd>
<dt>安全に使えますか？</dt><dd>一度きりの登録やコード、テストには安全です。銀行や行政のアカウントには決して使わないでください。</dd>
<dt>名前を自分で選べますか？</dt><dd>はい。受信箱を作る前に名前を入力してください。空いていればその名前が使えます。</dd>
</dl>
""",
}


def main():
    for lang, block in BLOCKS.items():
        p = PUBLIC / lang / "index.html"
        raw = p.read_text(encoding="utf-8")
        if "offex-hub-content" in raw:
            print(f"{lang}: already present")
            continue
        marker = "</div></main>"
        if marker not in raw:
            print(f"{lang}: marker not found")
            continue
        raw = raw.replace(marker, f'<!-- offex-hub-content -->{block}\n</div></main>', 1)
        p.write_text(raw, encoding="utf-8")
        print(f"{lang}: added")
    print("done")


if __name__ == "__main__":
    main()
