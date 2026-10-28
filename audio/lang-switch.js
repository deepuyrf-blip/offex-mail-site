/* Offex Audio — language switcher.
 *
 * Every page carries the same compact <select id="langSelect">. This script
 * keeps it in sync with the page language, remembers the visitor's choice in
 * localStorage, and — only on English pages — offers a one-click way back to
 * the language the visitor last picked. It never redirects on its own, so
 * crawlers and first-time visitors always see the page they asked for.
 */
(function () {
  var KEY = "offex-lang";
  var root = document.documentElement;
  var current = root.getAttribute("data-lang") || "en";
  var sel = document.getElementById("langSelect");
  var saved = null;

  try { saved = localStorage.getItem(KEY); } catch (e) { /* storage blocked */ }

  if (sel) {
    var mine = sel.querySelector('option[data-lang="' + current + '"]');
    if (mine) sel.value = mine.value;

    sel.addEventListener("change", function () {
      if (!sel.value) return;
      var picked = sel.options[sel.selectedIndex];
      var code = (picked && picked.getAttribute("data-lang")) || "en";
      try { localStorage.setItem(KEY, code); } catch (e) { /* storage blocked */ }
      window.location.href = sel.value;
    });
  }

  // Returning visitor: show "Continue in <language>" on English pages only.
  if (current !== "en" || !saved || saved === "en" || !sel) return;
  var target = sel.querySelector('option[data-lang="' + saved + '"]');
  if (!target) return;

  var host = document.querySelector(".top-actions") || document.querySelector(".oa-header-in");
  if (!host || host.querySelector(".lang-return")) return;

  var link = document.createElement("a");
  link.className = "lang-return";
  link.href = target.value;
  link.textContent = target.textContent + " →";
  host.appendChild(link);
})();
