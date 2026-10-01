/**
 * offex-ads — ad configuration service for the Offex sites.
 *
 *   GET  /?site=mail|audio   -> { enabled, code, label }    (public, CORS *)
 *   GET  /ping               -> { ok: true }                (no KV, health)
 *   POST /?site=mail|audio   -> update config               (needs x-admin-key)
 *
 * Config lives in Workers KV (binding AD_CONFIG), keyed by site.
 */

const CORS = {
  "Access-Control-Allow-Origin": "*",
  "Access-Control-Allow-Methods": "GET, POST, OPTIONS",
  "Access-Control-Allow-Headers": "Content-Type, x-admin-key",
  "Access-Control-Max-Age": "86400",
};

const DEFAULT_CFG = { enabled: false, code: "", label: "Advertisement" };

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "Content-Type": "application/json", "Cache-Control": "no-store", ...CORS },
  });
}

function siteKey(url) {
  const s = (url.searchParams.get("site") || "mail").toLowerCase();
  return s === "audio" ? "audio" : "mail";
}

export default {
  async fetch(request, env) {
    try {
      const url = new URL(request.url);

      if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

      if (url.pathname === "/ping") {
        return json({ ok: true, kv: !!env.AD_CONFIG, hasKey: !!env.ADMIN_KEY, ts: Date.now() });
      }

      const key = siteKey(url);
      const kv = env.AD_CONFIG;

      if (request.method === "GET") {
        if (!kv) return json({ ...DEFAULT_CFG, _warn: "AD_CONFIG binding missing" });
        let cfg = null;
        try { cfg = await kv.get(key, "json"); } catch (e) { cfg = null; }
        return json(cfg || DEFAULT_CFG);
      }

      if (request.method === "POST") {
        const provided = request.headers.get("x-admin-key") || "";
        const expected = env.ADMIN_KEY || "";
        if (!expected) return json({ ok: false, error: "ADMIN_KEY not set on worker" }, 500);
        if (provided !== expected) return json({ ok: false, error: "unauthorized" }, 401);
        let body;
        try { body = await request.json(); } catch (e) { return json({ ok: false, error: "bad json" }, 400); }
        const cfg = {
          enabled: !!body.enabled,
          code: String(body.code || "").slice(0, 20000),
          label: String(body.label || "Advertisement").slice(0, 80),
        };
        if (!kv) return json({ ok: false, error: "AD_CONFIG binding missing" }, 500);
        await kv.put(key, JSON.stringify(cfg));
        return json({ ok: true, site: key, cfg });
      }

      return json({ ok: false, error: "method not allowed" }, 405);
    } catch (e) {
      return json({ ok: false, error: String(e), stack: String((e && e.stack) || "").slice(0, 400) }, 200);
    }
  },
};
