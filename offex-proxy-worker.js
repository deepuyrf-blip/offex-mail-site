// Offex API proxy Worker
// api.mytemp-mail.online  ->  https://factblink514-compiled.hf.space
// Only /api/* and /history are proxied. /api/* must come from our own site.
// POST /api/inbox requires a valid Cloudflare Turnstile token.
// The Hugging Face token is injected server-side (the browser never sees it).

const ALLOWED = [
  "https://mytemp-mail.online",
  "https://www.mytemp-mail.online",
  "https://offexmail.online",
  "https://www.offexmail.online",
  "https://tempmail.offexmail.online",
];

const ORIGIN = "https://factblink514-compiled.hf.space";


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
    const isHistory = path === "/history" || path.startsWith("/history/");

    if (!isApi && !isHistory) {
      return new Response("Not found", { status: 404, headers: { "x-offex-proxy": "1" } });
    }

    if (isApi) {
      const origin = request.headers.get("Origin") || "";
      const referer = request.headers.get("Referer") || "";
      const ok = ALLOWED.some((a) => origin.startsWith(a) || referer.startsWith(a));
      if (!ok) {
        return new Response(JSON.stringify({ error: "forbidden" }), {
          status: 403,
          headers: { "content-type": "application/json", "x-offex-proxy": "1" },
        });
      }
    }

    // captcha check on inbox creation
    if (path === "/api/inbox" && request.method === "POST") {
      const ok = await turnstileOk(request, env);
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
