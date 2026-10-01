/* Offex Audio — cross-promo popup (promotes the free temp-mail site).
   Shows once per browser session; fully dismissible; never blocks the page. */
(function () {
  "use strict";
  try { if (sessionStorage.getItem("offex_audio_promo_seen")) return; } catch (e) {}

  var TARGET = "https://tempmail.offexmail.online";

  var css = ""
    + ".op-ov{position:fixed;inset:0;z-index:99999;background:rgba(8,7,4,.72);backdrop-filter:blur(6px);"
    + "-webkit-backdrop-filter:blur(6px);display:flex;align-items:center;justify-content:center;padding:18px;"
    + "opacity:0;pointer-events:none;transition:opacity .25s ease}"
    + ".op-ov.on{opacity:1;pointer-events:auto}"
    + ".op-card{position:relative;width:100%;max-width:420px;background:#1a160e;border:1px solid rgba(232,161,61,.35);"
    + "border-radius:20px;padding:26px 24px 22px;text-align:center;color:#f5efe3;"
    + "box-shadow:0 30px 70px rgba(0,0,0,.6);transform:translateY(14px) scale(.98);transition:transform .3s cubic-bezier(.2,.8,.2,1);"
    + "font-family:Inter,-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,sans-serif}"
    + ".op-ov.on .op-card{transform:none}"
    + ".op-x{position:absolute;top:10px;right:10px;width:34px;height:34px;border-radius:10px;cursor:pointer;"
    + "background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.14);color:#f5efe3;font-size:15px;font-family:inherit}"
    + ".op-x:hover{border-color:#e8a13d;color:#e8a13d}"
    + ".op-emoji{font-size:40px;line-height:1;margin-bottom:12px}"
    + ".op-card h3{margin:0 0 10px;font-size:19px;font-weight:800;letter-spacing:-.3px;color:#fff}"
    + ".op-card p{margin:0 0 18px;font-size:14px;line-height:1.6;color:#b8ae9c}"
    + ".op-cta{display:inline-flex;align-items:center;justify-content:center;gap:8px;width:100%;"
    + "background:linear-gradient(135deg,#e8a13d,#f0c060);color:#1a160e;font-weight:800;font-size:15px;"
    + "text-decoration:none;padding:14px 18px;border-radius:13px;box-shadow:0 12px 28px rgba(232,161,61,.35);"
    + "transition:transform .16s ease}"
    + ".op-cta:hover{transform:translateY(-2px)}"
    + ".op-skip{display:block;width:100%;margin-top:10px;background:none;border:none;color:#8f8677;"
    + "font-size:13px;font-weight:600;cursor:pointer;font-family:inherit;padding:8px}"
    + ".op-skip:hover{color:#f5efe3}"
    + ".op-tag{display:inline-block;font-size:11px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;"
    + "color:#e8a13d;background:rgba(232,161,61,.12);border:1px solid rgba(232,161,61,.3);"
    + "padding:5px 12px;border-radius:999px;margin-bottom:14px}";

  var html = ""
    + '<div class="op-ov" id="opPromo" role="dialog" aria-modal="true">'
    +   '<div class="op-card">'
    +     '<button class="op-x" id="opPromoX" aria-label="Close">&#10005;</button>'
    +     '<div class="op-emoji">&#128233;</div>'
    +     '<span class="op-tag">100% Working</span>'
    +     '<h3>Free Temp Mail &#8212; instant inbox</h3>'
    +     '<p>Need an email for OTP or account verification? Get a free disposable inbox in one click &#8212; no signup, no password, no spam.</p>'
    +     '<a class="op-cta" href="' + TARGET + '" target="_blank" rel="noopener">&#128236; Get Free Inbox &rarr;</a>'
    +     '<button class="op-skip" id="opPromoSkip">Maybe later</button>'
    +   '</div>'
    + '</div>';

  function boot() {
    var style = document.createElement("style");
    style.textContent = css;
    document.head.appendChild(style);
    var holder = document.createElement("div");
    holder.innerHTML = html;
    document.body.appendChild(holder.firstChild);
    var ov = document.getElementById("opPromo");

    function close() {
      ov.classList.remove("on");
      try { sessionStorage.setItem("offex_audio_promo_seen", "1"); } catch (e) {}
      setTimeout(function () { if (ov && ov.parentNode) ov.parentNode.removeChild(ov); }, 320);
    }
    document.getElementById("opPromoX").onclick = close;
    document.getElementById("opPromoSkip").onclick = close;
    ov.addEventListener("click", function (e) { if (e.target === ov) close(); });
    document.addEventListener("keydown", function (e) { if (e.key === "Escape") close(); });

    setTimeout(function () { ov.classList.add("on"); }, 2200);
  }

  if (document.readyState === "loading") {
    document.addEventListener("DOMContentLoaded", boot);
  } else {
    boot();
  }
})();
