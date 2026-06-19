import os

js_path = "E:/PropVista_Final/static/js/app.js"

with open(js_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

target = """  function initCinematicFilm() {
    const container = document.getElementById("cinematic-container");
    const sticky = document.getElementById("cinematic-sticky");
    const canvas = document.getElementById("cinematic-canvas");
    if (!container || !canvas) return;

    const ctx = canvas.getContext("2d");
    const frameCount = 300;
    const images = [];

    function getFrameUrl(index) {
      const frameNum = String(index).padStart(3, '0');
      return `/static/images/film-frames/ezgif-frame-${frameNum}.jpg`;
    }

    // Preload first frame immediately to draw on canvas
    const firstImage = new Image();
    firstImage.src = getFrameUrl(1);
    images[0] = firstImage;
    firstImage.onload = () => {
      drawFrame(0);
    };

    let targetFrame = 0;
    let currentFrame = 0;
    const ease = 0.08; // smooth lerp factor

    // Sequential lazy-loader in background
    let preloadIndex = 1;
    function preloadNext() {
      if (preloadIndex >= frameCount) return;
      if (images[preloadIndex]) {
        preloadIndex++;
        preloadNext();
        return;
      }
      const img = new Image();
      img.src = getFrameUrl(preloadIndex + 1);
      img.onload = () => {
        images[preloadIndex] = img;
        preloadIndex++;
        setTimeout(preloadNext, 5); // yield to main thread
      };
      img.onerror = () => {
        preloadIndex++;
        setTimeout(preloadNext, 5);
      };
      images[preloadIndex] = img;
    }

    setTimeout(preloadNext, 250);

    function resizeCanvas() {
      canvas.width = window.innerWidth * window.devicePixelRatio;
      canvas.height = window.innerHeight * window.devicePixelRatio;
      canvas.style.width = "100%";
      canvas.style.height = "100%";
      drawFrame(Math.round(currentFrame));
    }

    function drawFrame(index) {
      let img = images[index];
      if (!img) {
        // Priority lazy load for current frame on scroll
        img = new Image();
        img.src = getFrameUrl(index + 1);
        img.onload = () => {
          images[index] = img;
          if (Math.round(currentFrame) === index) {
            renderImage(img);
          }
        };
        images[index] = img;
      }

      if (!img.complete || img.naturalWidth === 0) {
        const closest = getClosestLoadedImage(index);
        if (closest) {
          renderImage(closest);
        }
        return;
      }
      renderImage(img);
    }

    function getClosestLoadedImage(index) {
      let left = index;
      let right = index;
      while (left >= 0 || right < frameCount) {
        if (left >= 0 && images[left] && images[left].complete && images[left].naturalWidth !== 0) {
          return images[left];
        }
        if (right < frameCount && images[right] && images[right].complete && images[right].naturalWidth !== 0) {
          return images[right];
        }
        left--;
        right++;
      }
      return null;
    }

    function renderImage(img) {
      ctx.clearRect(0, 0, canvas.width, canvas.height);

      const cw = canvas.width;
      const ch = canvas.height;
      const iw = img.width;
      const ih = img.height;

      const r = Math.min(cw / iw, ch / ih);
      let nw = iw * r;
      let nh = ih * r;

      if (nw < cw) {
        const scaleVal = cw / iw;
        nw = iw * scaleVal;
        nh = ih * scaleVal;
      }
      if (nh < ch) {
        const scaleVal = ch / ih;
        nw = iw * scaleVal;
        nh = ih * scaleVal;
      }

      // Gentle zoom and blur effects
      const rect = container.getBoundingClientRect();
      const totalScrollRange = rect.height - window.innerHeight;
      let progress = -rect.top / totalScrollRange;
      progress = Math.max(0, Math.min(1, progress));

      const zoom = 1.0 + (progress * 0.05); // 5% gentle zoom
      nw *= zoom;
      nh *= zoom;

      const x = (cw - nw) / 2;
      const y = (ch - nh) / 2;

      let blurVal = 0;
      if (progress > 0.9) {
        blurVal = ((progress - 0.9) / 0.1) * 8;
      }

      ctx.filter = blurVal > 0 ? `blur(${blurVal}px)` : 'none';
      ctx.drawImage(img, x, y, nw, nh);

      // Vignette overlay
      const gradient = ctx.createRadialGradient(
        cw / 2, ch / 2, Math.min(cw, ch) * 0.35,
        cw / 2, ch / 2, Math.max(cw, ch) * 0.85
      );
      gradient.addColorStop(0, "rgba(8, 16, 36, 0)");
      gradient.addColorStop(1, "rgba(8, 16, 36, 0.45)");
      ctx.fillStyle = gradient;
      ctx.filter = 'none'; // reset filter for vignette
      ctx.fillRect(0, 0, cw, ch);
    }

    function updateScroll() {
      const rect = container.getBoundingClientRect();
      const totalScrollRange = rect.height - window.innerHeight;
      if (totalScrollRange <= 0) return;

      let progress = -rect.top / totalScrollRange;
      progress = Math.max(0, Math.min(1, progress));

      targetFrame = progress * (frameCount - 1);

      // Fade out canvas sticky in the last 8% of scroll
      if (progress > 0.92) {
        const opacity = 1.0 - ((progress - 0.92) / 0.08);
        sticky.style.opacity = Math.max(0, opacity);
      } else {
        sticky.style.opacity = 1.0;
      }

      // Hide hint
      const hint = document.getElementById("cinematic-hint");
      if (hint) {
        hint.style.opacity = progress > 0.05 ? "0" : "0.6";
        hint.style.transform = `translate(-50%, ${progress * -30}px)`;
      }
    }

    let lastIndex = -1;
    function renderLoop() {
      const diff = targetFrame - currentFrame;
      if (Math.abs(diff) > 0.01) {
        currentFrame += diff * ease;
        const index = Math.round(currentFrame);
        if (index !== lastIndex) {
          drawFrame(index);
          lastIndex = index;
        }
      }
      requestAnimationFrame(renderLoop);
    }

    window.addEventListener("resize", resizeCanvas);
    window.addEventListener("scroll", updateScroll, { passive: true });

    resizeCanvas();
    updateScroll();
    requestAnimationFrame(renderLoop);
  }"""

replacement = """  function initCinematicFilm() {
    const container = document.getElementById("cinematic-container");
    const sticky = document.getElementById("cinematic-sticky");
    const video = document.getElementById("cinematic-video");
    if (!container || !video) return;

    let duration = 0;
    let targetProgress = 0;
    let currentProgress = 0;
    const ease = 0.06; // Lerp ease factor

    video.addEventListener("loadedmetadata", () => {
      duration = video.duration;
      updateScroll();
    });

    if (video.readyState >= 1) {
      duration = video.duration;
    }

    function updateScroll() {
      const rect = container.getBoundingClientRect();
      const totalScrollRange = rect.height - window.innerHeight;
      if (totalScrollRange <= 0) return;

      let progress = -rect.top / totalScrollRange;
      progress = Math.max(0, Math.min(1, progress));

      targetProgress = progress;

      // Fade out sticky viewport in the last 8% of scroll
      if (progress > 0.92) {
        const opacity = 1.0 - ((progress - 0.92) / 0.08);
        sticky.style.opacity = Math.max(0, opacity);
      } else {
        sticky.style.opacity = 1.0;
      }

      // Hide/reveal scroll hint based on scroll progress
      const hint = document.getElementById("cinematic-hint");
      if (hint) {
        hint.style.opacity = progress > 0.05 ? "0" : "0.6";
        hint.style.transform = `translate(-50%, ${progress * -30}px)`;
      }
    }

    function renderLoop() {
      if (duration > 0) {
        const diff = targetProgress - currentProgress;
        if (Math.abs(diff) > 0.0001) {
          currentProgress += diff * ease;
          if (currentProgress < 0) currentProgress = 0;
          if (currentProgress > 1) currentProgress = 1;

          // Smooth hardware-accelerated zoom and blur
          const zoom = 1.0 + (currentProgress * 0.05);
          let blurVal = 0;
          if (currentProgress > 0.9) {
            blurVal = ((currentProgress - 0.9) / 0.1) * 8;
          }
          video.style.transform = `scale(${zoom})`;
          video.style.filter = blurVal > 0 ? `blur(${blurVal}px)` : 'none';

          // Update video currentTime based on lerped scroll progress
          const nextTime = currentProgress * duration;
          if (!video.seeking && Math.abs(video.currentTime - nextTime) > 0.02) {
            video.currentTime = nextTime;
          }
        }
      }
      requestAnimationFrame(renderLoop);
    }

    window.addEventListener("scroll", updateScroll, { passive: true });
    updateScroll();
    requestAnimationFrame(renderLoop);
  }"""

if target in content:
    content = content.replace(target, replacement)
    with open(js_path, "w", encoding="utf-8") as f:
        f.write(content)
    print("JS updated successfully!")
else:
    # Try with raw line separator matching if system uses carriage returns
    content_norm = content.replace("\r\n", "\n")
    target_norm = target.replace("\r\n", "\n")
    replacement_norm = replacement.replace("\r\n", "\n")
    if target_norm in content_norm:
        content_norm = content_norm.replace(target_norm, replacement_norm)
        with open(js_path, "w", encoding="utf-8") as f:
            f.write(content_norm)
        print("JS updated successfully (normalized lines)!")
    else:
        print("Target JS block not found in app.js!")
