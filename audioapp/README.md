# Offex Audio — Android app (`online.offexaudio.app`)

A WebView-based Android app for the Offex Audio website (offexmail.online). Built by a
dedicated generator set so the mail app's build (`android.yml`, `gn_a…gn_af`) is
completely untouched.

- **Workflow:** `.github/workflows/android-audio.yml`
- **Generators:** `gna_1.py` … `gna_6.py` (repo root) → emit `android-audio/`
- **Package / version:** `online.offexaudio.app` / versionName `1.1` (versionCode 2)

## How the app works (v1.1)

The WebView loads the **real audio website** — `https://offexmail.online` — so the tools
run through the **genuine Gradio / Hugging Face flow** the website uses: real upload
progress, real server-side processing, real results, the real default silence value and
the site's own Live / Not-connected badge. The app does **not** fake any of this.

Around the WebView sits a **native shell**:

- **Bottom tab bar** — Remove Silence / Enhance Audio / Voice-BGM scroll the loaded page to
  the matching tool section (JS `scrollIntoView`); History and More open native panels.
- **File chooser** — `WebChromeClient.onShowFileChooser` → `ACTION_OPEN_DOCUMENT`
  (`audio/*`, `video/*`) with a persisted read grant for the picked URI.
- **Downloads** — (a) the page's finished blob is captured in JS and written to the public
  **Downloads** folder via MediaStore; (b) any real `http(s)` link the page triggers is
  saved with `DownloadManager` (`DIRECTORY_DOWNLOADS`, correct mime); (c) a native
  **Save result** button saves the latest result URL.
- **Notifications** — FCM (`FcmService`) plus local job alerts through `Notifier`, behind
  the mandatory POST_NOTIFICATIONS gate.
- **History** — local store of finished jobs with re-download.
- **Ads** — AdMob banner / interstitial / rewarded / app-open / native.
- **Languages** — English, Hindi, Spanish, Portuguese, Arabic (RTL), Russian, Indonesian.

A tiny bundled `assets/offline.html` is shown only if the live site cannot be reached; it
carries no job logic and simply reloads the site.

### What was removed in v1.1

The old build loaded a bundled `file://` HTML shell and served every backend request
natively through `MainActivity.BackendProxy` (`shouldInterceptRequest`). That broke the
Gradio client's real fetch / WebSocket / upload flow, so no genuine job ever ran and the UI
reported an instant fake "job finished". The shell, the interception path and the fake job
logic are all gone.

## Backend

The loaded site reaches the audio backend through its own **`/hf/*` proxy** — the app does
not talk to the backend directly and embeds **no HF token**:

| Purpose | URL |
| --- | --- |
| Gradio proxy (jobs, uploads, files) | `https://offexmail.online/hf` |
| Health / Live badge (rendered by the site) | `https://offexmail.online/health` |

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
  "update": { "latest": "1.1", "url": "https://.../OffexAudio.apk", "force": false },
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
