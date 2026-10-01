/**
 * Offex Mail — API proxy (Cloudflare Pages Function)
 * ==================================================
 * The browser calls /api/* on THIS site. This function forwards the request
 * to the real backend (the Hugging Face Space) server-side, so the backend
 * URL and any access code are NEVER exposed in the client HTML.
 *
 * Set these in Cloudflare → Pages → your project → Settings → Variables:
 *   BACKEND_URL          = https://factblink514-compiled.hf.space   (kept secret-ish / server-side)
 *   BACKEND_ACCESS_CODE  = optional, only if the Space uses an ACCESS_CODE
 */
export async function onRequest(context) {
  const { request, env } = context;
  const backend = (env.BACKEND_URL || "https://factblink514-compiled.hf.space").replace(/\/+$/, "");
  const url = new URL(request.url);

  const headers = new Headers(request.headers);
  headers.delete("host");
  headers.delete("cf-connecting-ip");
  headers.delete("cf-ipcountry");
  if (env.BACKEND_ACCESS_CODE) headers.set("x-access-code", env.BACKEND_ACCESS_CODE);

  const init = { method: request.method, headers, redirect: "follow" };
  if (request.method !== "GET" && request.method !== "HEAD") {
    init.body = request.body;
  }

  let resp;
  try {
    resp = await fetch(backend + url.pathname + url.search, init);
  } catch (e) {
    return new Response(JSON.stringify({ error: "Backend unreachable. It may be waking up — try again in a few seconds." }),
      { status: 502, headers: { "content-type": "application/json" } });
  }

  const outHeaders = new Headers(resp.headers);
  outHeaders.set("access-control-allow-origin", "*");
  outHeaders.set("cache-control", "no-store");
  return new Response(resp.body, { status: resp.status, statusText: resp.statusText, headers: outHeaders });
}
