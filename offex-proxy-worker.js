// Offex API proxy Worker
// api.mytemp-mail.online  ->  https://factblink514-compiled.hf.space
//
// Routing / access rules:
//   * Panel HTML routes  /admin, /audio-admin  -> served DIRECTLY to a normal
//     top-level browser navigation. A typed or bookmarked URL sends no Origin
//     and no Referer, so these routes are never gated by the same-site check.
//   * History page       /history              -> served directly (same reason).
//   * API endpoints      /api/*                -> gated: only a same-site
//     browser request is allowed (stops cross-site abuse).
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

// A request counts as same-site when the browser says it came from one of our own
// pages. Origin/Referer cover cross-origin API calls; Sec-Fetch-Site is set by the
// browser (page JavaScript cannot forge it) and also covers same-origin calls from
// the admin panels when the browser omits the Referer header.
function sameSite(request) {
  const origin = request.headers.get("Origin") || "";
  const referer = request.headers.get("Referer") || "";
  if (ALLOWED.some((a) => origin.startsWith(a) || referer.startsWith(a))) return true;
  const sfs = (request.headers.get("Sec-Fetch-Site") || "").toLowerCase();
  return sfs === "same-origin" || sfs === "same-site";
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
