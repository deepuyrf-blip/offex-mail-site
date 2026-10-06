/* Offex Mail — shared app-download banner.
   Injected as an always-visible promo bar right under the page header on
   the static service / legal / hub pages. It is deliberately NOT a popup and
   NOT a modal: it never covers content, never blocks the page, and carries a
   plain download link (no interstitial), so it stays AdSense-safe. */
(function () {
  "use strict";
  var APK = "https://github.com/deepuyrf-blip/offex-mail-site/releases/latest/download/OffexMail.apk";

  var STR = {
    en: { t: "\ud83d\udcf1 Better experience on the app \u2014 Download Offex Mail", b: "Download", a: "Download the Offex Mail Android app" },
    hi: { t: "\ud83d\udcf1 App par better experience \u2014 Offex Mail download karo", b: "Download", a: "Offex Mail Android app download karo" },
    es: { t: "\ud83d\udcf1 Mejor experiencia en la app \u2014 Descarga Offex Mail", b: "Descargar", a: "Descarga la app Offex Mail para Android" },
    fr: { t: "\ud83d\udcf1 Meilleure exp\u00e9rience sur l'appli \u2014 T\u00e9l\u00e9chargez Offex Mail", b: "T\u00e9l\u00e9charger", a: "T\u00e9l\u00e9charger l'application Offex Mail" },
    de: { t: "\ud83d\udcf1 Bessere Erfahrung in der App \u2014 Offex Mail herunterladen", b: "Herunterladen", a: "Offex Mail App herunterladen" },
    pt: { t: "\ud83d\udcf1 Melhor experi\u00eancia no app \u2014 Baixe o Offex Mail", b: "Baixar", a: "Baixar o app Offex Mail" },
    ru: { t: "\ud83d\udcf1 \u0423\u0434\u043e\u0431\u043d\u0435\u0435 \u0432 \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0438 \u2014 \u0421\u043a\u0430\u0447\u0430\u0439\u0442\u0435 Offex Mail", b: "\u0421\u043a\u0430\u0447\u0430\u0442\u044c", a: "\u0421\u043a\u0430\u0447\u0430\u0442\u044c \u043f\u0440\u0438\u043b\u043e\u0436\u0435\u043d\u0438\u0435 Offex Mail" },
    ar: { t: "\ud83d\udcf1 \u062a\u062c\u0631\u0628\u0629 \u0623\u0641\u0636\u0644 \u0641\u064a \u0627\u0644\u062a\u0637\u0628\u064a\u0642 \u2014 \u062d\u0645\u0651\u0644 Offex Mail", b: "\u062a\u062d\u0645\u064a\u0644", a: "\u062d\u0645\u0651\u0644 \u062a\u0637\u0628\u064a\u0642 Offex Mail" },
    zh: { t: "\ud83d\udcf1 \u5e94\u7528\u4f53\u9a8c\u66f4\u4f73 \u2014 \u4e0b\u8f7d Offex Mail", b: "\u4e0b\u8f7d", a: "\u4e0b\u8f7d Offex Mail \u5e94\u7528" },
    ja: { t: "\ud83d\udcf1 \u30a2\u30d7\u30ea\u306e\u307b\u3046\u304c\u5feb\u9069 \u2014 Offex Mail \u3092\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9", b: "\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9", a: "Offex Mail \u30a2\u30d7\u30ea\u3092\u30c0\u30a6\u30f3\u30ed\u30fc\u30c9" }
  };

  var CSS = ".appdl{background:linear-gradient(135deg,#6d4dff,#0ea5b7);color:#fff}" +
    ".appdl .wrap{display:flex;flex-wrap:wrap;align-items:center;justify-content:center;text-align:center;gap:10px;padding-top:12px;padding-bottom:12px}" +
    ".appdl-tx{font-weight:700;font-size:.95rem;line-height:1.35;flex:1 1 200px;min-width:0}" +
    ".appdl-btn{display:inline-flex;align-items:center;gap:6px;background:#fff;color:#3a22b8;text-decoration:none;font-weight:700;font-size:.9rem;padding:9px 16px;border-radius:999px;white-space:nowrap;box-shadow:0 6px 16px rgba(0,0,0,.18)}" +
    ".appdl-btn:hover{filter:brightness(.96)}" +
    "@media(max-width:520px){.appdl-tx{flex:1 1 100%}.appdl-btn{width:100%;justify-content:center}}";

  function boot() {
    if (document.getElementById("offexAppdl")) return;
    var lang = (document.documentElement.getAttribute("lang") || "en").toLowerCase().slice(0, 2);
    var s = STR[lang] || STR.en;

    if (!document.getElementById("offexAppdlCss")) {
      var st = document.createElement("style");
      st.id = "offexAppdlCss";
      st.textContent = CSS;
      (document.head || document.documentElement).appendChild(st);
    }

    var d = document.createElement("div");
    d.id = "offexAppdl";
    d.className = "appdl";
    d.setAttribute("role", "complementary");
    d.setAttribute("aria-label", s.a);

    var wrap = document.createElement("div");
    wrap.className = "wrap";

    var tx = document.createElement("span");
    tx.className = "appdl-tx";
    tx.textContent = s.t;

    var a = document.createElement("a");
    a.className = "appdl-btn";
    a.href = APK;
    a.setAttribute("download", "");
    a.setAttribute("rel", "noopener");
    a.textContent = "\u2b07 " + s.b;

    wrap.appendChild(tx);
    wrap.appendChild(a);
    d.appendChild(wrap);

    var h = document.querySelector("header");
    if (h && h.parentNode) h.parentNode.insertBefore(d, h.nextSibling);
    else if (document.body) document.body.insertBefore(d, document.body.firstChild);
  }

  if (document.readyState === "loading") document.addEventListener("DOMContentLoaded", boot);
  else boot();
})();
