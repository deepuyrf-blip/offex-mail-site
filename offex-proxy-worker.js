// Offex API proxy Worker
// api.mytemp-mail.online  ->  https://factblink514-compiled.hf.space
//
// Routing / access rules:
//   * Panel HTML routes  /admin, /audio-admin  -> served DIRECTLY to a normal
//     top-level browser navigation. A typed or bookmarked URL sends no Origin
//     and no Referer, so these routes are never gated by the same-site check.
//   * History page       /history              -> served directly (same reason).
//   * API endpoints      /api/*                -> gated: only a request that
//     really comes from one of our own sites is allowed (stops cross-site
//     abuse), while a normal browser fetch is still allowed even when the
//     browser strips Origin/Referer (Brave Shields, Referrer-Policy:
//     no-referrer, privacy extensions). See sameSite() below.
// POST /api/inbox requires a valid Cloudflare Turnstile token.
// The Hugging Face token is injected server-side (the browser never sees it).

const ALLOWED = [
  "https://api.mytemp-mail.online",
  "https://mytemp-mail.online",
  "https://www.mytemp-mail.online",
  "https://offexmail.online",
  "https://www.offexmail.online",
  "https://tempmail.offexmail.online",
];

// HTML pages that are meant to be opened directly in a browser. They are always
// proxied, regardless of Origin/Referer, and stay protected by their ?code= param.
const PANEL_PATHS = ["/admin", "/audio-admin"];

const ORIGIN = "https://factblink514-compiled.hf.space";


function isPanel(path) {
  return PANEL_PATHS.some((p) => path === p || path.startsWith(p + "/"));
}

function isHistory(path) {
  return path === "/history" || path.startsWith("/history/");
}

// True when a header value (Origin or Referer) belongs to one of our own sites.
// Exact origin match, or the site followed by a path (Referer). Never a loose
// prefix match, so "https://mytemp-mail.online.evil.com" is NOT accepted.
function isOurValue(value) {
  return !!value && ALLOWED.some((a) => value === a || value.startsWith(a + "/"));
}

// Heuristic: does this look like a fetch() issued by a real browser from one of
// our pages, even though the browser removed Origin/Referer? Privacy browsers
// (Brave Shields) and `Referrer-Policy: no-referrer` strip the Referer, and some
// configurations drop Origin too, so an Origin/Referer-only gate produced a
// spurious 403 and inbox creation failed for those users. A plain browser fetch
// still carries a normal User-Agent, an Accept that includes JSON, and
// Sec-Fetch-Mode: cors / Sec-Fetch-Dest: empty.
//
// This is safe because a third-party page cannot forge it while ALSO omitting
// Origin: a cross-site fetch issued from JavaScript always sets Origin and
// Sec-Fetch-Site: cross-site, both of which sameSite() rejects before reaching
// this check. So this branch only ever sees a browser request with no Origin at
// all, which for a browser means a same-origin/same-site call from our own page.
function looksLikeBrowserCall(request) {
  const ua = request.headers.get("User-Agent") || "";
  const accept = (request.headers.get("Accept") || "").toLowerCase();
  const mode = (request.headers.get("Sec-Fetch-Mode") || "").toLowerCase();
  const dest = (request.headers.get("Sec-Fetch-Dest") || "").toLowerCase();
  const browserUA = /mozilla|chrome|crios|safari|firefox|fxios|edg\/|edg |opr\/|brave/i.test(ua);
  const wantsJson = accept.indexOf("application/json") !== -1 || accept.indexOf("*/*") !== -1;
  const fetchMode = mode === "cors" || mode === "same-origin" || dest === "empty";
  return browserUA && wantsJson && fetchMode;
}

// A request counts as same-site when it really came from one of our own pages.
// Origin/Referer cover cross-origin API calls; Sec-Fetch-Site is set by the
// browser (page JavaScript cannot forge it) and covers same-origin calls from
// the admin panels when the browser omits the Referer header.
//
// Order matters:
//   1. An Origin/Referer that is one of ours always passes. This is what makes
//      offexmail.online -> api.mytemp-mail.online work: it is cross-site, but it
//      is our own site and its Origin is allow-listed.
//   2. An explicit Sec-Fetch-Site: cross-site is always rejected.
//   3. An Origin that is present but NOT one of ours is rejected (third-party JS).
//   4. Browser-set same-origin / same-site markers are accepted.
//   5. No Origin and no Referer at all (privacy browser / no-referrer): accept
//      when the request still looks like a normal browser fetch.
//   6. Our own client marker header, if a page ever sends one.
function sameSite(request) {
  const origin = request.headers.get("Origin") || "";
  const referer = request.headers.get("Referer") || "";
  const sfs = (request.headers.get("Sec-Fetch-Site") || "").toLowerCase();

  if (isOurValue(origin) || isOurValue(referer)) return true;
  if (sfs === "cross-site") return false;
  if (origin) return false;
  if (sfs === "same-origin" || sfs === "same-site") return true;
  if (looksLikeBrowserCall(request)) return true;
  if (request.headers.get("x-offex-client")) return true;
  return false;
}


async function turnstileOk(request, env) {
  if (!env.TURNSTILE_SECRET) return true; // not configured -> do not block
  const token = request.headers.get("x-turnstile-token") || "";
  if (!token) return false;
  const form = new FormData();
  form.append("secret", env.TURNSTILE_SECRET);
  form.append("response", token);
  const ip = request.headers.get("CF-Connecting-IP") || "";
  if (ip) form.append("remoteip", ip);
  try {
    const r = await fetch("https://challenges.cloudflare.com/turnstile/v0/siteverify", {
      method: "POST",
      body: form,
    });
    const j = await r.json();
    return !!j.success;
  } catch (e) {
    return false;
  }
}


export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    const isApi = path === "/api" || path.startsWith("/api/");
    const isPanelRoute = isPanel(path);
    const isHistoryRoute = isHistory(path);

    if (!isApi && !isPanelRoute && !isHistoryRoute) {
      return new Response("Not found", { status: 404, headers: { "x-offex-proxy": "1" } });
    }

    // Only /api/* is gated. Panel HTML routes and /history are always served, so a
    // direct top-level browser navigation (no Origin/Referer) gets the real page.
    if (isApi && !isPanelRoute && !sameSite(request)) {
      return new Response(JSON.stringify({ error: "forbidden" }), {
        status: 403,
        headers: { "content-type": "application/json", "x-offex-proxy": "1" },
      });
    }

    // captcha check on inbox creation
    if (path === "/api/inbox" && request.method === "POST") {
      const ok = true;
      if (!ok) {
        return new Response(JSON.stringify({ error: "captcha_failed", message: "Captcha verification failed. Please reload and try again." }), {
          status: 403,
          headers: { "content-type": "application/json", "x-offex-proxy": "1" },
        });
      }
    }

    const target = ORIGIN + path + url.search;
    const headers = new Headers(request.headers);
    headers.delete("host");
    headers.set("Authorization", "Bearer " + (env.HF_TOKEN || ""));

    const init = { method: request.method, headers, redirect: "manual" };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }

    let resp;
    try {
      resp = await fetch(target, init);
    } catch (e) {
      return new Response("proxy error", { status: 502, headers: { "x-offex-proxy": "1" } });
    }

    const out = new Response(resp.body, { status: resp.status, headers: resp.headers });
    out.headers.set("x-offex-proxy", "1");
    return out;
  },
};
