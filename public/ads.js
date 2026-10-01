/* ============================================================
   Offex Mail — Ad integration (Monetag)
   ============================================================

   HOW TO ENABLE (takes ~5 minutes):

   1. Create a FREE account at  https://monetag.com  (publisher signup).
   2. In the dashboard click "Add website" and enter:
         offex-mail.pages.dev        (and your custom domain if any)
   3. Verify ownership — Monetag shows you a <meta> tag (or a file).
        • Meta tag  ->  send it to me, I'll add it to the site's <head>.
   4. Create an ad zone / "MultiTag" for the site, then COPY its code.
   5. Paste that code between the markers below (and set ENABLED = true).
      Then redeploy — done.

   Typical Monetag MultiTag code looks like this (yours may differ —
   paste EXACTLY what Monetag gives you):

       var s = document.createElement('script');
       s.src = '//libtl.com/sdk.js';
       s.dataset.zone = '1234567';
       s.dataset.sdk  = '1234567';
       s.async = true;
       document.head.appendChild(s);

   NOTES
   • Monetag's main formats (Popunder, Push, In-Page Push, Vignette,
     SmartLink) are injected by the script — no extra HTML needed.
   • Set SHOW_SLOT = true only if you use a banner / native format that
     needs a visible box (the box is hidden by default).
   ============================================================ */
(function () {
  "use strict";

  var ENABLED = false;    // <-- set true after pasting your code below
  var SHOW_SLOT = false;  // <-- true only for banner/native formats

  if (SHOW_SLOT) {
    var slot = document.getElementById("adSlot");
    var box = document.getElementById("adSlotBox");
    if (box) box.textContent = "";
    if (slot) slot.style.display = "";
  }

  if (!ENABLED) return;

  try {

    /* ======== PASTE YOUR MONETAG CODE BELOW THIS LINE ======== */



    /* ======== PASTE YOUR MONETAG CODE ABOVE THIS LINE ======== */

  } catch (e) {
    if (window.console) console.warn("Ad init failed:", e);
  }
})();
