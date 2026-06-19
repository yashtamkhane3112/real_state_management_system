import os

js_path = "E:/PropVista_Final/static/js/app.js"

with open(js_path, "r", encoding="utf-8", errors="replace") as f:
    content = f.read()

target = """  function initCinematicFilm() {
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

replacement = """  function initCinematicFilm() {
    const container = document.getElementById("cinematic-container");
    const sticky = document.getElementById("cinematic-sticky");
    const images = Array.from(document.querySelectorAll(".lp-story-img"));
    if (!container || !sticky || images.length === 0) return;

    let targetProgress = 0;
    let currentProgress = 0;
    const ease = 0.08; // smooth lerp factor

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
      const diff = targetProgress - currentProgress;
      if (Math.abs(diff) > 0.0001) {
        currentProgress += diff * ease;
        if (currentProgress < 0) currentProgress = 0;
        if (currentProgress > 1) currentProgress = 1;

        // Total segments (intervals between consecutive images)
        const totalSegments = images.length - 1;
        const rawIndex = currentProgress * totalSegments;
        const activeIndex = Math.min(Math.floor(rawIndex), totalSegments - 1);
        const segmentProgress = rawIndex - activeIndex;

        // Determine active and next image opacities with 20% cross-fade overlap
        let opacityActive = 1.0;
        let opacityNext = 0.0;

        if (segmentProgress > 0.8) {
          const t = (segmentProgress - 0.8) / 0.2; // 0.0 to 1.0
          opacityActive = 1.0 - t;
          opacityNext = t;
        } else {
          opacityActive = 1.0;
          opacityNext = 0.0;
        }

        // Apply scale zoom (1.00 to 1.05) and opacity to images
        for (let i = 0; i < images.length; i++) {
          const img = images[i];
          if (i === activeIndex) {
            img.style.opacity = opacityActive;
            const scale = 1.00 + (segmentProgress * 0.05);
            img.style.transform = `scale(${scale.toFixed(4)})`;
            img.style.visibility = opacityActive > 0.001 ? "visible" : "hidden";
          } else if (i === activeIndex + 1) {
            img.style.opacity = opacityNext;
            const scale = 1.00 + (segmentProgress * 0.05);
            img.style.transform = `scale(${scale.toFixed(4)})`;
            img.style.visibility = opacityNext > 0.001 ? "visible" : "hidden";
          } else {
            img.style.opacity = 0;
            img.style.transform = "scale(1.00)";
            img.style.visibility = "hidden";
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
