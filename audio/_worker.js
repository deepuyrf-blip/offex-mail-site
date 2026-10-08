/**
 * Offex Audio — Cloudflare Pages advanced-mode worker.
 *
 * Server-side audio tools run on the Hugging Face Space (Gradio app) at
 * https://hydui-ytvideo.hf.space. This worker proxies every /hf/* request
 * (HTTP and WebSocket) to that Space, so the browser can talk to the Gradio
 * backend through the same origin as the site.
 *
 * /health reports whether the Hugging Face Space is responding, which drives
 * the Live / Not connected badge in the UI.
 */

const DEFAULT_HF_SPACE = "https://hydui-ytvideo.hf.space";

function hfBase(env) {
  return String((env && env.HF_SPACE_URL) || DEFAULT_HF_SPACE).replace(/\/+$/, "");
}

function getHFTarget(request, env) {
  const incoming = new URL(request.url);
  const base = hfBase(env);
  const suffix = incoming.pathname === "/hf" ? "/" : incoming.pathname.slice(3);
  const target = new URL(base + suffix);
  target.search = incoming.search;
  return { incoming, target };
}

function addHFAuth(headers, env) {
  headers.delete("host");
  if (env.HF_TOKEN) {
    headers.set("Authorization", `Bearer ${env.HF_TOKEN}`);
    headers.set("X-HF-Authorization", `Bearer ${env.HF_TOKEN}`);
  }
  return headers;
}

async function proxyWebSocket(request, env, target) {
  const upgrade = request.headers.get("Upgrade");
  if (!upgrade || upgrade.toLowerCase() !== "websocket") {
    return new Response("Expected Upgrade: websocket", { status: 426 });
  }

  const pair = new WebSocketPair();
  const [client, server] = Object.values(pair);

  const headers = addHFAuth(new Headers(request.headers), env);
  // The backend is the real WebSocket origin; this avoids origin checks
  // rejecting the Cloudflare Pages hostname.
  headers.set("Origin", target.origin);
  headers.set("Upgrade", "websocket");

  try {
    const upstream = await fetch(target.toString(), {
      method: "GET",
      headers,
      redirect: "follow"
    });

    if (upstream.status !== 101 || !upstream.webSocket) {
      const body = await upstream.text().catch(() => "");
      return new Response(
        `Hugging Face WebSocket upgrade failed (${upstream.status})${body ? `: ${body.slice(0, 500)}` : ""}`,
        { status: 502 }
      );
    }

    const remote = upstream.webSocket;

    server.accept({ allowHalfOpen: true });
    remote.accept({ allowHalfOpen: true });

    const closeBoth = (code = 1000, reason = "") => {
      try { if (server.readyState !== WebSocket.CLOSED) server.close(code, reason); } catch {}
      try { if (remote.readyState !== WebSocket.CLOSED) remote.close(code, reason); } catch {}
    };

    server.addEventListener("message", event => {
      try {
        if (remote.readyState === WebSocket.OPEN) remote.send(event.data);
      } catch {
        closeBoth(1011, "WebSocket proxy error");
      }
    });

    remote.addEventListener("message", event => {
      try {
        if (server.readyState === WebSocket.OPEN) server.send(event.data);
      } catch {
        closeBoth(1011, "WebSocket proxy error");
      }
    });

    server.addEventListener("close", event => {
      try { if (remote.readyState !== WebSocket.CLOSED) remote.close(event.code, event.reason || ""); } catch {}
    });

    remote.addEventListener("close", event => {
      try { if (server.readyState !== WebSocket.CLOSED) server.close(event.code, event.reason || ""); } catch {}
    });

    server.addEventListener("error", () => closeBoth(1011, "Client WebSocket error"));
    remote.addEventListener("error", () => closeBoth(1011, "Upstream WebSocket error"));

    return new Response(null, {
      status: 101,
      webSocket: client
    });
  } catch (error) {
    try { server.close(1011, "Upstream connection failed"); } catch {}
    return new Response(`Hugging Face WebSocket proxy error: ${error?.message || error}`, { status: 502 });
  }
}

async function proxyHTTP(request, env, target) {
  const headers = addHFAuth(new Headers(request.headers), env);
  headers.delete("connection");
  headers.delete("upgrade");

  const init = {
    method: request.method,
    headers,
    redirect: "follow"
  };

  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  return fetch(new Request(target.toString(), init));
}

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

// Ping the Hugging Face Space itself. A 2xx/3xx (after redirects) means the
// Space is up; anything else (or a timeout) means it is not reachable.
async function spaceOnline(env) {
  const base = hfBase(env);
  const ctrl = new AbortController();
  const timer = setTimeout(() => ctrl.abort(), 3500);
  try {
    const r = await fetch(base + "/", {
      method: "GET",
      redirect: "follow",
      signal: ctrl.signal,
      headers: { "accept": "text/html,application/xhtml+xml" }
    });
    clearTimeout(timer);
    return r.ok;
  } catch (e) {
    clearTimeout(timer);
    return false;
  }
}

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    // Lightweight, non-blocking health probe used by the Live / Not connected
    // badge. It reflects the Hugging Face Space, not a local placeholder.
    if (url.pathname === "/health") {
      const online = await spaceOnline(env);
      return json({
        status: "ok",
        service: "offex-audio",
        time: new Date().toISOString(),
        backend: online,
        processor: online
      });
    }

    // Hugging Face Space proxy (HTTP + WebSocket).
    if (url.pathname === "/hf" || url.pathname.startsWith("/hf/")) {
      const { target } = getHFTarget(request, env);
      const upgrade = request.headers.get("Upgrade");

      if (upgrade && upgrade.toLowerCase() === "websocket") {
        return proxyWebSocket(request, env, target);
      }

      return proxyHTTP(request, env, target);
    }

    // The app's own custom UI is published as a static asset (app-ui.html) so
    // it shares this site's origin with the /hf proxy. Serve it for the clean
    // URL /app-ui (and /app-ui/) regardless of the asset layer's extension
    // handling, so the WebView can load https://offexmail.online/app-ui.
    if (url.pathname === "/app-ui" || url.pathname === "/app-ui/") {
      const rewritten = new URL(request.url);
      rewritten.pathname = "/app-ui.html";
      return env.ASSETS.fetch(new Request(rewritten.toString(), request));
    }

    return env.ASSETS.fetch(request);
  }
};
