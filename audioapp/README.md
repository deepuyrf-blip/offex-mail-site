# Offex Audio — Android app (`online.offexaudio.app`)

A WebView-based Android app for the Offex Audio website (offexmail.online), mirroring the
architecture of the Offex Mail app. Built by a dedicated generator set so the mail app's
build (`android.yml`, `gn_a…gn_af`) is completely untouched.

- **Workflow:** `.github/workflows/android-audio.yml`
- **Generators:** `gna_1.py` … `gna_6.py` (repo root) → emit `android-audio/`
- **UI shell:** `audioapp/assets/offex_audio_ui.html` (self-contained; CSS/SVG/JS inline)
- **Vendored:** `audioapp/assets/gradio_client.js` (a build of `@gradio/client`),
  `audioapp/assets/audio-engine.js` (the site's in-browser fallback engine)
- **Package / version:** `online.offexaudio.app` / versionName `1.0` (versionCode 1)

## Backend

The app reaches the audio backend through the **same `/hf/*` proxy the website uses**:

| Purpose | URL |
| --- | --- |
| Health check (Live badge) | `https://offexmail.online/health` |
| Gradio proxy (jobs, uploads, files) | `https://offexmail.online/hf` |

Every request to those hosts is served natively by `MainActivity.BackendProxy`
(`shouldInterceptRequest`), so there is **no CORS problem and no HF token inside the app** —
the Cloudflare proxy adds the token from its own environment variables.

When the backend is offline, Remove Silence and Enhance Audio fall back to the bundled
in-browser `audio-engine.js`. Voice/BGM isolation requires the server.

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
  "update": { "latest": "1.0", "url": "https://.../OffexAudio.apk", "force": false },
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
