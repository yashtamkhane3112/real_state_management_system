(function () {
  const qs = (s, root = document) => root.querySelector(s);
  const qsa = (s, root = document) => Array.from(root.querySelectorAll(s));

  function navbar() {
    const nav = qs("[data-navbar]");
    const toggle = qs("[data-mobile-nav]");
    const links = qs("[data-nav-links]");
    if (!nav) return;
    // Scroll handler for transparency and glass effects
    const sync = () => {
      const scrolled = window.scrollY > 12;
      nav.classList.toggle("is-scrolled", scrolled);
      nav.classList.toggle("navbar-scrolled", scrolled);
      
      // Update global body class for child component reactivity
      document.body.classList.toggle("navbar-scrolled", scrolled);
    };
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    
    if (toggle && links) {
      toggle.addEventListener("click", () => {
        const isOpen = links.classList.toggle("is-open");
        nav.classList.toggle("navbar-open", isOpen);
        
        const icon = toggle.querySelector("i");
        if (icon) {
          icon.className = isOpen ? "bi bi-x fs-4" : "bi bi-list fs-4";
        }
        
        if (window.gsap) {
          if (isOpen) {
            gsap.fromTo(links.children, 
              { x: -16, opacity: 0 }, 
              { x: 0, opacity: 1, stagger: 0.04, duration: 0.3, ease: "power2.out" }
            );
          }
        }
      });
    }
  }

  function gsapMotion() {
    if (!window.gsap) return;
    gsap.registerPlugin(window.ScrollTrigger);
    gsap.from("body", { opacity: 0, duration: .55, ease: "power2.out" });
    gsap.from(".pv-navbar", { y: -10, opacity: 0, duration: .8, ease: "power2.out" });
    qsa(".reveal:not(.no-reveal), .pv-card:not(.no-reveal), .property-card-premium:not(.no-reveal)").forEach((el) => {
      gsap.from(el, {
        y: 14,
        duration: .95,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 88%" }
      });
    });
    qsa("[data-counter]").forEach((el) => {
      const target = Number(el.dataset.counter || el.textContent.replace(/[^\d.]/g, "")) || 0;
      const suffix = el.dataset.suffix || "";
      const prefix = el.dataset.prefix || "";
      const obj = { value: 0 };
      gsap.to(obj, {
        value: target,
        duration: 1.5,
        ease: "power2.out",
        scrollTrigger: { trigger: el, start: "top 90%" },
        onUpdate: () => {
          el.textContent = prefix + Math.round(obj.value).toLocaleString() + suffix;
        }
      });
    });
  }

  function tiltCards() {
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;
    qsa("[data-tilt]").forEach((card) => {
      if (card.dataset.tiltReady === "true") return;
      card.dataset.tiltReady = "true";
      const move = (e) => {
        const r = card.getBoundingClientRect();
        const x = (e.clientX - r.left) / r.width - .5;
        const y = (e.clientY - r.top) / r.height - .5;
        card.classList.add("is-3d-active");
        card.style.setProperty("--pv-spot-x", `${Math.round((x + .5) * 100)}%`);
        card.style.setProperty("--pv-spot-y", `${Math.round((y + .5) * 100)}%`);
        card.style.setProperty("--pv-shine-x", `${x * 8}%`);
        card.style.setProperty("--pv-shine-y", `${y * 8}%`);
        if (!reduceMotion) {
          card.style.transform = `perspective(1100px) rotateY(${x * 2.8}deg) rotateX(${-y * 2.2}deg) translate3d(0,-1px,4px) scale(1.002)`;
        }
      };
      const reset = () => {
        card.classList.remove("is-3d-active");
        card.style.transform = "";
        card.style.setProperty("--pv-shine-x", "-30%");
        card.style.setProperty("--pv-shine-y", "-18%");
      };
      card.addEventListener("pointerenter", () => card.classList.add("is-3d-active"), { passive: true });
      card.addEventListener("pointermove", move, { passive: true });
      card.addEventListener("mousemove", move, { passive: true });
      card.addEventListener("pointerleave", reset, { passive: true });
      card.addEventListener("mouseleave", reset, { passive: true });
    });

  }

  function card3dMotion() {
    const selector = [
      ".pv-card",
      ".pv-glass",
      ".glass",
      ".city-tile",
      ".dashboard-hero",
      ".pipeline-col",
      ".lead-pill",
      ".map-panel",
      ".auth-card",
      ".stat-mini",
      ".activity",
      ".detail-gallery-main",
      ".detail-tile",
      ".amenity-item",
      ".listing-tools",
      ".dash-link",
      ".property-media"
    ].join(",");
    const cards = qsa(selector).filter((card) => !card.closest(".property-card-premium") && !card.matches(".filter-panel") && !card.closest(".filter-panel"));
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    cards.forEach((card, index) => {
      card.dataset.motion3d = "true";
      card.addEventListener("pointermove", (event) => {
        const rect = card.getBoundingClientRect();
        const x = (event.clientX - rect.left) / Math.max(rect.width, 1);
        const y = (event.clientY - rect.top) / Math.max(rect.height, 1);
        const rotateY = (x - .5) * 1.8;
        const rotateX = (.5 - y) * 1.5;
        card.style.setProperty("--pv-spot-x", `${Math.round(x * 100)}%`);
        card.style.setProperty("--pv-spot-y", `${Math.round(y * 100)}%`);
        card.style.setProperty("--pv-shine-x", `${(x - .5) * 6}%`);
        card.style.setProperty("--pv-shine-y", `${(y - .5) * 6}%`);
        if (!reduceMotion) {
          card.style.transform = `perspective(1000px) rotateX(${rotateX}deg) rotateY(${rotateY}deg) translate3d(0,-1px,3px)`;
        }
      }, { passive: true });

      card.addEventListener("pointerenter", () => {
        card.classList.add("is-3d-active");
      }, { passive: true });

      card.addEventListener("pointerleave", () => {
        card.classList.remove("is-3d-active");
        card.style.transform = "";
        card.style.setProperty("--pv-shine-x", "-28%");
        card.style.setProperty("--pv-shine-y", "-24%");
      }, { passive: true });

      if (window.gsap && !reduceMotion && index < 60) {
        gsap.fromTo(card,
          { rotateX: 1.2, rotateY: -1.2, z: -6 },
          {
            rotateX: 0,
            rotateY: 0,
            z: 0,
            duration: 1,
            delay: Math.min(index * .018, .28),
            ease: "power2.out",
            scrollTrigger: { trigger: card, start: "top 92%" }
          }
        );
      }
    });
  }

  function charts() {
    if (!window.Chart) {
      qsa(".dashboard-chart").forEach((canvas) => {
        const values = JSON.parse(canvas.dataset.values || "[]");
        const labels = JSON.parse(canvas.dataset.labels || "[]");
        const type = canvas.dataset.type || "line";
        const fallback = document.createElement("div");
        fallback.className = `pv-chart-fallback ${type === "doughnut" ? "is-donut" : "is-trend"}`;
        if (type === "doughnut") {
          fallback.innerHTML = `<div class="pv-chart-donut"></div><div class="pv-chart-legend">${labels.map((label, i) => `<span><b style="--i:${i}"></b>${label}</span>`).join("")}</div>`;
        } else {
          const max = Math.max(...values, 1);
          fallback.innerHTML = values.map((value, i) => `<span style="height:${Math.max(12, (value / max) * 100)}%" title="${labels[i] || ""}: ${value}"></span>`).join("");
        }
        canvas.replaceWith(fallback);
      });
      return;
    }
    qsa(".dashboard-chart").forEach((canvas) => {
      const labels = JSON.parse(canvas.dataset.labels || "[]");
      const values = JSON.parse(canvas.dataset.values || "[]");
      const type = canvas.dataset.type || "line";
      new Chart(canvas, {
        type,
        data: {
          labels,
          datasets: [{
            label: canvas.dataset.title || "Performance",
            data: values,
            borderColor: "#8b5cf6",
            backgroundColor: type === "line" ? "rgba(139,92,246,.16)" : ["#8b5cf6", "#ec4899", "#14b8a6", "#f59e0b", "#6366f1"],
            fill: true,
            tension: .42,
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          cutout: type === "doughnut" ? "62%" : undefined,
          plugins: { legend: { display: type === "doughnut", position: "bottom", labels: { color: "#475569", usePointStyle: true, boxWidth: 8 } } },
          scales: type === "doughnut" ? {} : {
            x: { grid: { display: false }, ticks: { color: "#64748b" } },
            y: { grid: { color: "#e2e8f0" }, ticks: { color: "#64748b" } }
          }
        }
      });
    });
  }

  function swiper() {
    if (!window.Swiper) {
      qsa(".property-swiper").forEach((el) => {
        const rail = qs(".swiper-wrapper", el);
        const prev = qs(".property-swiper-prev", el);
        const next = qs(".property-swiper-next", el);
        if (!rail) return;
        const step = () => Math.max(280, rail.clientWidth * .76);
        prev && prev.addEventListener("click", () => rail.scrollBy({ left: -step(), behavior: "smooth" }));
        next && next.addEventListener("click", () => rail.scrollBy({ left: step(), behavior: "smooth" }));
        rail.tabIndex = 0;
        rail.addEventListener("keydown", (event) => {
          if (event.key === "ArrowRight") rail.scrollBy({ left: step(), behavior: "smooth" });
          if (event.key === "ArrowLeft") rail.scrollBy({ left: -step(), behavior: "smooth" });
        });
      });
      return;
    }
    qsa(".property-swiper").forEach((el) => {
      new Swiper(el, {
        slidesPerView: 1.05,
        spaceBetween: 18,
        grabCursor: true,
        keyboard: { enabled: true },
        loop: qsa(".swiper-slide", el).length > 3,
        autoplay: { delay: 4200, disableOnInteraction: false, pauseOnMouseEnter: true },
        navigation: {
          prevEl: qs(".property-swiper-prev", el),
          nextEl: qs(".property-swiper-next", el)
        },
        effect: "coverflow",
        coverflowEffect: { rotate: 0, stretch: 0, depth: 90, modifier: 1.3, slideShadows: false },
        breakpoints: { 576: { slidesPerView: 1.45 }, 768: { slidesPerView: 2.35 }, 1100: { slidesPerView: 3.6 } }
      });
    });
  }

  function ambientScene() {
    const canvas = qs("#ambientScene");
    if (!canvas || !window.THREE) return;

    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    const camera = new THREE.PerspectiveCamera(42, window.innerWidth / Math.max(window.innerHeight, 1), .1, 1000);
    const root = new THREE.Group();
    const towers = new THREE.Group();
    const markers = new THREE.Group();
    const mouse = { x: 0, y: 0 };
    const reduceMotion = window.matchMedia && window.matchMedia("(prefers-reduced-motion: reduce)").matches;

    renderer.setPixelRatio(Math.min(window.devicePixelRatio || 1, 2));
    renderer.setSize(window.innerWidth, window.innerHeight, false);
    camera.position.set(0, 6.6, 30);

    scene.add(new THREE.AmbientLight(0x1a0533, 2.2));
    const key = new THREE.DirectionalLight(0xffffff, 1.2);
    key.position.set(8, 14, 10);
    const blue = new THREE.PointLight(0x818cf8, 2.5, 80);
    blue.position.set(-10, 6, 12);
    const purple = new THREE.PointLight(0xa855f7, 2.0, 70);
    purple.position.set(12, 5, -8);
    const pink = new THREE.PointLight(0xf472b6, 1.8, 60);
    pink.position.set(0, 10, 8);
    scene.add(key, blue, purple, pink);

    const glass = new THREE.MeshPhysicalMaterial({
      color: 0x1e1b4b,
      metalness: .7,
      roughness: .05,
      transmission: .3,
      transparent: true,
      opacity: .9
    });
    const primary = new THREE.MeshStandardMaterial({ color: 0x0d1225, metalness: .6, roughness: .1, transparent: true, opacity: .95 });
    const accent = new THREE.MeshStandardMaterial({ color: 0x6366f1, metalness: .8, roughness: .05, emissive: 0x4338ca, emissiveIntensity: 0.8 });
    const warm = new THREE.MeshStandardMaterial({ color: 0xa855f7, metalness: .8, roughness: .05, emissive: 0x7e22ce, emissiveIntensity: 0.8 });
    const pinkMat = new THREE.MeshStandardMaterial({ color: 0xf472b6, metalness: .8, roughness: .05, emissive: 0xbe185d, emissiveIntensity: 0.7 });
    const lineMat = new THREE.LineBasicMaterial({ color: 0x818cf8, transparent: true, opacity: .5 });

    for (let i = -8; i <= 8; i++) {
      const height = 1.3 + Math.abs(Math.sin(i * 1.35)) * 4.6;
      const width = .62 + Math.abs(Math.cos(i * 1.1)) * .42;
      const tower = new THREE.Mesh(new THREE.BoxGeometry(width, height, width), i % 4 === 0 ? warm : i % 3 === 0 ? accent : glass);
      tower.position.set(i * 1.45, height / 2 - 5.4, -9 + Math.sin(i * .8) * 2.5);
      tower.rotation.y = Math.sin(i) * .12;
      towers.add(tower);

      const cap = new THREE.Mesh(new THREE.ConeGeometry(width * .62, .32, 4), i % 3 === 0 ? primary : warm);
      cap.position.set(tower.position.x, tower.position.y + height / 2 + .18, tower.position.z);
      cap.rotation.y = Math.PI / 4;
      towers.add(cap);
    }

    for (let i = 0; i < 9; i++) {
      const marker = new THREE.Group();
      const pin = new THREE.Mesh(new THREE.ConeGeometry(.34, .9, 24), i % 2 ? accent : warm);
      const head = new THREE.Mesh(new THREE.SphereGeometry(.28, 20, 20), i % 3 === 0 ? pinkMat : i % 2 ? accent : glass);
      head.position.y = .52;
      marker.add(pin, head);
      marker.position.set(-10 + i * 2.5, -1.8 + Math.sin(i) * .65, -3 + Math.cos(i * .7) * 4);
      marker.rotation.z = Math.PI;
      markers.add(marker);
    }

    for (let i = 0; i < 4; i++) {
      const curve = new THREE.EllipseCurve(0, 0, 5.2 + i * 2.6, 1.9 + i * .9, 0, Math.PI * 2);
      const pts = curve.getPoints(96).map((p) => new THREE.Vector3(p.x, 0, p.y));
      const ring = new THREE.LineLoop(new THREE.BufferGeometry().setFromPoints(pts), lineMat);
      ring.rotation.x = Math.PI / 2;
      ring.rotation.z = i * .22;
      ring.position.set(0, -2.4 + i * .42, -6 + i * 1.2);
      root.add(ring);
    }

    const particles = new THREE.BufferGeometry();
    const positions = [];
    for (let i = 0; i < 520; i++) {
      positions.push((Math.random() - .5) * 62, Math.random() * 21 - 8, (Math.random() - .5) * 38);
    }
    particles.setAttribute("position", new THREE.Float32BufferAttribute(positions, 3));
    const points = new THREE.Points(particles, new THREE.PointsMaterial({ color: 0x818cf8, size: .04, transparent: true, opacity: .7 }));
    const pinkParticles = new THREE.BufferGeometry();
    const pinkPos = [];
    for (let i = 0; i < 200; i++) pinkPos.push((Math.random()-.5)*62, Math.random()*21-8, (Math.random()-.5)*38);
    pinkParticles.setAttribute("position", new THREE.Float32BufferAttribute(pinkPos, 3));
    const pinkPoints = new THREE.Points(pinkParticles, new THREE.PointsMaterial({ color: 0xf472b6, size: .045, transparent: true, opacity: .6 }));
    root.add(towers, markers);
    scene.add(root, points, pinkPoints);

    window.addEventListener("mousemove", (event) => {
      mouse.x = (event.clientX / window.innerWidth - .5) * 2;
      mouse.y = (event.clientY / window.innerHeight - .5) * 2;
    }, { passive: true });

    const resize = () => {
      camera.aspect = window.innerWidth / Math.max(window.innerHeight, 1);
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight, false);
    };
    window.addEventListener("resize", resize);

    function render(t) {
      const time = t || 0;
      root.rotation.y = Math.sin(time * .00018) * .13 + mouse.x * .04;
      root.rotation.x = mouse.y * .018;
      towers.children.forEach((mesh, i) => {
        mesh.position.y += Math.sin(time * .0012 + i) * .0012;
      });
      markers.children.forEach((marker, i) => {
        marker.position.y += Math.sin(time * .0015 + i) * .0028;
        marker.rotation.y += .004;
      });
      points.rotation.y = time * .00005;
      camera.position.x = mouse.x * .75;
      camera.position.y = 6.6 + mouse.y * .28;
      camera.lookAt(0, -1.2, -5.5);
      renderer.render(scene, camera);
      if (!reduceMotion) requestAnimationFrame(render);
    }

    render(0);
  }

  function cityHero() {
    const canvas = qs("#cityHero");
    if (!canvas || !window.THREE) return;
    const scene = new THREE.Scene();
    const renderer = new THREE.WebGLRenderer({ canvas, alpha: true, antialias: true });
    const camera = new THREE.PerspectiveCamera(44, window.innerWidth / Math.max(window.innerHeight, 1), .1, 1000);
    const group = new THREE.Group();
    const floaters = new THREE.Group();
    const mouse = { x: 0, y: 0 };

    renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
    renderer.setSize(window.innerWidth, window.innerHeight);
    camera.position.set(0, 7.5, 24);
    scene.add(new THREE.AmbientLight(0xffffff, 1.8));
    const sun = new THREE.DirectionalLight(0xffffff, 2.2);
    sun.position.set(8, 15, 12);
    scene.add(sun);
    const fill = new THREE.PointLight(0x2563eb, 1.4, 90);
    fill.position.set(-10, 7, 12);
    scene.add(fill);

    const glassMat = new THREE.MeshPhysicalMaterial({
      color: 0xe8f2ff,
      metalness: .5,
      roughness: .1,
      transmission: .2,
      transparent: true,
      opacity: .95
    });
    const blueMat = new THREE.MeshStandardMaterial({ color: 0x0b215b, metalness: .4, roughness: .2 });
    const accentMat = new THREE.MeshStandardMaterial({ color: 0x2563eb, metalness: .6, roughness: .1, emissive: 0x1e3a8a, emissiveIntensity: 0.6 });
    const goldMat = new THREE.MeshStandardMaterial({ color: 0xc8a45d, metalness: .6, roughness: .2, emissive: 0x4c1d95, emissiveIntensity: 0.6 });

    for (let i = -10; i <= 10; i++) {
      const h = 2.2 + Math.abs(Math.sin(i * 1.7)) * 7 + Math.random() * 2;
      const w = .85 + Math.random() * .75;
      const mesh = new THREE.Mesh(new THREE.BoxGeometry(w, h, w), i % 4 === 0 ? accentMat : i % 5 === 0 ? goldMat : glassMat);
      mesh.position.set(i * 1.25, h / 2 - 4.2, -2.5 + Math.sin(i) * 2.2);
      mesh.rotation.y = Math.sin(i) * .08;
      group.add(mesh);

      const roof = new THREE.Mesh(new THREE.ConeGeometry(w * .78, .4, 4), blueMat);
      roof.position.set(mesh.position.x, h - 3.92, mesh.position.z);
      roof.rotation.y = Math.PI / 4;
      group.add(roof);
    }

    const tower = new THREE.Group();
    const base = new THREE.Mesh(new THREE.BoxGeometry(3.2, 7.5, 3.2), blueMat);
    base.position.set(5.8, .1, 2.4);
    const wing = new THREE.Mesh(new THREE.BoxGeometry(5.8, 2.8, 2.6), glassMat);
    wing.position.set(4.4, -2.2, 2.2);
    const cap = new THREE.Mesh(new THREE.BoxGeometry(3.8, .35, 3.8), goldMat);
    cap.position.set(5.8, 4.1, 2.4);
    tower.add(base, wing, cap);
    group.add(tower);

    for (let i = 0; i < 7; i++) {
      const model = new THREE.Mesh(new THREE.BoxGeometry(1.2, .55, .9), i % 2 ? accentMat : glassMat);
      model.position.set(-9 + i * 3, 2.5 + Math.sin(i) * 1.3, 3 + Math.cos(i) * 1.5);
      model.rotation.set(.1, i * .3, .05);
      floaters.add(model);
    }
    scene.add(group, floaters);

    const particles = new THREE.BufferGeometry();
    const pts = [];
    for (let i = 0; i < 700; i++) pts.push((Math.random() - .5) * 56, Math.random() * 21 - 5, (Math.random() - .5) * 28);
    particles.setAttribute("position", new THREE.Float32BufferAttribute(pts, 3));
    scene.add(new THREE.Points(particles, new THREE.PointsMaterial({ color: 0x2563eb, size: .035, transparent: true, opacity: .5 })));

    window.addEventListener("mousemove", (event) => {
      mouse.x = (event.clientX / window.innerWidth - .5) * 2;
      mouse.y = (event.clientY / window.innerHeight - .5) * 2;
    }, { passive: true });

    function loop(t) {
      group.rotation.y = Math.sin(t * .00025) * .13 + mouse.x * .035;
      group.rotation.x = mouse.y * .015;
      floaters.children.forEach((m, i) => {
        m.position.y += Math.sin(t * .001 + i) * .0025;
        m.rotation.y += .002;
      });
      camera.position.x = Math.sin(t * .00022) * 1.5 + mouse.x * .6;
      camera.position.y = 7.5 + mouse.y * .28;
      camera.lookAt(1.8, .3, 0);
      renderer.render(scene, camera);
      requestAnimationFrame(loop);
    }
    loop(0);

    window.addEventListener("resize", () => {
      camera.aspect = window.innerWidth / Math.max(window.innerHeight, 1);
      camera.updateProjectionMatrix();
      renderer.setSize(window.innerWidth, window.innerHeight);
    });
  }

  function parsePins(el) {
    try {
      // Normalize potentially malformed JSON from template (extra/trailing commas)
      var raw = (el.dataset.pins || "[]").replace(/,\s*,/g, ",").replace(/\[\s*,/g, "[").replace(/,\s*\]/g, "]");
      return JSON.parse(raw)
        .filter((p) => p.lat && p.lng)
        .map((p) => ({ ...p, lat: Number(p.lat), lng: Number(p.lng) }));
    } catch (e) { return []; }
  }

  function pvTileLayer() {
    return L.tileLayer("https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png", {
      maxZoom: 19,
      attribution: '&copy; <a href="https://openstreetmap.org" target="_blank">OSM</a>'
    });
  }

  function pvCustomIcon(color) {
    const c = color || "#7c3aed";
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 48" width="36" height="48">
      <defs>
        <filter id="shadow" x="-20%" y="-10%" width="140%" height="130%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="rgba(0,0,0,0.28)"/>
        </filter>
      </defs>
      <path filter="url(#shadow)" d="M18 2C10.268 2 4 8.268 4 16c0 10.5 14 30 14 30S32 26.5 32 16C32 8.268 25.732 2 18 2z" fill="${c}"/>
      <circle cx="18" cy="16" r="7" fill="white" fill-opacity="0.92"/>
      <path d="M15 16l2 2 4-4" stroke="${c}" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round" fill="none"/>
    </svg>`;
    return L.divIcon({
      html: svg,
      className: "",
      iconSize: [36, 48],
      iconAnchor: [18, 48],
      popupAnchor: [0, -50]
    });
  }

  function pvPickerIcon() {
    const svg = `<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 36 48" width="36" height="48">
      <defs>
        <filter id="ps" x="-20%" y="-10%" width="140%" height="130%">
          <feDropShadow dx="0" dy="3" stdDeviation="3" flood-color="rgba(0,0,0,0.35)"/>
        </filter>
      </defs>
      <path filter="url(#ps)" d="M18 2C10.268 2 4 8.268 4 16c0 10.5 14 30 14 30S32 26.5 32 16C32 8.268 25.732 2 18 2z" fill="#0ea5e9"/>
      <circle cx="18" cy="16" r="7" fill="white" fill-opacity="0.9"/>
      <circle cx="18" cy="16" r="3.5" fill="#0ea5e9"/>
    </svg>`;
    return L.divIcon({
      html: svg,
      className: "",
      iconSize: [36, 48],
      iconAnchor: [18, 48],
      popupAnchor: [0, -50]
    });
  }

  function renderMapFallback(el, pins, title) {
    const items = pins.length ? pins : [{ title, city: "Mumbai", lat: 19.076, lng: 72.8777 }];
    el.innerHTML = `
      <div class="pv-map-fallback">
        <div class="pv-eyebrow"><i class="bi bi-map"></i> Map intelligence</div>
        <div class="mt-3">
          ${items.slice(0, 10).map((pin) => `<span class="pv-map-fallback-pin"><i class="bi bi-geo-alt-fill"></i>${pin.title || pin.city || "Property"}</span>`).join("")}
        </div>
      </div>`;
  }

  function pvPinPopup(pin, opts) {
    opts = opts || {};
    const imgHtml = pin.image
      ? `<img src="${pin.image}" class="pv-popup-img" alt="${pin.title || ""}">` : "";
    const typeHtml = pin.type
      ? `<span class="pv-popup-badge">${pin.type}</span>` : "";
    const priceHtml = pin.price
      ? `<div class="pv-popup-price">&#8377; ${Number(pin.price).toLocaleString("en-IN")}</div>`
      : `<div class="pv-popup-price">Premium asset</div>`;
    const locHtml = (pin.locality || pin.city)
      ? `<div class="pv-popup-loc"><i class="bi bi-geo-alt-fill"></i> ${pin.locality || ""}${pin.locality && pin.city ? ", " : ""}${pin.city || ""}</div>` : "";
    const linkHtml = pin.url
      ? `<a class="pv-popup-cta" href="${pin.url}">View details <i class="bi bi-arrow-right"></i></a>` : "";
    return L.popup({ maxWidth: 270, className: "pv-leaflet-popup" }).setContent(`
      <div class="pv-map-popup">
        ${imgHtml}
        <div class="pv-popup-body">
          ${typeHtml}
          <strong>${pin.title || "PropVista property"}</strong>
          ${priceHtml}
          ${locHtml}
          ${linkHtml}
        </div>
      </div>`);
  }

  function pvMarker(map, pin, opts) {
    const marker = L.marker([pin.lat, pin.lng], { icon: pvCustomIcon(opts && opts.color) });
    marker.bindPopup(pvPinPopup(pin));
    if (map) marker.addTo(map);
    return marker;
  }

  window.initListingMap = function () {
    const el = qs("#listingMap");
    if (!el) return;
    const pins = parsePins(el);
    if (!window.L || pins.length === 0) {
      renderMapFallback(el, pins, "Property market");
      return;
    }
    const center = [pins[0].lat, pins[0].lng];
    const map = L.map(el, { scrollWheelZoom: false, zoomControl: true }).setView(center, 12);
    pvTileLayer().addTo(map);

    // Use MarkerCluster if available
    const clusterGroup = window.L.markerClusterGroup
      ? L.markerClusterGroup({ maxClusterRadius: 60, showCoverageOnHover: false,
          iconCreateFunction(cluster) {
            const count = cluster.getChildCount();
            return L.divIcon({ html: `<div class="pv-cluster">${count}</div>`, className: "", iconSize: [42, 42] });
          }
        })
      : null;

    const markers = pins.map((pin) => pvMarker(clusterGroup ? null : map, pin));
    if (clusterGroup) {
      markers.forEach((m) => clusterGroup.addLayer(m));
      map.addLayer(clusterGroup);
    }
    if (markers.length > 1) {
      map.fitBounds(L.featureGroup(markers).getBounds().pad(0.12));
    }
  };

  window.initDetailMap = function () {
    const el = qs("#detailMap");
    if (!el) return;
    const pos = { lat: Number(el.dataset.lat), lng: Number(el.dataset.lng) };
    if (!window.L || !pos.lat || !pos.lng) {
      renderMapFallback(el, [{ title: el.dataset.title, lat: pos.lat, lng: pos.lng }], el.dataset.title);
      return;
    }
    const map = L.map(el, { scrollWheelZoom: false, zoomControl: true }).setView([pos.lat, pos.lng], 15);
    pvTileLayer().addTo(map);
    pvMarker(map, {
      lat: pos.lat, lng: pos.lng,
      title: el.dataset.title,
      price: el.dataset.price,
      type: el.dataset.proptype,
      image: el.dataset.image,
      locality: el.dataset.locality,
      city: el.dataset.city
    }).openPopup();
  };

  window.initLocationPicker = function () {
    const el = qs("#locationPickerMap");
    if (!el || !window.L) return;
    const latInput = qs("#id_latitude");
    const lngInput = qs("#id_longitude");
    const hint = qs("#locationPickerHint");
    const initLat = parseFloat(latInput && latInput.value) || 20.5937;
    const initLng = parseFloat(lngInput && lngInput.value) || 78.9629;
    const initZoom = (latInput && latInput.value) ? 14 : 5;

    const map = L.map(el, { scrollWheelZoom: true }).setView([initLat, initLng], initZoom);
    pvTileLayer().addTo(map);

    let marker = null;

    function placeMarker(latlng) {
      if (marker) marker.setLatLng(latlng);
      else {
        marker = L.marker(latlng, { icon: pvPickerIcon(), draggable: true }).addTo(map);
        marker.on("dragend", function (e) {
          const pos = e.target.getLatLng();
          updateInputs(pos.lat, pos.lng);
        });
      }
      updateInputs(latlng.lat, latlng.lng);
    }

    function updateInputs(lat, lng) {
      if (latInput) latInput.value = lat.toFixed(6);
      if (lngInput) lngInput.value = lng.toFixed(6);
      if (hint) hint.textContent = `📍 Selected: ${lat.toFixed(5)}, ${lng.toFixed(5)} — drag pin or click map to change`;
    }

    // If coordinates already exist (edit mode), place a marker
    if (latInput && latInput.value && lngInput && lngInput.value) {
      placeMarker({ lat: initLat, lng: initLng });
    }

    map.on("click", function (e) {
      placeMarker(e.latlng);
      map.setView(e.latlng, Math.max(map.getZoom(), 14));
    });
  };

  function phoneValidation() {
    qsa('input[name="phone"], input[id="id_phone"], input[id="phone"]').forEach((input) => {
      input.setAttribute("maxlength", "10");
      input.setAttribute("pattern", "\\d{10}");
      
      const validate = () => {
        const val = input.value;
        const cleaned = val.replace(/\D/g, '');
        if (val !== cleaned) {
          input.value = cleaned;
        }
        
        let errorDiv = input.parentNode.querySelector(".phone-error-msg");
        if (errorDiv) {
          errorDiv.remove();
        }
        
        if (input.value.length === 0) {
          input.setCustomValidity("");
        } else if (input.value.length !== 10) {
          input.setCustomValidity("Enter a valid 10-digit phone number.");
          errorDiv = document.createElement("div");
          errorDiv.className = "text-danger small mt-1 phone-error-msg";
          errorDiv.textContent = "Enter a valid 10-digit phone number.";
          input.parentNode.appendChild(errorDiv);
        } else {
          input.setCustomValidity("");
        }
      };

      input.addEventListener("input", validate);
      input.addEventListener("blur", validate);
      
      const form = input.closest("form");
      if (form) {
        form.addEventListener("submit", (e) => {
          validate();
          if (!input.checkValidity()) {
            e.preventDefault();
            input.reportValidity();
          }
        });
      }
    });
  }

  function loadingState() {
    const loader = qs("#pv-loader");
    if (loader) {
      window.addEventListener("load", () => {
        setTimeout(() => {
          loader.classList.add("is-hidden");
        }, 500);
      });
    }
  }

  function initLightbox() {
    // 1. Create lightbox markup dynamically if it doesn't exist
    if (document.getElementById("pvLightbox")) return;
    
    const lightbox = document.createElement("div");
    lightbox.className = "pv-lightbox";
    lightbox.id = "pvLightbox";
    lightbox.innerHTML = `
      <button class="pv-lightbox-close" aria-label="Close viewer" id="pvLightboxClose">&times;</button>
      <button class="pv-lightbox-nav pv-lightbox-prev" aria-label="Previous image" id="pvLightboxPrev">&lsaquo;</button>
      <div class="pv-lightbox-content">
        <img class="pv-lightbox-img" id="pvLightboxImg" src="" alt="Viewer image">
      </div>
      <button class="pv-lightbox-nav pv-lightbox-next" aria-label="Next image" id="pvLightboxNext">&rsaquo;</button>
      <div class="pv-lightbox-counter" id="pvLightboxCounter"></div>
    `;
    document.body.appendChild(lightbox);

    const closeBtn = lightbox.querySelector("#pvLightboxClose");
    const prevBtn = lightbox.querySelector("#pvLightboxPrev");
    const nextBtn = lightbox.querySelector("#pvLightboxNext");
    const mainImg = lightbox.querySelector("#pvLightboxImg");
    const counterEl = lightbox.querySelector("#pvLightboxCounter");

    let currentGallery = [];
    let currentIndex = -1;
    let isAvatarMode = false;

    function openLightbox(src, gallery = [], index = -1) {
      mainImg.src = src;
      lightbox.classList.add("is-open");
      document.body.style.overflow = "hidden"; // Prevent body scroll
      
      if (gallery.length > 0 && index !== -1) {
        isAvatarMode = false;
        currentGallery = gallery;
        currentIndex = index;
        prevBtn.style.display = "flex";
        nextBtn.style.display = "flex";
        counterEl.style.display = "block";
        updateCounter();
      } else {
        isAvatarMode = true;
        currentGallery = [];
        currentIndex = -1;
        prevBtn.style.display = "none";
        nextBtn.style.display = "none";
        counterEl.style.display = "none";
      }
      closeBtn.focus();
    }

    function closeLightbox() {
      lightbox.classList.remove("is-open");
      document.body.style.overflow = "";
      mainImg.src = "";
    }

    function navigate(direction) {
      if (isAvatarMode || currentGallery.length <= 1) return;
      currentIndex = (currentIndex + direction + currentGallery.length) % currentGallery.length;
      mainImg.src = currentGallery[currentIndex];
      updateCounter();
    }

    function updateCounter() {
      counterEl.textContent = `Image ${currentIndex + 1} of ${currentGallery.length}`;
    }

    // Click hooks
    closeBtn.addEventListener("click", closeLightbox);
    lightbox.addEventListener("click", (e) => {
      if (e.target === lightbox || e.target.classList.contains("pv-lightbox-content")) {
        closeLightbox();
      }
    });
    prevBtn.addEventListener("click", () => navigate(-1));
    nextBtn.addEventListener("click", () => navigate(1));

    // Keyboard hooks
    document.addEventListener("keydown", (e) => {
      if (!lightbox.classList.contains("is-open")) return;
      if (e.key === "Escape") {
        closeLightbox();
      } else if (e.key === "ArrowLeft") {
        navigate(-1);
      } else if (e.key === "ArrowRight") {
        navigate(1);
      }
    });

    // Mobile Swipe Support
    let touchStartX = 0;
    let touchEndX = 0;
    lightbox.addEventListener("touchstart", (e) => {
      touchStartX = e.changedTouches[0].screenX;
    }, { passive: true });
    lightbox.addEventListener("touchend", (e) => {
      touchEndX = e.changedTouches[0].screenX;
      const diff = touchEndX - touchStartX;
      if (Math.abs(diff) > 50) {
        if (diff > 0) {
          navigate(-1);
        } else {
          navigate(1);
        }
      }
    }, { passive: true });

    // Click delegates for interactive elements
    const avatarSelectors = [
      "img.pv-avatar",
      ".sidebar-profile img",
      ".pv-card img[alt='avatar']",
      ".profile-avatar img",
      "img[src*='avatars/']"
    ];

    document.addEventListener("click", (e) => {
      const clickedImg = e.target.closest("img");
      if (!clickedImg) return;

      // Avoid clicking lightbox's own image triggering it again
      if (clickedImg.id === "pvLightboxImg") return;

      // Skip any image that is explicitly marked as no-lightbox (e.g. navbar avatar)
      if (clickedImg.hasAttribute("data-no-lightbox")) return;
      if (clickedImg.closest("[data-no-lightbox]")) return;

      // 1. Is it an avatar image?
      let isAvatar = false;
      for (let sel of avatarSelectors) {
        if (clickedImg.matches(sel)) {
          isAvatar = true;
          break;
        }
      }
      
      if (isAvatar) {
        e.preventDefault();
        openLightbox(clickedImg.src);
        return;
      }

      // 2. Is it a property detail gallery image?
      const isDetailGallery = clickedImg.closest("#propertyGalleryCarousel, .gallery-tile-container, .detail-gallery-premium");
      if (isDetailGallery) {
        e.preventDefault();
        const srcs = [];
        document.querySelectorAll("#propertyGalleryCarousel .carousel-inner img, .gallery-tile-container img, .detail-gallery-premium img").forEach(img => {
          if (img.src && !srcs.includes(img.src) && img.id !== "pvLightboxImg") {
            srcs.push(img.src);
          }
        });
        const clickedSrc = clickedImg.src;
        const index = srcs.indexOf(clickedSrc);
        openLightbox(clickedSrc, srcs, index !== -1 ? index : 0);
      }
    });
  }

  document.addEventListener("DOMContentLoaded", () => {
    loadingState();
    navbar();
    gsapMotion();
    card3dMotion();
    charts();
    swiper();
    tiltCards();
    phoneValidation();
    initLightbox();
    if (window.location.pathname === "/") {
      ambientScene();
      cityHero();
    }
  });
})();
