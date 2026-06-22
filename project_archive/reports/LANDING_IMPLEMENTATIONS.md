# PropVista Landing Page Media Implementations

This document registers and describes the three interchangeable homepage hero/media modes configured in PropVista.

---

## Implementation A: Original Hero Video (`VIDEO_HERO`)

An elegant, high-impact loop video overlaying the search panel, feature chips, and quick filters. Instantly engages users with autoplaying premium property cinematography.

### 📋 Specifications
* **Files Required**:
  * [templates/home.html](file:///E:/PropVista_Final/templates/home.html) (Mode-conditional block)
* **CSS Required**:
  * [static/css/app.css](file:///E:/PropVista_Final/static/css/app.css) (`.pv-hero`, `.pm-hero`, `.pv-hero-canvas`, `.pv-hero-content`, `.pm-hero-content`, `.pm-hero-copy`, `.pv-eyebrow`, `.pv-hero-accent`, `.pv-hero-chip`, `.pm-command-search`, `.pm-filter-chips`)
* **JS Required**:
  * None (purely CSS-driven autoplay loop).
* **Assets Required**:
  * [static/media/landing/video-hero/videoplayback.mp4](file:///E:/PropVista_Final/static/media/landing/video-hero/videoplayback.mp4) (Length: 49.87s, 61.9 MB H.264 video).

### 👍 Pros & 👎 Cons
* **Pros**:
  * Zero Javascript dependence.
  * Autoplays instantly with high client performance (GPU composite layers).
  * Direct access to the Search panel and navigation chips above the fold.
  * Very easy to customize and replace.
* **Cons**:
  * Media file is large (~61.9 MB) and requires decent client bandwidth.
  * Lacks the scroll-interactive engagement of Mode B or C.

---

## Implementation B: Video Scroll Scrub (`VIDEO_SCRUB`)

An immersive luxury product-page experience where the scrollbar directly controls the playback frame of a premium cinematic property film. Scrolling down scrubs the video forward, and scrolling up scrubs it backward.

### 📋 Specifications
* **Files Required**:
  * [templates/home.html](file:///E:/PropVista_Final/templates/home.html) (Mode-conditional block)
  * [static/js/app.js](file:///E:/PropVista_Final/static/js/app.js) (`initVideoScrub()`, `initLandingMedia()`)
* **CSS Required**:
  * [static/css/app.css](file:///E:/PropVista_Final/static/css/app.css) (`.lp-cinematic`, `.lp-cinematic__sticky`, `.lp-cinematic__video`, `.lp-cinematic__hint`, `.lp-cinematic__hint-text`, `.lp-cinematic__hint-line`, `.lp-cinematic__vignette`)
* **JS Required**:
  * [static/js/app.js](file:///E:/PropVista_Final/static/js/app.js) (`initVideoScrub()`): Attaches passive scroll listener, calculates scroll progress over a `700vh` scroll container, applies a linear interpolation (`ease = 0.06`) render loop via `requestAnimationFrame`, smoothly controls `video.currentTime`, and triggers scale zoom and blur filters.
* **Assets Required**:
  * [static/media/landing/video-scrub/property.mp4](file:///E:/PropVista_Final/static/media/landing/video-scrub/property.mp4) (Length: 10.00s, 4.25 MB H.264 video optimized for scrubbing).

### 👍 Pros & 👎 Cons
* **Pros**:
  * High user engagement and luxury product feel (Apple/Tesla aesthetic).
  * Video size is very small (4.25 MB) and highly optimized.
  * Extremely smooth scrolling with lerped interpolation.
* **Cons**:
  * Performance varies across mobile devices and older browsers due to video decoding/seeking limits.
  * Compression artifacts may become visible during fullscreen scaling.

---

## Implementation C: Cinematic Image Story (`IMAGE_STORY`)

A premium architectural storytelling experience using a sequence of ultra-sharp, high-detail imagery. As the user scrolls, images cross-fade with zoom and vignette adjustments, presenting the property like a cinematic photo story.

### 📋 Specifications
* **Files Required**:
  * [templates/home.html](file:///E:/PropVista_Final/templates/home.html) (Mode-conditional block)
  * [static/js/app.js](file:///E:/PropVista_Final/static/js/app.js) (`initImageStory()`, `initLandingMedia()`)
* **CSS Required**:
  * [static/css/app.css](file:///E:/PropVista_Final/static/css/app.css) (`.lp-cinematic`, `.lp-cinematic__sticky`, `.lp-story-wrapper`, `.lp-story-img`, `.lp-story-img.active`, `.lp-cinematic__hint`, `.lp-cinematic__vignette`)
* **JS Required**:
  * [static/js/app.js](file:///E:/PropVista_Final/static/js/app.js) (`initImageStory()`): Calculates scroll progress across a `600vh` scroll range, runs a lerp (`ease = 0.08`) render loop, maps progress to 11 images, handles cross-fading overlap (20% threshold), and manages hardware-accelerated zoom scaling (1.00x to 1.05x).
* **Assets Required**:
  * [static/media/landing/image-story/property_000.jpg](file:///E:/PropVista_Final/static/media/landing/image-story/property_000.jpg) to `property_099.jpg` (11 curated high-resolution frames, totaling ~2.3 MB).

### 👍 Pros & 👎 Cons
* **Pros**:
  * Stunning visual sharpness and zero compression artifacts on high-resolution displays.
  * Highly performant; utilizes image transitions and GPU scale transformations (no video decoding overhead).
  * Works perfectly across all mobile devices and browsers.
* **Cons**:
  * Requires fetching 11 separate image files (preloaded with `fetchpriority="high"` for the first image to minimize content shift).
  * Does not support arbitrary frame-rate playback like actual videos.
