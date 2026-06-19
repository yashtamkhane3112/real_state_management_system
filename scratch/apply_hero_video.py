import os

html_path = "E:/PropVista_Final/templates/home.html"
js_path = "E:/PropVista_Final/static/js/app.js"
css_path = "E:/PropVista_Final/static/css/app.css"

# 1. Update templates/home.html
with open(html_path, "r", encoding="utf-8") as f:
    home_html = f.read()

# Replace the lp-cinematic section with the fullscreen looping video hero section
old_cinematic_sec = """<section class="lp-cinematic" id="cinematic-container" aria-label="Cinematic property presentation" style="height: 600vh;">
  <div class="lp-cinematic__sticky" id="cinematic-sticky">
    <!-- Cinematic Image Story Stack -->
    <div class="lp-story-wrapper">
      <img class="lp-story-img active" src="{% static 'images/story-frames/property_000.jpg' %}" alt="Story Frame 1" fetchpriority="high">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_010.jpg' %}" alt="Story Frame 2">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_020.jpg' %}" alt="Story Frame 3">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_030.jpg' %}" alt="Story Frame 4">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_040.jpg' %}" alt="Story Frame 5">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_050.jpg' %}" alt="Story Frame 6">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_060.jpg' %}" alt="Story Frame 7">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_070.jpg' %}" alt="Story Frame 8">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_080.jpg' %}" alt="Story Frame 9">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_090.jpg' %}" alt="Story Frame 10">
      <img class="lp-story-img" src="{% static 'images/story-frames/property_099.jpg' %}" alt="Story Frame 11">
    </div>
    
    <!-- Luxury vignette overlay -->
    <div class="lp-cinematic__vignette"></div>
    
    <!-- Subtle luxury scroll indicator -->
    <div class="lp-cinematic__hint" id="cinematic-hint">
      <span class="lp-cinematic__hint-text">Scroll to explore the property</span>
      <div class="lp-cinematic__hint-line"></div>
    </div>
  </div>
</section>"""

new_hero_sec = """<section class="pv-hero pm-hero">
  <video class="pv-hero-canvas" autoplay muted loop playsinline preload="auto" aria-hidden="true" style="width: 100%; height: 100%; object-fit: cover; pointer-events: none;">
    <source src="{% static 'videoplayback.mp4' %}" type="video/mp4">
  </video>
  <div class="container pv-hero-content pm-hero-content">
    <div class="pm-hero-copy">
      <span class="pv-eyebrow reveal"><i class="bi bi-buildings"></i> INTELLIGENT PROPERTY PLATFORM</span>
      <h1 class="reveal">Real Estate Operations <span class="pv-hero-accent">Unified.</span></h1>
      <p class="pv-hero-copy reveal">Discover, manage, and close premium property opportunities from one intelligent platform.</p>
      
      <!-- Trust Indicators / Feature Chips -->
      <div class="d-flex flex-wrap justify-content-center gap-3 pm-feature-chips-container reveal">
        <span class="pv-hero-chip"><i class="bi bi-cpu"></i> AI Recommendations</span>
        <span class="pv-hero-chip"><i class="bi bi-arrow-repeat"></i> Lifecycle Tracking</span>
        <span class="pv-hero-chip"><i class="bi bi-graph-up-arrow"></i> Advanced Analytics</span>
      </div>

      <form class="pm-command-search pv-glass reveal" action="{% url 'properties:list' %}">
        <div>
          <label>Location</label>
          <input name="q" class="form-control" placeholder="City, locality, landmark">
        </div>
        <div>
          <label>Asset type</label>
          <select name="property_type" class="form-select">
            <option value="">All properties</option>
            <option value="apartment">Apartment</option>
            <option value="villa">Villa</option>
            <option value="house">House</option>
            <option value="commercial">Commercial</option>
          </select>
        </div>
        <div>
          <label>Budget</label>
          <select name="max_price" class="form-select">
            <option value="">Any budget</option>
            <option value="10000000">Under 1 Cr</option>
            <option value="25000000">Under 2.5 Cr</option>
            <option value="50000000">Under 5 Cr</option>
          </select>
        </div>
        <button class="pv-btn pv-btn-primary" type="submit"><i class="bi bi-search"></i> Open inventory</button>
      </form>

      <div class="pm-filter-chips reveal" aria-label="Popular filters">
        <a class="chip" href="{% url 'properties:list' %}?property_type=apartment"><i class="bi bi-building"></i> Apartment</a>
        <a class="chip" href="{% url 'properties:list' %}?max_price=10000000"><i class="bi bi-currency-rupee"></i> Under 1 Cr</a>
        <a class="chip" href="{% url 'properties:list' %}?property_type=villa"><i class="bi bi-house-heart"></i> Villa</a>
        <a class="chip" href="{% url 'properties:list' %}?sort=popular"><i class="bi bi-stars"></i> Popular</a>
      </div>
    </div>
  </div>
</section>"""

if old_cinematic_sec in home_html:
    home_html = home_html.replace(old_cinematic_sec, new_hero_sec)
else:
    # Try normalized
    home_html_norm = home_html.replace("\r\n", "\n")
    old_cinematic_sec_norm = old_cinematic_sec.replace("\r\n", "\n")
    if old_cinematic_sec_norm in home_html_norm:
        home_html = home_html_norm.replace(old_cinematic_sec_norm, new_hero_sec)
    else:
        print("Error: Cinematic section markup not matched in home.html!")

with open(html_path, "w", encoding="utf-8") as f:
    f.write(home_html)
print("home.html updated with video hero copy.")


# 2. Update static/js/app.js (remove initCinematicFilm and its listener call)
with open(js_path, "r", encoding="utf-8", errors="replace") as f:
    js_content = f.read()

# Replace the function call on DOMContentLoaded
js_content = js_content.replace("    // Cinematic scroll film\n    initCinematicFilm();\n", "")
js_content = js_content.replace("    // Cinematic scroll film\r\n    initCinematicFilm();\r\n", "")

# Search and remove the initCinematicFilm function definition
js_func_target = """  function initCinematicFilm() {
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

if js_func_target in js_content:
    js_content = js_content.replace(js_func_target, "")
else:
    js_content_norm = js_content.replace("\r\n", "\n")
    js_func_target_norm = js_func_target.replace("\r\n", "\n")
    if js_func_target_norm in js_content_norm:
        js_content = js_content_norm.replace(js_func_target_norm, "")
    else:
        print("Error: initCinematicFilm function definition not matched in app.js!")

with open(js_path, "w", encoding="utf-8") as f:
    f.write(js_content)
print("app.js updated, initCinematicFilm function removed.")


# 3. Update static/css/app.css (remove cinematic scroll styling)
with open(css_path, "r", encoding="utf-8", errors="replace") as f:
    css_content = f.read()

# Target selectors for cinematic frame scrubbing
cinematic_css_rules = [
""".lp-cinematic {
  position: relative;
  width: 100%;
  height: 600vh; /* scroll range of 600vh */
  background: #081024;
  overflow: visible;
}""",
""".lp-cinematic__sticky {
  position: sticky;
  top: 0;
  width: 100%;
  height: 100vh;
  overflow: hidden;
  display: flex;
  align-items: center;
  justify-content: center;
  background: #081024;
  transition: opacity 0.3s ease;
}""",
""".lp-cinematic__canvas,
.lp-cinematic__video {
  display: block;
  width: 100%;
  height: 100%;
  object-fit: cover;
}""",
""".lp-cinematic__hint {
  position: absolute;
  bottom: 3.5rem;
  left: 50%;
  transform: translateX(-50%);
  z-index: 10;
  display: flex;
  flex-direction: column;
  align-items: center;
  gap: 0.75rem;
  opacity: 0.6;
  pointer-events: none;
  transition: opacity 0.4s ease, transform 0.4s ease;
}""",
""".lp-cinematic__hint-text {
  font-family: "Manrope", "Inter", sans-serif;
  font-size: 0.72rem;
  font-weight: 700;
  letter-spacing: 0.15em;
  text-transform: uppercase;
  color: #ffffff;
  text-shadow: 0 2px 8px rgba(0, 0, 0, 0.5);
}""",
""".lp-cinematic__hint-line {
  width: 1px;
  height: 48px;
  background: linear-gradient(to bottom, #ffffff, rgba(255, 255, 255, 0));
  position: relative;
  overflow: hidden;
}""",
""".lp-cinematic__hint-line::after {
  content: "";
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  background: linear-gradient(to bottom, rgba(255, 255, 255, 0), #e8c580, rgba(255, 255, 255, 0));
  animation: lp-hint-scroll 2s cubic-bezier(0.15, 0.85, 0.45, 1) infinite;
}""",
"""/* LP Cinematic Video Vignette Overlay */
.lp-cinematic__vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: radial-gradient(circle, rgba(8, 16, 36, 0) 35%, rgba(8, 16, 36, 0.45) 85%);
  z-index: 2;
}""",
"""/* ================================================================
   PropVista V8 Cinematic Image Story Experience
   ================================================================ */
.lp-story-wrapper {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  overflow: hidden;
  z-index: 1;
}

.lp-story-img {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  object-fit: cover;
  opacity: 0;
  transform: scale(1.00);
  transform-origin: center;
  will-change: opacity, transform;
  transition: opacity 0.4s ease-out;
}

.lp-story-img.active {
  opacity: 1;
}

.lp-cinematic__vignette {
  position: absolute;
  top: 0;
  left: 0;
  width: 100%;
  height: 100%;
  pointer-events: none;
  background: linear-gradient(180deg, rgba(15, 23, 42, 0.15), rgba(15, 23, 42, 0.30));
  z-index: 2;
}"""
]

css_content_norm = css_content.replace("\r\n", "\n")
for rule in cinematic_css_rules:
    rule_norm = rule.replace("\r\n", "\n")
    if rule_norm in css_content_norm:
        css_content_norm = css_content_norm.replace(rule_norm, "")
        print(f"Removed CSS rule: {rule[:30]}...")

with open(css_path, "w", encoding="utf-8") as f:
    f.write(css_content_norm)
print("app.css updated, dead cinematic CSS code cleaned up.")
