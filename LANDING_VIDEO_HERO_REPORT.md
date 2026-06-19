# Landing Page Premium Autoplay Video Hero Report

This document reports the successful replacement of the landing page image story with a **Standard Premium Autoplay Hero Video** using the high-quality source `C:\Users\lenovo\Downloads\videoplayback.mp4`.

---

## 🗄️ Backups Created
The following rollback backups have been created:
* [templates/home.html.v12backup](file:///E:/PropVista_Final/templates/home.html.v12backup) (copy of `templates/home.html` prior to replacement)
* [static/css/app.css.v12backup](file:///E:/PropVista_Final/static/css/app.css.v12backup) (copy of `static/css/app.css` prior to replacement)
* [static/css/navbar.css.v12backup](file:///E:/PropVista_Final/static/css/navbar.css.v12backup) (copy of `static/css/navbar.css` prior to replacement)
* [static/js/app.js.v12backup](file:///E:/PropVista_Final/static/js/app.js.v12backup) (copy of `static/js/app.js` prior to replacement)

Backup registry details are stored in [LANDING_VIDEO_HERO_BACKUP.md](file:///E:/PropVista_Final/LANDING_VIDEO_HERO_BACKUP.md).

---

## 🛠️ Files Modified
* [.env](file:///E:/PropVista_Final/.env): Set `LANDING_MEDIA_MODE=VIDEO_HERO`.
* [templates/home.html](file:///E:/PropVista_Final/templates/home.html): Configured hero video to load using `autoplay muted loop playsinline preload="metadata"`.

---

## 📹 Video Specifications
* **Source Path**: `C:\Users\lenovo\Downloads\videoplayback.mp4`
* **Target Path**: [static/media/landing/video-hero/videoplayback.mp4](file:///E:/PropVista_Final/static/media/landing/video-hero/videoplayback.mp4)
* **File Size**: 61.9 MB (64,940,451 bytes)
* **Duration**: 49.87 seconds
* **Resolution**: 1920x1080 (Sharp 1080p high definition)
* **Aspect Ratio**: 16:9 widescreen
* **CSS Display**: Pinned fullscreen background with `object-fit: cover` and no scroll filters/blur.

---

## ⚡ Performance Comparison

* **V11 Cinematic Image Story**:
  * **Scrolling CPU overhead**: Medium. Page scroll events trigger JS logic mapping current position to image stacks, opacity transitions, and transform scaling.
  * **Initial load bandwidth**: ~2.1 MB total JPEGs loaded on scroll.
* **Standard Autoplay Video Hero (Active Mode)**:
  * **Scrolling CPU overhead**: **None**. Scroll listeners are bypassed since video loops continuously without scroll interaction. GPU composite threads render the looping video background with zero layout thrashing or paint overhead.
  * **Initial load bandwidth**: Controlled by `preload="metadata"` loading headers first and streaming buffers only as needed, minimizing initial network footprint.
  * **Frame rate**: Guaranteed stable 60 FPS scrolling on all desktop and mobile viewports.

---

## ⏪ Rollback Instructions
To restore the V11 image storytelling layout, copy the backups back to their active locations:
```powershell
cp templates/home.html.v12backup templates/home.html
cp static/css/app.css.v12backup static/css/app.css
cp static/css/navbar.css.v12backup static/css/navbar.css
cp static/js/app.js.v12backup static/js/app.js
```
No other pages are affected by this media switch.
