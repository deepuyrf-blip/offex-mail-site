/**
 * offex-ads — ad configuration service for the Offex sites.
 *
 *   GET  /?site=mail|audio        -> { enabled, code, label }   (public, CORS *)
 *   POST /?site=mail|audio        -> update config              (needs x-admin-key)
 *
 * Config is stored in Workers KV (binding AD_CONFIG), keyed by site.
 * The sites fetch this at load time and inject whatever ad code is configured,
 * so ads can be turned on/off (or changed) from the admin panel with no redeploy.
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
    const url = new URL(request.url);

    if (request.method === "OPTIONS") return new Response(null, { headers: CORS });

    const key = siteKey(url);

    if (request.method === "GET") {
      let cfg = null;
      try { cfg = await env.AD_CONFIG.get(key, "json"); } catch (e) { cfg = null; }
      return json(cfg || DEFAULT_CFG);
    }

    if (request.method === "POST") {
      const provided = request.headers.get("x-admin-key") || "";
      const expected = env.ADMIN_KEY || "";
      if (!expected || provided !== expected) {
        return json({ ok: false, error: "unauthorized" }, 401);
      }
      let body;
      try { body = await request.json(); } catch (e) { return json({ ok: false, error: "bad json" }, 400); }
      const cfg = {
        enabled: !!body.enabled,
        code: String(body.code || "").slice(0, 20000),
        label: String(body.label || "Advertisement").slice(0, 80),
      };
      try {
        await env.AD_CONFIG.put(key, JSON.stringify(cfg));
      } catch (e) {
        return json({ ok: false, error: "kv write failed: " + String(e).slice(0, 120) }, 500);
      }
      return json({ ok: true, site: key, cfg });
    }

    return json({ ok: false, error: "method not allowed" }, 405);
  },
};
