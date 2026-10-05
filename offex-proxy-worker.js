// Offex API proxy Worker
// api.mytemp-mail.online/*  ->  https://factblink514-compiled.hf.space/*
// Injects the Hugging Face token server-side (browser never sees it).
export default {
  async fetch(request, env) {
    const inUrl = new URL(request.url);
    const target = "https://factblink514-compiled.hf.space" + inUrl.pathname + inUrl.search;

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
      return new Response("proxy error: " + e.message, { status: 502, headers: { "x-offex-proxy": "1" } });
    }

    const out = new Response(resp.body, { status: resp.status, headers: resp.headers });
    out.headers.set("Access-Control-Allow-Origin", "*");
    out.headers.set("x-offex-proxy", "1");
    return out;
  },
};
