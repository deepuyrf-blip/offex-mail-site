# Offex Audio — Android app (`online.offexaudio.app`)

A WebView-based Android app for the Offex Audio service (offexmail.online), with its own
purpose-built UI. Built by a dedicated generator set so the mail app's
build (`android.yml`, `gn_a…gn_af`) is completely untouched.

- **Workflow:** `.github/workflows/android-audio.yml`
- **Generators:** `gna_1.py` … `gna_6.py` (repo root) → emit `android-audio/`
- **UI shell:** `audioapp/assets/offex_audio_ui.html` (self-contained; CSS/SVG/JS inline).
  This is the app's **own** design — the dark futuristic UI with three tool tabs
  (Remove Silence / Enhance Audio / Voice-BGM) plus History and More. It is **not**
  the website.
- **Vendored:** `audioapp/assets/gradio_client.js` (a build of `@gradio/client`),
  `audioapp/assets/audio-engine.js` (the offline in-browser fallback engine)
- **Package / version:** `online.offexaudio.app` / versionName `1.3` (versionCode 4)

## Backend (how the tools really work)

The app's own custom UI page is **hosted on the site itself** (committed as
`audio/app-ui.html`, published by the audio Pages project) and the WebView
loads it from:

    https://offexmail.online/app-ui

Loading it from the site means the page shares the site's **origin** with the
`/hf` proxy and `/health`, so its ordinary `fetch`/`XHR`/`WebSocket` calls are
**same-origin** - no CORS problem (the v1.2 build served the page from
`https://appassets.androidplatform.net` and called the proxy cross-origin,
which was blocked). The page then runs the **real Gradio client flow** against
the same `/hf` proxy the website uses:

| Purpose | URL |
| --- | --- |
| Health check (Live badge) | `https://offexmail.online/health` |
| Gradio proxy (connect, upload, submit, files) | `https://offexmail.online/hf` |
| Upload endpoint | `https://offexmail.online/hf/gradio_api/upload` |
| Result file | `https://offexmail.online/hf/gradio_api/file=<path>` |

Flow: `Client.connect(proxy)` → POST the file to `/gradio_api/upload` (with **real**
`xhr.upload` progress) → `client.submit(endpoint, inputs)` → stream `status`
progress → resolve the result file URL. Endpoints used: `/process_audio`,
`/enhance_audio`, `/isolate_voice_bgm`. Remove Silence default threshold is **0.02**.

The Cloudflare proxy injects the HF token server-side, so there is **no HF token
inside the app** and no CORS problem. When the backend is offline, Remove Silence
and Enhance Audio fall back to the bundled in-browser `audio-engine.js`;
Voice/BGM isolation requires the server.

## Remote config the panel should serve

The app reads its config from:

    https://api.mytemp-mail.online/api/app-config

All keys are optional; anything missing falls back to built-in defaults.

```json
{
  "appearance": {
    "accent": "#6366f1",
    "accent2": "#22d3ee",
    "gradient_start": "#6366f1",
    "gradient_end": "#d946ef",
    "radius": 22,
    "hero_title": "Offex Audio",
    "hero_tagline": "Audio Studio"
  },
  "ads": {
    "banner": "ca-app-pub-.../...",
    "interstitial": "ca-app-pub-.../...",
    "rewarded": "ca-app-pub-.../...",
    "app_open": "ca-app-pub-.../...",
    "native": "ca-app-pub-.../..."
  },
  "flags": {
    "show_banner_ad": true,
    "show_history": true,
    "show_features": true
  },
  "update": { "latest": "1.2", "url": "https://.../OffexAudio.apk", "force": false },
  "banner": { "on": false, "text": "", "url": "" },
  "announcement": { "on": false, "text": "" },
  "endpoints": {
    "health": "https://offexmail.online/health",
    "proxy": "https://offexmail.online/hf"
  }
}
```

While the panel is not extended, the app ships Google's **official AdMob TEST unit ids**:

| Placement | Test unit |
| --- | --- |
| App id | `ca-app-pub-3940256099942544~3347511713` |
| Banner | `ca-app-pub-3940256099942544/6300978111` |
| Interstitial | `ca-app-pub-3940256099942544/1033173712` |
| Rewarded | `ca-app-pub-3940256099942544/5224354917` |
| App-open | `ca-app-pub-3940256099942544/9257395921` |
| Native | `ca-app-pub-3940256099942544/2247696110` |

Endpoints the app may call (best-effort, never blocking):

- `POST https://api.mytemp-mail.online/api/device` — FCM token registration
- `POST https://api.mytemp-mail.online/api/audio-history` — job history reporting
