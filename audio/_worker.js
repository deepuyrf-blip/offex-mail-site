const DEFAULT_HF_SPACE = "https://hydui-ytvideo.hf.space";

function getHFTarget(request, env) {
  const incoming = new URL(request.url);
  const hfBase = (env.HF_SPACE_URL || DEFAULT_HF_SPACE).replace(/\/+$/, "");
  const suffix = incoming.pathname === "/hf" ? "/" : incoming.pathname.slice(3);
  const target = new URL(hfBase + suffix);
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

export default {
  async fetch(request, env) {
    const url = new URL(request.url);

    if (url.pathname === "/hf" || url.pathname.startsWith("/hf/")) {
      const { target } = getHFTarget(request, env);
      const upgrade = request.headers.get("Upgrade");

      if (upgrade && upgrade.toLowerCase() === "websocket") {
        return proxyWebSocket(request, env, target);
      }

      return proxyHTTP(request, env, target);
    }

    return env.ASSETS.fetch(request);
  }
};
