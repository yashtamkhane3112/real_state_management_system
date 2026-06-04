(function () {
  const qs = (s, root = document) => root.querySelector(s);
  const qsa = (s, root = document) => Array.from(root.querySelectorAll(s));

  function navbar() {
    const nav = qs("[data-navbar]");
    const toggle = qs("[data-mobile-nav]");
    const links = qs("[data-nav-links]");
    if (!nav) return;
    const sync = () => nav.classList.toggle("is-scrolled", window.scrollY > 12);
    sync();
    window.addEventListener("scroll", sync, { passive: true });
    if (toggle && links) {
      toggle.addEventListener("click", () => {
        links.classList.toggle("is-open");
        if (window.gsap) gsap.fromTo(links.children, { x: -12, opacity: 0 }, { x: 0, opacity: 1, stagger: .04, duration: .25 });
      });
    }
  }

  function gsapMotion() {
    if (!window.gsap) return;
    gsap.registerPlugin(window.ScrollTrigger);
    gsap.from("body", { opacity: 0, duration: .55, ease: "power2.out" });
    gsap.from(".pv-navbar", { y: -10, opacity: 0, duration: .8, ease: "power2.out" });
    qsa(".reveal, .pv-card, .property-card-premium").forEach((el) => {
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
    const cards = qsa(selector).filter((card) => !card.closest(".property-card-premium"));
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
    if (!window.Chart) return;
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
            borderColor: "#2563eb",
            backgroundColor: type === "line" ? "rgba(37,99,235,.12)" : ["#2563eb", "#0b215b", "#c8a45d", "#7c3aed", "#14b8a6"],
            fill: true,
            tension: .42,
            borderWidth: 3
          }]
        },
        options: {
          responsive: true,
          maintainAspectRatio: false,
          plugins: { legend: { display: false } },
          scales: type === "doughnut" ? {} : {
            x: { grid: { display: false }, ticks: { color: "#64748b" } },
            y: { grid: { color: "#e2e8f0" }, ticks: { color: "#64748b" } }
          }
        }
      });
    });
  }

  function swiper() {
    if (!window.Swiper) return;
    qsa(".property-swiper").forEach((el) => {
      new Swiper(el, {
        slidesPerView: 1.05,
        spaceBetween: 18,
        grabCursor: true,
        effect: "coverflow",
        coverflowEffect: { rotate: 0, stretch: 0, depth: 90, modifier: 1.3, slideShadows: false },
        breakpoints: { 768: { slidesPerView: 2.2 }, 1100: { slidesPerView: 3.35 } }
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
    const pink = new THREE.MeshStandardMaterial({ color: 0xf472b6, metalness: .8, roughness: .05, emissive: 0xbe185d, emissiveIntensity: 0.7 });
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
      const head = new THREE.Mesh(new THREE.SphereGeometry(.28, 20, 20), i % 2 ? accent : glass);
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
      color: 0x0f172a,
      metalness: .5,
      roughness: .1,
      transmission: .2,
      transparent: true,
      opacity: .95
    });
    const blueMat = new THREE.MeshStandardMaterial({ color: 0x09090b, metalness: .4, roughness: .2 });
    const accentMat = new THREE.MeshStandardMaterial({ color: 0x3b82f6, metalness: .6, roughness: .1, emissive: 0x1e3a8a, emissiveIntensity: 0.6 });
    const goldMat = new THREE.MeshStandardMaterial({ color: 0x8b5cf6, metalness: .6, roughness: .2, emissive: 0x4c1d95, emissiveIntensity: 0.6 });

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

  window.initListingMap = function () {
    const el = qs("#listingMap");
    if (!el || !window.google) return;
    const pins = JSON.parse(el.dataset.pins || "[]").filter((p) => p.lat && p.lng);
    const center = pins[0] || { lat: 19.076, lng: 72.8777 };
    const map = new google.maps.Map(el, {
      center,
      zoom: 11,
      disableDefaultUI: true,
      zoomControl: true,
      styles: [{ featureType: "all", elementType: "geometry", stylers: [{ color: "#f8fafc" }] }, { featureType: "water", stylers: [{ color: "#dbeafe" }] }]
    });
    pins.forEach((p) => {
      const marker = new google.maps.Marker({ position: { lat: Number(p.lat), lng: Number(p.lng) }, map, title: p.title });
      marker.addListener("click", () => { location.href = p.url; });
    });
  };

  window.initDetailMap = function () {
    const el = qs("#detailMap");
    if (!el || !window.google) return;
    const pos = { lat: Number(el.dataset.lat), lng: Number(el.dataset.lng) };
    const map = new google.maps.Map(el, { center: pos, zoom: 14, disableDefaultUI: true, zoomControl: true });
    new google.maps.Marker({ position: pos, map, title: el.dataset.title });
  };

  document.addEventListener("DOMContentLoaded", () => {
    navbar();
    gsapMotion();
    card3dMotion();
    charts();
    swiper();
    tiltCards();
    ambientScene();
    cityHero();
  });
})();
