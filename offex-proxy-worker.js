// Offex API proxy Worker
// Forwards api.mytemp-mail.online/*  ->  https://factblink514-compiled.hf.space/*
// and injects the Hugging Face token server-side (the browser never sees it).
export default {
  async fetch(request, env) {
    const inUrl = new URL(request.url);
    const target = "https://factblink514-compiled.hf.space" + inUrl.pathname + inUrl.search;

    const headers = new Headers(request.headers);
    headers.set("Authorization", "Bearer " + (env.HF_TOKEN || ""));
    headers.delete("cf-connecting-ip");
    headers.delete("cf-worker");

    const init = { method: request.method, headers, redirect: "manual" };
    if (request.method !== "GET" && request.method !== "HEAD") {
      init.body = request.body;
    }

    const resp = await fetch(target, init);
    const out = new Response(resp.body, { status: resp.status, headers: resp.headers });
    out.headers.set("Access-Control-Allow-Origin", "*");
    return out;
  },
};
