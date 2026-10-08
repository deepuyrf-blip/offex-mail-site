#!/usr/bin/env python3
"""Real end-to-end probe of the Offex Audio Hugging Face Space, run from a
GitHub Actions runner (the only place with egress to offexmail.online).

It mirrors EXACTLY what audio/app-ui.html and audio/index.html do in a browser:
  * read /gradio_api/info
  * POST the file to /gradio_api/upload
  * drive the Gradio queue/call flow
and prints the RAW JSON responses so the true failure can be diagnosed.
"""
import json
import math
import os
import struct
import sys
import wave

import requests

BASE = os.environ.get("HF_BASE", "https://offexmail.online/hf").rstrip("/")
TOKEN = os.environ.get("HF_TOKEN", "").strip()
DIRECT = os.environ.get("HF_DIRECT", "https://hydui-ytvideo.hf.space").rstrip("/")

SESSION = requests.Session()
SESSION.headers.update({"User-Agent": "offex-hf-probe/1.0"})


def hr(title):
    print("\n" + "=" * 78)
    print("== " + title)
    print("=" * 78, flush=True)


def dump(label, resp, limit=20000):
    hr(label)
    print("URL      :", resp.request.method, resp.url)
    print("STATUS   :", resp.status_code)
    print("HEADERS  :", dict(resp.headers))
    text = resp.text
    print("BODY (len=%d):" % len(text))
    if len(text) > limit:
        print(text[:limit] + "\n...[TRUNCATED %d chars]..." % (len(text) - limit))
    else:
        print(text)
    sys.stdout.flush()
    return text


def make_wav(path, seconds=4.0, rate=22050):
    n = int(seconds * rate)
    frames = bytearray()
    for i in range(n):
        t = i / rate
        v = (math.sin(2 * math.pi * 180 * t) * 0.5
             + math.sin(2 * math.pi * 360 * t) * 0.25
             + math.sin(2 * math.pi * 540 * t) * 0.12)
        v *= 0.6 + 0.4 * math.sin(2 * math.pi * 4 * t)
        m = (math.sin(2 * math.pi * 261.63 * t)
             + math.sin(2 * math.pi * 329.63 * t)
             + math.sin(2 * math.pi * 392.00 * t)) / 3.0
        s = 0.6 * v + 0.4 * m
        s = max(-1.0, min(1.0, s))
        frames += struct.pack("<h", int(s * 32000))
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(rate)
        w.writeframes(bytes(frames))
    return path


def fetch_info(base, headers=None):
    return SESSION.get(base + "/gradio_api/info", timeout=60, headers=headers or {})


def upload(base, path, headers=None):
    with open(path, "rb") as fh:
        files = {"files": (os.path.basename(path), fh, "audio/wav")}
        return SESSION.post(base + "/gradio_api/upload", files=files, timeout=300,
                            headers=headers or {})


def api_names(info_json):
    names = []
    for section in ("named_endpoints", "unnamed_endpoints"):
        sec = info_json.get(section) or {}
        for k in sec:
            names.append(k)
    return names


def describe_endpoint(info_json, wanted):
    hr("SIGNATURE: %s" % wanted)
    found = False
    for section in ("named_endpoints", "unnamed_endpoints"):
        sec = info_json.get(section) or {}
        for name, meta in sec.items():
            if wanted.strip("/").lower() in name.strip("/").lower():
                found = True
                print("section:", section)
                print("api_name:", name)
                print("parameters:")
                for p in (meta.get("parameters") or []):
                    print("   -", json.dumps(p))
                print("returns:")
                for ret in (meta.get("returns") or []):
                    print("   -", json.dumps(ret))
                print("raw meta:", json.dumps(meta)[:8000])
    if not found:
        print("NOT FOUND. Available:", api_names(info_json))
    sys.stdout.flush()


def call_rest(base, api_name, payload, headers=None, label=""):
    fn = api_name.strip("/")
    hr("REST CALL %s -> /gradio_api/call/%s" % (label, fn))
    print("REQUEST BODY:", json.dumps(payload)[:4000])
    r = SESSION.post(base + "/gradio_api/call/" + fn, json=payload, timeout=120,
                     headers=headers or {})
    dump("POST /gradio_api/call/%s (%s)" % (fn, label), r)
    try:
        event_id = r.json().get("event_id")
    except Exception:
        event_id = None
    if not event_id:
        print("!! no event_id returned")
        return None
    hr("STREAM /gradio_api/call/%s/%s (%s)" % (fn, event_id, label))
    with SESSION.get(base + "/gradio_api/call/%s/%s" % (fn, event_id),
                     stream=True, timeout=900, headers=headers or {}) as resp:
        print("STATUS:", resp.status_code)
        events = []
        for raw in resp.iter_lines(decode_unicode=True):
            if raw is None:
                continue
            print("SSE|", raw)
            if raw.startswith("data:"):
                try:
                    events.append(json.loads(raw[5:].strip()))
                except Exception:
                    pass
        sys.stdout.flush()
        if events:
            return events[-1]
    return None


def summarise_result(data, label):
    hr("SUMMARISE %s" % label)
    if data is None:
        print("no data")
        return
    if isinstance(data, dict) and "output" in data:
        data = data["output"]
    if isinstance(data, dict) and "data" in data:
        data = data["data"]
    if not isinstance(data, list):
        print("unexpected shape:", json.dumps(data)[:4000])
        return
    print("output count:", len(data))
    for i, item in enumerate(data):
        print("[%d] %s" % (i, json.dumps(item)[:1500]))


def main():
    hr("ENVIRONMENT")
    print("BASE (proxy)  :", BASE)
    print("DIRECT space  :", DIRECT)
    print("TOKEN present :", bool(TOKEN))

    try:
        dump("SITE /health", SESSION.get("https://offexmail.online/health", timeout=30))
    except Exception as e:
        print("health error:", e)

    info_text = None
    try:
        info_text = dump("INFO via proxy", fetch_info(BASE))
    except Exception as e:
        print("proxy info error:", e)

    direct_headers = {}
    if TOKEN:
        direct_headers["Authorization"] = "Bearer " + TOKEN
    try:
        dump("INFO direct to space", fetch_info(DIRECT, direct_headers))
    except Exception as e:
        print("direct info error:", e)

    info = None
    if info_text:
        try:
            info = json.loads(info_text)
        except Exception as e:
            print("info not JSON:", e)

    if info:
        hr("ENDPOINT NAMES")
        print(json.dumps(api_names(info), indent=2))
        print("gradio version:", info.get("version"))
        for ep in ("/isolate_voice_bgm", "/process_audio", "/enhance_audio"):
            describe_endpoint(info, ep)

    wav = make_wav("/tmp/offex_probe.wav")
    print("\ntest wav:", wav, os.path.getsize(wav), "bytes")

    up_text = None
    try:
        up_text = dump("UPLOAD via proxy", upload(BASE, wav))
    except Exception as e:
        print("proxy upload error:", e)

    server_path = None
    if up_text:
        try:
            j = json.loads(up_text)
            first = j[0] if isinstance(j, list) else j
            server_path = first if isinstance(first, str) else (first or {}).get("path")
        except Exception as e:
            print("upload parse error:", e)
    print("server_path:", server_path)

    server_path_direct = None
    try:
        t = dump("UPLOAD direct", upload(DIRECT, wav, direct_headers))
        j = json.loads(t)
        first = j[0] if isinstance(j, list) else j
        server_path_direct = first if isinstance(first, str) else (first or {}).get("path")
    except Exception as e:
        print("direct upload error:", e)
    print("server_path_direct:", server_path_direct)

    model = os.environ.get("PROBE_MODEL", "High quality")
    target = os.environ.get("PROBE_ENDPOINT", "/isolate_voice_bgm")

    def file_data(p, name="offex_probe.wav"):
        return {"path": p, "orig_name": name, "size": os.path.getsize(wav),
                "mime_type": "audio/wav", "meta": {"_type": "gradio.FileData"}}

    for base, sp, hdrs, tag in ((BASE, server_path, {}, "proxy"),
                                (DIRECT, server_path_direct, direct_headers, "direct")):
        if not sp:
            print("skip %s (no server path)" % tag)
            continue
        try:
            out = call_rest(base, target, {"data": [file_data(sp), model]}, hdrs,
                            label="%s %s model=%r" % (tag, target, model))
            summarise_result(out, "%s %s" % (tag, target))
        except Exception as e:
            print("call_rest error (%s):" % tag, e)
        try:
            out2 = call_rest(base, "/process_audio", {"data": [file_data(sp), 0.02]}, hdrs,
                             label="%s /process_audio" % tag)
            summarise_result(out2, "%s /process_audio" % tag)
        except Exception as e:
            print("process call error (%s):" % tag, e)

    hr("DONE")


if __name__ == "__main__":
    main()
