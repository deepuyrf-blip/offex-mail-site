import sys

T = {
 "en": ("Ad blocker detected",
        "Please turn off your ad blocker / AdGuard (and any ad-blocking DNS) to use this site, then reload.",
        "Reload"),
 "hi": ("Ad blocker detect hua",
        "Is site ko use karne ke liye pehle apna ad blocker / AdGuard (aur koi bhi ad-blocking DNS) band karo, phir reload karo.",
        "Reload"),
 "es": ("Bloqueador de anuncios detectado",
        "Desactiva tu bloqueador de anuncios / AdGuard (y cualquier DNS de bloqueo) para usar este sitio, luego recarga.",
        "Recargar"),
 "fr": ("Bloqueur de publicités détecté",
        "Désactivez votre bloqueur de publicités / AdGuard (et tout DNS de blocage) pour utiliser ce site, puis rechargez.",
        "Recharger"),
 "de": ("Werbeblocker erkannt",
        "Bitte deaktiviere deinen Werbeblocker / AdGuard (und blockierendes DNS), um diese Seite zu nutzen, dann neu laden.",
        "Neu laden"),
 "pt": ("Bloqueador de anúncios detectado",
        "Desative seu bloqueador de anúncios / AdGuard (e qualquer DNS de bloqueio) para usar este site, depois recarregue.",
        "Recarregar"),
 "ru": ("Обнаружен блокировщик рекламы",
        "Отключите блокировщик рекламы / AdGuard (и блокирующий DNS), чтобы пользоваться сайтом, затем перезагрузите.",
        "Перезагрузить"),
 "ar": ("تم اكتشاف مانع الإعلانات",
        "يرجى إيقاف مانع الإعلانات / AdGuard (وأي DNS مانع للإعلانات) لاستخدام هذا الموقع، ثم أعد التحميل.",
        "إعادة التحميل"),
 "zh": ("检测到广告拦截器",
        "请关闭您的广告拦截器 / AdGuard（以及任何广告拦截 DNS）以使用本网站，然后刷新。",
        "刷新"),
 "ja": ("広告ブロッカーを検出しました",
        "このサイトを利用するには、広告ブロッカー / AdGuard（および広告ブロックDNS）をオフにして、再読み込みしてください。",
        "再読み込み"),
}


def patch_i18n(path):
    s = open(path, encoding="utf-8").read()
    for code, (title, msg, btn) in T.items():
        anchor = "\n%s:{" % code
        if s.count(anchor) != 1:
            print("i18n anchor FAIL", code, s.count(anchor))
            sys.exit(2)
        add = ('\n%s:{\n'
               ' adblock_title:"%s",\n'
               ' adblock_msg:"%s",\n'
               ' adblock_btn:"%s",') % (code, title, msg, btn)
        s = s.replace(anchor, add, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("i18n patched, size:", len(s))


def patch_html(path):
    s = open(path, encoding="utf-8").read()
    anchor = "<body>\n"
    if s.count(anchor) != 1:
        print("html body anchor FAIL", s.count(anchor))
        sys.exit(2)

    gate = '''<body>
<div id="adblockGate" style="display:none;position:fixed;inset:0;z-index:99999;background:#0f1117;color:#e8eaf2;align-items:center;justify-content:center;padding:24px;text-align:center;font-family:system-ui,-apple-system,Segoe UI,Roboto,sans-serif">
  <div style="max-width:540px">
    <div style="font-size:46px">\U0001f6ab</div>
    <h2 data-i18n="adblock_title" style="margin:10px 0 10px;font-size:20px">Ad blocker detected</h2>
    <p data-i18n="adblock_msg" style="color:#a9b0c7;line-height:1.65;font-size:15px">Please turn off your ad blocker / AdGuard (and any ad-blocking DNS) to use this site, then reload.</p>
    <p style="color:#7b8194;line-height:1.6;font-size:12px;margin-top:14px">Disable AdGuard / ad blocker / ad-blocking DNS, then reload.</p>
    <button onclick="location.reload()" data-i18n="adblock_btn" style="margin-top:18px;padding:12px 24px;border:0;border-radius:10px;background:#6d4dff;color:#fff;font-weight:700;font-size:15px;cursor:pointer">Reload</button>
  </div>
</div>
<script>
(function(){
  function blocked(){
    try{
      var b=document.createElement("div");
      b.className="adsbox ad-banner adsbygoogle text-ad ad-placement pub_300x250";
      b.style.cssText="position:absolute!important;left:-9999px!important;top:-9999px!important;width:10px!important;height:10px!important;";
      b.innerHTML="&nbsp;";
      document.body.appendChild(b);
      var cs=window.getComputedStyle(b);
      var hidden = b.offsetHeight===0 || b.clientHeight===0 || b.offsetParent===null || cs.display==="none" || cs.visibility==="hidden";
      if(b.parentNode) b.parentNode.removeChild(b);
      return hidden;
    }catch(e){ return false; }
  }
  function apply(){
    var g=document.getElementById("adblockGate");
    if(!g) return;
    g.style.display = blocked() ? "flex" : "none";
  }
  window.addEventListener("DOMContentLoaded", apply);
  setTimeout(apply, 500);
  setInterval(apply, 3000);
})();
</script>
'''
    s = s.replace(anchor, gate, 1)
    open(path, "w", encoding="utf-8").write(s)
    print("html patched, size:", len(s))


patch_i18n("public/i18n.js")
patch_html("public/index.html")
