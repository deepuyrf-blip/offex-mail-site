// Offex API proxy Worker
// api.mytemp-mail.online  ->  https://factblink514-compiled.hf.space
// Only /api/* and /history are proxied. /api/* must come from our own site.
// The Hugging Face token is injected server-side (the browser never sees it).

const ALLOWED = [
  "https://mytemp-mail.online",
  "https://www.mytemp-mail.online",
  "https://offexmail.online",
  "https://www.offexmail.online",
  "https://tempmail.offexmail.online",
];

const ORIGIN = "https://factblink514-compiled.hf.space";


export default {
  async fetch(request, env) {
    const url = new URL(request.url);
    const path = url.pathname;

    const isApi = path === "/api" || path.startsWith("/api/");
    const isHistory = path === "/history" || path.startsWith("/history/");

    // nothing else is exposed through the proxy
    if (!isApi && !isHistory) {
      return new Response("Not found", { status: 404, headers: { "x-offex-proxy": "1" } });
    }

    // API calls must originate from our own website
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
