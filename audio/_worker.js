/**
 * Offex Audio — Cloudflare Pages advanced-mode worker.
 *
 * The site no longer depends on any Hugging Face Space. All core audio tools
 * (Remove Silence, Enhance Audio) run entirely in the visitor's browser.
 *
 * Optional server-side processing can still be attached later by setting the
 * BACKEND_URL environment variable on the Pages project; when it is present the
 * worker proxies /api/* to it and /health reports the processor as online.
 */

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: {
      "content-type": "application/json; charset=utf-8",
      "cache-control": "no-store, max-age=0",
      "access-control-allow-origin": "*"
    }
  });
}

function backendBase(env) {
  return String((env && env.BACKEND_URL) || "").replace(/\/+$/, "");
}

async function processorOnline(env) {
  const base = backendBase(env);
  if (!base) return false;
  try {
    const ctrl = new AbortController();
    const timer = setTimeout(() => ctrl.abort(), 3500);
    const r = await fetch(base + "/health", {
      method: "GET",
      signal: ctrl.signal,
      headers: { "accept": "application/json" }
    });
    clearTimeout(timer);
    return r.ok;
  } catch (e) {
    return false;
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Lightweight, non-blocking health probe used by the Live / Not connected badge.
    if (url.pathname === "/health") {
      const processor = await processorOnline(env);
      return json({
        status: "ok",
        service: "offex-audio",
        time: new Date().toISOString(),
        processor: processor
      });
    }

    // Optional server processor proxy. Returns 503 when none is configured,
    // so the UI can degrade gracefully instead of hanging.
    if (url.pathname === "/api" || url.pathname.startsWith("/api/")) {
      const base = backendBase(env);
      if (!base) return json({ error: "No server processor is configured." }, 503);
      const target = new URL(base + url.pathname.slice(4) + url.search);
      const headers = new Headers(request.headers);
      headers.delete("host");
      const init = { method: request.method, headers: headers, redirect: "follow" };
      if (request.method !== "GET" && request.method !== "HEAD") init.body = request.body;
      return fetch(new Request(target.toString(), init));
    }

    return env.ASSETS.fetch(request);
  }
};
