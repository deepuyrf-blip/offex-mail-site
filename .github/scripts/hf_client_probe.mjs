// Real end-to-end reproduction of the browser job flow using the SAME
// @gradio/client library the page loads, so the failing and fixed paths can be
// compared against the live Space.
import { Client } from "@gradio/client";
import fs from "node:fs";

const BASE = (process.env.HF_BASE || "https://offexmail.online/hf").replace(/\/$/, "");
const WAV = "/tmp/offex_probe.wav";

function hr(t) { console.log("\n" + "=".repeat(70) + "\n== " + t + "\n" + "=".repeat(70)); }

async function upload(path, name) {
  const buf = fs.readFileSync(path);
  const form = new FormData();
  form.append("files", new Blob([buf], { type: "audio/wav" }), name);
  const r = await fetch(BASE + "/gradio_api/upload", { method: "POST", body: form });
  const j = await r.json();
  const p = Array.isArray(j) ? j[0] : j;
  return { path: p, orig_name: name, size: buf.length, mime_type: "audio/wav", meta: { _type: "gradio.FileData" } };
}

// Exactly the page's fileUrl() helper.
function fileUrl(v) {
  if (v == null) return null;
  if (typeof v === "string") return v.length ? (v.indexOf("http") === 0 ? v : BASE + "/gradio_api/file=" + encodeURIComponent(v)) : null;
  if (typeof v === "object") {
    const u = v.url || v.path || v.name;
    if (!u) return null;
    if (String(u).indexOf("http") === 0) return u;
    if (String(u).charAt(0) === "/") return BASE + u;
    return BASE + "/gradio_api/file=" + encodeURIComponent(u);
  }
  return null;
}

function urlFrom(data) {
  if (!Array.isArray(data)) return { vocals: null, bgm: null };
  return {
    vocals: fileUrl(data[0]) || fileUrl(data[2]),
    bgm: fileUrl(data[1]) || fileUrl(data[3]),
  };
}

async function getBytes(url) {
  if (!url) return "no url";
  try {
    const r = await fetch(url, { redirect: "follow" });
    const b = await r.arrayBuffer();
    return `HTTP ${r.status}, ${b.byteLength} bytes, ${r.headers.get("content-type")}`;
  } catch (e) { return "fetch error: " + e.message; }
}

async function main() {
  hr("CONNECT (same target the page uses)");
  const client = await Client.connect(BASE);
  console.log("connected to", BASE);

  const fd = await upload(WAV, "offex_probe.wav");
  console.log("uploaded FileData:", JSON.stringify(fd));

  for (const model of ["High quality", "Faster"]) {
    hr(`BUGGY app-ui runJob path - submit("/isolate_voice_bgm", [file, ${JSON.stringify(model)}])`);
    {
      const job = client.submit("/isolate_voice_bgm", [fd, model]);
      let first = null, last = null, dataEvents = 0, statuses = [];
      job.on("data", (d) => { dataEvents++; if (first === null) first = d; last = d; });
      job.on("status", (st) => { if (st) statuses.push(st.stage || st.status || st.message); });
      await new Promise((res) => {
        job.on("status", (st) => { const s = st && (st.stage || st.status); if (s === "complete" || s === "error") res(); });
        setTimeout(res, 300000);
      });
      const f = urlFrom(first);
      console.log("data events fired:", dataEvents);
      console.log("statuses:", JSON.stringify(statuses.slice(-4)));
      console.log("FIRST data event:", JSON.stringify(first).slice(0, 700));
      console.log("FIRST -> vocals:", f.vocals, "| bgm:", f.bgm, "=> app-ui would throw 'no output':", (!f.vocals || !f.bgm));
      console.log("LAST data event outputs [0..3]:", JSON.stringify((last || []).slice(0, 4)).slice(0, 700));
    }

    hr(`FIXED path (iterate to completion) - model ${JSON.stringify(model)}`);
    {
      const job = client.submit("/isolate_voice_bgm", [fd, model]);
      let finalData = null, dataMessages = 0;
      for await (const msg of job) {
        if (msg && msg.type === "data") { finalData = msg.data; dataMessages++; }
      }
      const u = urlFrom(finalData);
      console.log("data messages:", dataMessages);
      console.log("FINAL -> vocals:", u.vocals);
      console.log("FINAL -> bgm   :", u.bgm);
      console.log("vocals bytes   :", await getBytes(u.vocals));
      console.log("bgm bytes      :", await getBytes(u.bgm));
    }
  }

  hr("COMPARISON - /process_audio (working tool) via iterate-to-completion");
  {
    const job = client.submit("/process_audio", [fd, 0.05, "Custom value", "Balanced"]);
    let finalData = null;
    for await (const msg of job) { if (msg && msg.type === "data") finalData = msg.data; }
    const u = fileUrl(finalData && finalData[0]);
    console.log("FINAL [0]:", JSON.stringify(finalData && finalData[0]).slice(0, 500));
    console.log("remove-silence output url:", u, "->", await getBytes(u));
  }

  hr("DONE");
}

main().catch((e) => { console.error("FATAL", e); process.exit(1); });
