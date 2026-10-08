// Reproduce the app-ui.html and index.html job paths EXACTLY against the live
// Space, using the same @gradio/client the CDN serves the browser.
import { Client } from "@gradio/client";
import fs from "node:fs";

const PROXY = "https://offexmail.online/hf";
const DIRECT = "https://hydui-ytvideo.hf.space";
const WAV = "/tmp/offex_probe.wav";
const VER = JSON.parse(fs.readFileSync("./node_modules/@gradio/client/package.json", "utf8")).version;

function hr(t) { console.log("\n" + "=".repeat(70) + "\n== " + t + "\n" + "=".repeat(70)); }

async function upload(base, path, name) {
  const buf = fs.readFileSync(path);
  const form = new FormData();
  form.append("files", new Blob([buf], { type: "audio/wav" }), name);
  const r = await fetch(base.replace(/\/$/, "") + "/gradio_api/upload", { method: "POST", body: form });
  const j = await r.json();
  const p = Array.isArray(j) ? j[0] : j;
  return { path: p, orig_name: name, size: buf.length, mime_type: "audio/wav", meta: { _type: "gradio.FileData" } };
}

function fileUrl(v, proxy) {
  if (v == null) return null;
  if (typeof v === "string") return v.length ? (v.indexOf("http") === 0 ? v : proxy + "/gradio_api/file=" + encodeURIComponent(v)) : null;
  if (typeof v === "object") {
    const u = v.url || v.path || v.name;
    if (!u) return null;
    if (String(u).indexOf("http") === 0) return u;
    if (String(u).charAt(0) === "/") return proxy + u;
    return proxy + "/gradio_api/file=" + encodeURIComponent(u);
  }
  return null;
}
async function getBytes(url) {
  if (!url) return "no url";
  try { const r = await fetch(url, { redirect: "follow" }); const b = await r.arrayBuffer(); return `HTTP ${r.status}, ${b.byteLength} bytes, ${r.headers.get("content-type")}`; }
  catch (e) { return "fetch error: " + e.message; }
}

async function connectLikeAppUi() {
  const targets = [PROXY, DIRECT];
  let lastErr = null, client = null;
  for (let attempt = 0; attempt < 3 && !client; attempt++) {
    for (const target of targets) {
      try {
        client = await Promise.race([
          Client.connect(target),
          new Promise((_, rej) => setTimeout(() => rej(new Error("timeout")), 12000)),
        ]);
        console.log("connected via", target, "(attempt", attempt + 1, ")");
        break;
      } catch (e) { lastErr = e; console.log("connect failed:", target, "-", e.message); }
    }
  }
  if (!client) throw lastErr || new Error("no connect");
  return client;
}

async function appUiRunJob(client, endpoint, inputs) {
  const job = client.submit(endpoint, inputs);
  let finalData = null;
  const trace = [];
  if (job && typeof job.on === "function") {
    trace.push("branch: job.on");
    finalData = await new Promise((resolve, reject) => {
      let done = false;
      job.on("data", (d) => { done = true; resolve(d); });
      job.on("status", () => {});
      setTimeout(() => { if (!done) reject(new Error("Job timed out")); }, 600000);
    });
  } else if (job && job[Symbol.asyncIterator]) {
    trace.push("branch: asyncIterator");
    let n = 0;
    for await (const msg of job) {
      n++;
      if (msg && msg.type === "data") { finalData = msg.data; trace.push("  data msg #" + n); }
      else if (msg && msg.type === "status") { trace.push("  status msg #" + n + " stage=" + (msg.status && msg.status.stage)); }
      else trace.push("  msg #" + n + " type=" + (msg && msg.type));
    }
  } else if (job && typeof job.result === "function") {
    trace.push("branch: result()");
    const r = await job.result(); finalData = (r && r.data) || r;
  } else {
    trace.push("branch: predict()");
    const pr = await client.predict(endpoint, inputs); finalData = (pr && pr.data) || pr;
  }
  return { finalData, trace };
}

async function main() {
  hr("@gradio/client version used by the browser bundle: " + VER);
  const client = await connectLikeAppUi();

  const fd = await upload(PROXY, WAV, "offex_probe.wav");
  console.log("uploaded FileData:", JSON.stringify(fd));

  for (const model of ["High quality", "Faster"]) {
    hr(`app-ui doIsolate reproduction - /isolate_voice_bgm, model=${JSON.stringify(model)}`);
    const { finalData, trace } = await appUiRunJob(client, "/isolate_voice_bgm", [fd, model]);
    console.log("branch trace:\n  " + trace.join("\n  "));
    console.log("finalData is array:", Array.isArray(finalData), "length:", Array.isArray(finalData) ? finalData.length : "n/a");
    console.log("finalData[0..3]:", JSON.stringify((finalData || []).slice(0, 4)).slice(0, 900));
    const arr = Array.isArray(finalData) ? finalData : ((finalData && finalData.data) || []);
    const vocals = fileUrl(arr[0], PROXY) || fileUrl(arr[2], PROXY);
    const bgm = fileUrl(arr[1], PROXY) || fileUrl(arr[3], PROXY);
    console.log("app-ui -> vocals:", vocals);
    console.log("app-ui -> bgm   :", bgm);
    console.log("app-ui would throw 'no output':", (!vocals || !bgm));
    console.log("vocals bytes:", await getBytes(vocals));
    console.log("bgm bytes   :", await getBytes(bgm));
  }

  hr("index.html runGradioJob reproduction - /isolate_voice_bgm (High quality)");
  {
    const job = client.submit("/isolate_voice_bgm", [fd, "High quality"]);
    let finalData = null, n = 0;
    for await (const msg of job) { n++; if (msg && msg.type === "data") finalData = msg.data; }
    const arr = finalData || [];
    console.log("data messages:", n, "len:", Array.isArray(arr) ? arr.length : "n/a");
    const vocals = fileUrl(arr[0], PROXY) || fileUrl(arr[2], PROXY);
    const bgm = fileUrl(arr[1], PROXY) || fileUrl(arr[3], PROXY);
    console.log("index.html -> vocals:", vocals, "|", await getBytes(vocals));
    console.log("index.html -> bgm   :", bgm, "|", await getBytes(bgm));
  }

  hr("COMPARISON - /process_audio (Remove Silence) via app-ui path");
  {
    const { finalData } = await appUiRunJob(client, "/process_audio", [fd, 0.05, "Custom value", "Balanced"]);
    const u = fileUrl(finalData && finalData[0], PROXY);
    console.log("remove-silence url:", u, "->", await getBytes(u));
  }

  hr("DONE");
}
main().catch((e) => { console.error("FATAL", e); process.exit(1); });
