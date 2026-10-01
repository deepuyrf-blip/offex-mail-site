/**
 * offex-ads — ad configuration service for the Offex sites.
 * Classic service-worker format (most compatible with older wrangler/accounts).
 *
 *   GET  /?site=mail|audio   -> { enabled, code, label }    (public, CORS *)
 *   GET  /ping               -> { ok: true }                (no KV, health)
 *   POST /?site=mail|audio   -> update config               (needs x-admin-key)
 */

var CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-admin-key",
  "Access-Control-Max-Age": "86400",
};

var DEFAULT_CFG = { enabled: false, code: "", label: "Advertisement" };

function json(obj, status) {
  return new Response(JSON.stringify(obj), {
    status: status || 200,
    headers: Object.assign({ "Content-Type": "application/json", "Cache-Control": "no-store" }, CORS),
  });
}

function siteKey(url) {
  var s = (url.searchParams.get("site") || "mail").toLowerCase();
  return s === "audio" ? "audio" : "mail";
}

async function handle(request, env) {
  try {
    var url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    if (url.pathname === "/ping") {
      return json({ ok: true, kv: !!env.AD_CONFIG, hasKey: !!env.ADMIN_KEY, ts: Date.now() });
    }

    var key = siteKey(url);
    var kv = env.AD_CONFIG;

    if (request.method === "GET") {
      if (!kv) return json(Object.assign({}, DEFAULT_CFG, { _warn: "AD_CONFIG binding missing" }));
      var cfg = null;
      try { cfg = await kv.get(key, "json"); } catch (e) { cfg = null; }
      return json(cfg || DEFAULT_CFG);
    }

    if (request.method === "POST") {
      var provided = request.headers.get("x-admin-key") || "";
      var expected = env.ADMIN_KEY || "";
      if (!expected) return json({ ok: false, error: "ADMIN_KEY not set on worker" }, 500);
      if (provided !== expected) return json({ ok: false, error: "unauthorized" }, 401);
      var body;
      try { body = await request.json(); } catch (e) { return json({ ok: false, error: "bad json" }, 400); }
      var newCfg = {
        enabled: !!body.enabled,
        code: String(body.code || "").slice(0, 20000),
        label: String(body.label || "Advertisement").slice(0, 80),
      };
      if (!kv) return json({ ok: false, error: "AD_CONFIG binding missing" }, 500);
      await kv.put(key, JSON.stringify(newCfg));
      return json({ ok: true, site: key, cfg: newCfg });
    }

    return json({ ok: false, error: "method not allowed" }, 405);
  } catch (e) {
    return json({ ok: false, error: String(e), stack: String((e && e.stack) || "").slice(0, 400) });
  }
}

addEventListener("fetch", function (event) {
  event.respondWith(handle(event.request, event.env || (typeof env !== "undefined" ? env : {})));
});
