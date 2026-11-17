# WaveFly YT

**A YouTube-only music and video downloader for Android, with a built-in player, library manager and an optional YouTube sign-in.**

WaveFly YT downloads songs (MP3) and videos (MP4) from YouTube links, playlists or searches, saves them straight into your phone's `Download/WaveFly` folder and lets you browse, play, tag and organize them without leaving the app. The interface is available in **Portuguese, English and Spanish**.

> For personal use only. Download content you have the right to download and respect YouTube's Terms of Service and copyright law.

## Features

- **Download from YouTube**: paste one or many links, whole playlists, or use the built-in search.
- **MP3 or MP4**: audio is converted to MP3 with embedded cover art and tags; video is merged into MP4.
- **Smart download queue**: parallel downloads and conversions, retries with back-off, and an automatic *brake* that slows down and then ramps back up when YouTube asks for a "not a bot" confirmation.
- **Battery-friendly**: optional conditions (Wi-Fi only, charging only, minimum battery level), a cap on song length, and thermal/battery readings in a built-in report.
- **Library**: folders (playlists), loose files, search and sorting, tag editing, duplicate finder, zip export, delete files or whole folders.
- **Built-in player**: background playback and a system media notification with cover art, previous / ±N seconds / play-pause / next and a draggable progress bar. Long tracks resume where you stopped.
- **Optional YouTube sign-in**: used only as a last resort on stubborn blocks. Cookies stay on the device.
- **Self-maintenance**: the app checks GitHub Releases for new app versions and can fetch a newer `yt-dlp` from PyPI without a new APK.
- **No ads, no accounts, no analytics.**

## How it works

WaveFly YT is a small web app running inside an Android app:

```
MainActivity (WebView, full screen)
      │  http://127.0.0.1:8773/        JS bridge "WF"
      ▼                                     ▲
PythonService (foreground service) ── Chaquopy ──► Python 3.11
      │                                   ├─ waveflysite.py   engine + HTML/CSS/JS UI + HTTP API
      │                                   ├─ wavefly_ui.py    i18n (pt/en/es), settings, help, developer panel
      │                                   ├─ wavefly_android.py  Android-only patches and player bridge
      │                                   └─ app_entry.py     bootstrap, yt-dlp updater
      └─ media notification + MediaSession (system player card)
```

- **Android layer (Java, `app/src/main/java/com/wavefly/app/`)**
  - `MainActivity`: hosts the WebView and exposes the `WF` JavaScript bridge (player state, preferences, login, folder access).
  - `PythonService`: keeps the Python server alive while downloading or playing, builds the media notification, owns the `MediaSession` (cover art, seek bar, transport controls) and handles notification actions.
  - `LoginActivity`: optional Google/YouTube sign-in in a WebView; exports cookies to a private file.
  - `FfmpegSetup`: unpacks the bundled `ffmpeg` binary used for MP3 conversion and merging video+audio.
  - `Atualizador`: looks for newer releases on GitHub and installs them with one tap.
  - `Estado`, `Idioma`, `SplashView`: device state (battery, temperature, network), language/preferences, animated splash screen.
- **Python layer (`app/src/main/python/`)**
  - `waveflysite.py` (the engine): a tiny local HTTP server with a JSON API (`/api/baixar`, `/api/buscar`, `/api/arquivos`, `/api/apagar`, `/api/audio`, `/api/capa`, …), the download queue and rate limiter, `yt-dlp` integration, MP3 conversion and tagging (`mutagen`), cover extraction, library listing, duplicate detection, zip export, and the whole single-page UI.
  - `wavefly_ui.py`: translations (exact-text dictionary plus regex patterns applied by a DOM walker), settings screens, help overlay and the developer panel/report.
  - `wavefly_android.py`: patches applied on top of the engine at startup (player ↔ notification bridge, small UI fixes for mobile).
  - `app_entry.py`: starts the server, wires `ffmpeg`, loads a newer `yt-dlp` wheel if one was downloaded, and exposes helpers to the Java side.

### Dealing with YouTube blocks

YouTube sometimes answers with "Sign in to confirm you're not a bot". The app treats that (and only that) as a block: the queue pauses for a few minutes, the mode drops back to normal speed, and after the first success it ramps up gently (fewer parallel jobs and longer gaps for a short while). Requests are paced with a jittered gap. Cookies from the optional sign-in are only used on late retries, because they can break the default clients.

## Build

Requirements: JDK 17, Android SDK (compileSdk 34), Gradle 8.5, Python 3.11 on the build machine (for Chaquopy).

```bash
gradle assembleRelease
```

Notes:
- ABI: `arm64-v8a` only; `minSdk 27`; `targetSdk 28` on purpose, so the bundled `ffmpeg` can run and files can be written to `Download/WaveFly` (the app is distributed as an APK, not through the Play Store).
- Python dependencies (installed by Chaquopy): `yt-dlp`, `mutagen`, `certifi`. `ffmpeg` comes from `youtubedl-android`.
- Signing keys are never stored in the repository. The release build reads `WAVEFLY_KEYSTORE` and `WAVEFLY_KEYSTORE_PASSWORD` from the environment.

## Releases and CI

`.github/workflows/build.yml` builds a signed APK on every push:

- Push to `main` → a normal release `vX.Y.Z` (marked *latest*).
- Push to a branch named `ajustes-*` → a pre-release `teste-N` for testing.

The signing key comes from the repository secrets `WAVEFLY_KEYSTORE_BASE64` (PKCS12 file, base64) and `WAVEFLY_KEYSTORE_PASSWORD`. The release body carries `versionCode: N`; the in-app updater picks the release with the highest `versionCode` and ignores pre-releases unless test updates are enabled.

## Privacy

Everything runs on the device. The app talks to YouTube (through `yt-dlp`), to GitHub (to look for updates) and to PyPI (to refresh `yt-dlp`). Sign-in cookies, queue and settings stay in the app's private storage.

## Project status

Android only, YouTube only. A Windows build is planned for later.
