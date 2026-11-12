// ALGORA real-time 3D (three.js r165). 1 unit = 100 mm; dimensions follow output/cnc/dims.json.
import * as THREE from "three";
import { RoomEnvironment } from "three/addons/environments/RoomEnvironment.js";
import { EffectComposer } from "three/addons/postprocessing/EffectComposer.js";
import { RenderPass } from "three/addons/postprocessing/RenderPass.js";
import { UnrealBloomPass } from "three/addons/postprocessing/UnrealBloomPass.js";
import { OutputPass } from "three/addons/postprocessing/OutputPass.js";

const ALG = window.ALG;
const FLAT = 3.0, FLAT_IN = 2.78, R = FLAT / Math.sqrt(3), R_IN = FLAT_IN / Math.sqrt(3), WATER_Y = 1.05;
const T = 0.05, TR = 0.10;                                   // 5 mm sheets, 10 mm rings
const LAYERS = { A: [0.15, 0.20], C1: [0.05, 0.15], C2: [-0.05, 0.05], C3: [-0.15, -0.05], B: [-0.20, -0.15] };
const HOLES = [[0, 1.25, 0.076], [-0.4, 1.25, 0.0625], [0.4, 1.25, 0.0625], [0, -1.25, 0.0625]];
const mobile = matchMedia("(max-width: 980px)").matches;

/* ---------------- materials (shared) ---------------- */
const M = {
  front: new THREE.MeshPhysicalMaterial({ color: 0xcfe9ff, roughness: 0.05, clearcoat: 1, transparent: true, opacity: 0.12, envMapIntensity: 0.6, depthWrite: false }),
  ring: new THREE.MeshPhysicalMaterial({ color: 0x2f8fd8, roughness: 0.15, clearcoat: 1, transparent: true, opacity: 0.55, emissive: 0x0b3f7a, emissiveIntensity: 0.35, envMapIntensity: 0.5 }),
  back: new THREE.MeshPhysicalMaterial({ color: 0x5a5f9a, roughness: 0.6, transparent: true, opacity: 0.6, envMapIntensity: 0.3 }),
  water: new THREE.MeshStandardMaterial({ color: 0x0f8f55, emissive: 0x12b86c, emissiveIntensity: 0.32, roughness: 0.35, transparent: true, opacity: 0.88 }),
  air: new THREE.MeshStandardMaterial({ color: 0x9fdcff, emissive: 0x0f3d63, emissiveIntensity: 0.3, transparent: true, opacity: 0.18, side: THREE.DoubleSide, depthWrite: false }),
  led: new THREE.MeshBasicMaterial({ color: 0xffd6f4 }),
  pcb: new THREE.MeshStandardMaterial({ color: 0xe9edf5, roughness: 0.6 }),
  gland: new THREE.MeshStandardMaterial({ color: 0x1d2433, roughness: 0.45, metalness: 0.2 }),
  edge: new THREE.LineBasicMaterial({ color: 0x9fe3ff, transparent: true, opacity: 0.55 }),
  bubble: new THREE.PointsMaterial({ color: 0xe8fff4, size: 0.05, transparent: true, opacity: 0.85, depthWrite: false }),
};

/* ---------------- geometry helpers ---------------- */
const hexPts = (r, n = 6) => Array.from({ length: n }, (_, i) => new THREE.Vector2(r * Math.cos(i * Math.PI / 3), r * Math.sin(i * Math.PI / 3)));
const shapeFrom = pts => new THREE.Shape(pts);
function clipBelow(pts, ymax) {
  const out = [];
  for (let i = 0; i < pts.length; i++) {
    const P = pts[(i + pts.length - 1) % pts.length], Q = pts[i], pin = P.y <= ymax, qin = Q.y <= ymax;
    const cut = () => new THREE.Vector2(P.x + (Q.x - P.x) * (ymax - P.y) / (Q.y - P.y), ymax);
    if (qin) { if (!pin) out.push(cut()); out.push(Q); } else if (pin) out.push(cut());
  }
  return out;
}
const clipAbove = (pts, ymin) => clipBelow(pts.map(p => new THREE.Vector2(p.x, -p.y)), -ymin).map(p => new THREE.Vector2(p.x, -p.y));
function prism(shape, z0, z1, mat, edges = true) {
  const g = new THREE.ExtrudeGeometry(shape, { depth: z1 - z0, bevelEnabled: false, curveSegments: 24 });
  g.translate(0, 0, z0);
  const m = new THREE.Mesh(g, mat);
  if (edges) m.add(new THREE.LineSegments(new THREE.EdgesGeometry(g, 30), M.edge));
  return m;
}

/* ---------------- one module ---------------- */
function makeModule({ bubbles = true } = {}) {
  const root = new THREE.Group(), parts = {};
  const outer = hexPts(R), inner = hexPts(R_IN);
  const sheet = shapeFrom(outer);
  const back = shapeFrom(outer); HOLES.forEach(([x, y, r]) => { const h = new THREE.Path(); h.absarc(x, y, r, 0, Math.PI * 2, true); back.holes.push(h); });
  const ring = shapeFrom(outer); ring.holes.push(new THREE.Path(inner.slice().reverse()));
  const add = (k, obj) => { const g = new THREE.Group(); g.add(obj); g.userData.base = 0; root.add(g); parts[k] = g; return g; };
  add("A", prism(sheet, ...LAYERS.A, M.front));
  for (const k of ["C1", "C2", "C3"]) add(k, prism(ring, ...LAYERS[k], M.ring));
  add("B", prism(back, ...LAYERS.B, M.back));
  // culture + air gap (stay in the middle when exploded)
  const W = new THREE.Group();
  W.add(prism(shapeFrom(clipBelow(inner, WATER_Y)), -0.148, 0.148, M.water, false));
  W.add(prism(shapeFrom(clipAbove(inner, WATER_Y)), -0.148, 0.148, M.air, false));
  root.add(W); parts.W = W;
  // LED strip on the outside of ring C2
  const led = new THREE.Group(), n = 31, perim = outer.map((p, i) => [p, outer[(i + 1) % 6]]);
  const pcbShape = shapeFrom(hexPts(R + 0.018)); pcbShape.holes.push(new THREE.Path(hexPts(R + 0.002).reverse()));
  led.add(prism(pcbShape, -0.045, 0.045, M.pcb, false));
  const dots = new THREE.InstancedMesh(new THREE.BoxGeometry(0.05, 0.05, 0.05), M.led, n); const tmp = new THREE.Object3D();
  for (let i = 0; i < n; i++) {
    const s = (i + 0.5) / n * 6, k = Math.floor(s), f = s - k, [a, b] = perim[k];
    const p = a.clone().lerp(b, f), nrm = p.clone().normalize();
    tmp.position.set(p.x + nrm.x * 0.03, p.y + nrm.y * 0.03, 0); tmp.lookAt(0, 0, 0); tmp.updateMatrix(); dots.setMatrixAt(i, tmp.matrix);
  }
  led.add(dots); parts.C2.add(led); parts.L = led;
  // cable glands on the back
  const G = new THREE.Group();
  HOLES.forEach(([x, y, r]) => {
    const nut = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.6, r * 1.6, 0.05, 6), M.gland); nut.rotation.x = Math.PI / 2; nut.position.set(x, y, -0.225);
    const cap = new THREE.Mesh(new THREE.CylinderGeometry(r * 1.15, r * 1.25, 0.14, 24), M.gland); cap.rotation.x = Math.PI / 2; cap.position.set(x, y, -0.32);
    G.add(nut, cap);
  });
  parts.B.add(G); parts.G = G;
  // bubbles
  if (bubbles) {
    const N = 40, pos = new Float32Array(N * 3), seed = [];
    for (let i = 0; i < N; i++) seed.push([Math.random(), Math.random() * 2 - 1, (Math.random() - 0.5) * 0.24]);
    const geo = new THREE.BufferGeometry(); geo.setAttribute("position", new THREE.BufferAttribute(pos, 3));
    const pts = new THREE.Points(geo, M.bubble); W.add(pts);
    root.userData.bubbles = { geo, seed, N };
  }
  root.userData.parts = parts;
  return root;
}
function animateBubbles(mod, t) {
  const b = mod.userData.bubbles; if (!b) return;
  const a = b.geo.attributes.position.array, y0 = -1.25, y1 = WATER_Y - 0.03;
  for (let i = 0; i < b.N; i++) {
    const [ph, sx, z] = b.seed[i], u = (t * 0.16 + ph) % 1, y = y0 + (y1 - y0) * u;
    const half = Math.max(0.1, R_IN - Math.abs(y) / Math.sqrt(3) - 0.08);
    a[i * 3] = Math.max(-half, Math.min(half, sx * 0.35 * u * 1.6 + Math.sin(t * 2 + ph * 9) * 0.04)); a[i * 3 + 1] = y; a[i * 3 + 2] = z;
  }
  b.geo.attributes.position.needsUpdate = true;
}

/* ---------------- theme ---------------- */
const STAGES = [], THEME_HOOKS = [];
function applyTheme(th) {
  const light = th === "light";
  STAGES.forEach(st => { st.scene.background = light ? null : new THREE.Color(0x050B16); st.bp.strength = st.bloom; st.bp.enabled = !light; });
  M.edge.color.set(light ? 0x2c6fb4 : 0x9fe3ff); M.edge.opacity = light ? 0.7 : 0.55;
  M.water.emissiveIntensity = light ? 0.05 : 0.32; M.water.color.set(light ? 0x0d9a52 : 0x0f8f55); M.water.opacity = light ? 0.96 : 0.88;
  M.front.opacity = light ? 0.06 : 0.12; M.back.color.set(light ? 0x8f94cf : 0x5a5f9a);
  M.ring.color.set(light ? 0x1f6fd0 : 0x2f8fd8); M.ring.opacity = light ? 0.75 : 0.55; M.ring.emissiveIntensity = light ? 0.05 : 0.35;
  STAGES.forEach(st => { st.scene.environmentIntensity = light ? 0.55 : 0.35; });
  THEME_HOOKS.forEach(f => f(light));
}
addEventListener("alg:theme", e => applyTheme(e.detail));

/* ---------------- renderer factory ---------------- */
function stage(canvas, { bloom = 0.9, fov = 35 } = {}) {
  const renderer = new THREE.WebGLRenderer({ canvas, antialias: true, alpha: true, powerPreference: "high-performance" });
  renderer.setPixelRatio(Math.min(devicePixelRatio, mobile ? 1.5 : 1.75));
  renderer.toneMapping = THREE.ACESFilmicToneMapping; renderer.toneMappingExposure = 0.9;
  const scene = new THREE.Scene();
  scene.environment = new THREE.PMREMGenerator(renderer).fromScene(new RoomEnvironment(), 0.04).texture; scene.environmentIntensity = 0.35;
  const camera = new THREE.PerspectiveCamera(fov, 1, 0.1, 200);
  const key = new THREE.DirectionalLight(0xffffff, 0.9); key.position.set(4, 6, 8); scene.add(key, new THREE.AmbientLight(0x6688ff, 0.35));
  const composer = new EffectComposer(renderer);
  composer.addPass(new RenderPass(scene, camera));
  const bp = new UnrealBloomPass(new THREE.Vector2(1, 1), bloom, 0.5, 0.62); composer.addPass(bp); composer.addPass(new OutputPass());
  STAGES.push({ scene, bp, bloom });
  const resize = () => {
    const w = canvas.clientWidth, h = canvas.clientHeight; if (!w || !h) return;
    renderer.setSize(w, h, false); composer.setSize(w, h); camera.aspect = w / h; camera.updateProjectionMatrix();
  };
  new ResizeObserver(resize).observe(canvas); resize();
  let visible = true; new IntersectionObserver(([e]) => visible = e.isIntersecting, { rootMargin: "100px" }).observe(canvas);
  return { renderer, scene, camera, composer, get visible() { return visible; } };
}
function honeycomb(n, gap = 0.08) {
  const Rp = (FLAT + gap) / Math.sqrt(3), out = [[0, 0]], dirs = [[0, 1], [-1, 0.5], [-1, -0.5], [0, -1], [1, -0.5], [1, 0.5]];
  for (let ring = 1; out.length < n; ring++) {
    let cur = [1.5 * Rp * ring, (FLAT + gap) * 0.5 * ring];
    for (let s = 0; s < 6 && out.length < n; s++) for (let k = 0; k < ring && out.length < n; k++) {
      out.push([cur[0], cur[1]]);
      const d = dirs[(s + 1) % 6]; cur = [cur[0] + d[0] * 1.5 * Rp, cur[1] + d[1] * (FLAT + gap)];
    }
  }
  return out.slice(0, n);
}

/* ---------------- HERO ---------------- */
function hero() {
  const S = stage(document.getElementById("hero3d"), { bloom: 1.05 });
  const wall = new THREE.Group(); S.scene.add(wall);
  const mods = honeycomb(7).map(([x, y]) => { const m = makeModule(); m.position.set(x, y, 0); wall.add(m); return m; });
  wall.scale.setScalar(mobile ? 0.42 : 0.66); wall.position.set(mobile ? 0.6 : 4.3, mobile ? 3.4 : 0, 0); wall.rotation.set(0.08, -0.5, 0);
  S.camera.position.set(0, 0, 16);
  // stars
  const sg = new THREE.BufferGeometry(), sp = new Float32Array(2400 * 3);
  for (let i = 0; i < sp.length; i++) sp[i] = (Math.random() - 0.5) * (i % 3 === 2 ? 40 : 60) - (i % 3 === 2 ? 15 : 0);
  sg.setAttribute("position", new THREE.BufferAttribute(sp, 3));
  const stars = new THREE.Points(sg, new THREE.PointsMaterial({ color: 0x9fb8ff, size: 0.04, transparent: true, opacity: 0.7 })); S.scene.add(stars);
  THEME_HOOKS.push(light => { stars.visible = !light; });
  // CO2 particles drifting into the modules
  const N = mobile ? 260 : 520, cg = new THREE.BufferGeometry(), cp = new Float32Array(N * 3), cs = [];
  const spawn = i => { const a = Math.random() * Math.PI * 2, r = 6 + Math.random() * 6; cs[i] = { p: new THREE.Vector3(Math.cos(a) * r, (Math.random() - 0.5) * 9, Math.sin(a) * r * 0.6), tgt: mods[(Math.random() * 7) | 0], v: 0.6 + Math.random() * 0.9 }; };
  for (let i = 0; i < N; i++) spawn(i);
  cg.setAttribute("position", new THREE.BufferAttribute(cp, 3));
  const co2 = new THREE.Points(cg, new THREE.PointsMaterial({ color: 0xffb547, size: 0.06, transparent: true, opacity: 0.9, depthWrite: false }));
  wall.add(co2);
  THEME_HOOKS.push(light => co2.material.color.set(light ? 0xe08a00 : 0xffb547));
  let mx = 0, my = 0; addEventListener("pointermove", e => { mx = e.clientX / innerWidth - 0.5; my = e.clientY / innerHeight - 0.5; });
  const clock = new THREE.Clock(), tgt = new THREE.Vector3();
  return () => {
    if (!S.visible) return;
    const t = clock.getElapsedTime(), dt = Math.min(0.05, clock.getDelta() || 0.016);
    wall.rotation.y += ((-0.5 + mx * 0.35 + Math.sin(t * 0.25) * 0.08) - wall.rotation.y) * 0.04;
    wall.rotation.x += ((0.08 + my * 0.2) - wall.rotation.x) * 0.04;
    mods.forEach((m, i) => { animateBubbles(m, t + i * 0.37); m.position.z = Math.sin(t * 0.8 + i) * 0.06; });
    const a = cg.attributes.position.array;
    for (let i = 0; i < N; i++) {
      const c = cs[i]; tgt.copy(c.tgt.position); const d = tgt.sub(c.p); const L = d.length();
      if (L < 0.6) { spawn(i); continue; }
      c.p.addScaledVector(d.normalize(), c.v * 0.016 * (1 + 2 / L));
      a[i * 3] = c.p.x; a[i * 3 + 1] = c.p.y; a[i * 3 + 2] = c.p.z;
    }
    cg.attributes.position.needsUpdate = true;
    S.composer.render();
    if (!ALG.ready) ALG.ready = true;
  };
}

/* ---------------- EXPLODED ---------------- */
function exploded() {
  const S = stage(document.getElementById("ex3d"), { bloom: 0.7 });
  const mod = makeModule(), P = mod.userData.parts; S.scene.add(mod);
  const OFF = { A: 1.4, C1: 0.7, C2: 0, C3: -0.7, B: -1.4 };
  mod.position.set(mobile ? -0.6 : 0.7, mobile ? 1.4 : 0, 0);
  S.camera.position.set(0, 0, mobile ? 14 : 11.5);
  const labels = document.getElementById("labels");
  const L = [
    ["A", ["A · LEMBAR DEPAN · BENING 5 MM", "A · FRONT SHEET · CLEAR 5 MM"], P.A, new THREE.Vector3(R * 0.5, FLAT / 2, 0.2)],
    ["C", ["C1–C3 · CINCIN 10 MM · DINDING 11 MM", "C1–C3 · 10 MM RINGS · 11 MM WALL"], P.C1, new THREE.Vector3(R, 0, 0.1)],
    ["W", ["KULTUR CHLORELLA · ±1,7 L · 30 MM", "CHLORELLA CULTURE · ~1.7 L · 30 MM"], P.W, new THREE.Vector3(-0.6, -0.4, 0.15)],
    ["L", ["STRIP LED · 31 × WS2812B", "LED STRIP · 31 × WS2812B"], P.C2, new THREE.Vector3(-R * 0.5, FLAT / 2 + 0.03, 0)],
    ["B", ["B · LEMBAR BELAKANG · BURAM 5 MM", "B · BACK SHEET · FROSTED 5 MM"], P.B, new THREE.Vector3(-R, 0, -0.2)],
    ["G", ["P1–P4 · CABLE GLAND PG9 / PG7", "P1–P4 · PG9 / PG7 CABLE GLANDS"], P.B, new THREE.Vector3(0.4, 1.25, -0.39)],
  ].map(([k, txt, obj, local]) => { const el = document.createElement("div"); el.className = "lbl"; labels.appendChild(el); return { k, el, obj, local, txt }; });
  const setLbl = () => L.forEach(l => l.el.textContent = l.txt[ALG.lang === "en" ? 1 : 0]); setLbl(); addEventListener("alg:lang", setLbl);
  const svg = document.createElementNS("http://www.w3.org/2000/svg", "svg"); svg.setAttribute("class", "lines"); labels.prepend(svg);
  const clock = new THREE.Clock(), v = new THREE.Vector3();
  return () => {
    if (!S.visible) return;
    const t = clock.getElapsedTime(), e = ALG.explode || 0, ease = e * e * (3 - 2 * e);
    for (const k in OFF) P[k].position.z = OFF[k] * ease;
    mod.rotation.y = -0.55 - ease * 0.55 + Math.sin(t * 0.3) * 0.05; mod.rotation.x = 0.18 + ease * 0.12;
    animateBubbles(mod, t);
    S.composer.render();
    const w = S.renderer.domElement.clientWidth, h = S.renderer.domElement.clientHeight;
    const show = ease > 0.35, lx = mobile ? w * 0.56 : w * 0.76;
    L.forEach(l => { v.copy(l.local); l.obj.localToWorld(v); v.project(S.camera); l.ax = (v.x + 1) / 2 * w; l.ay = (1 - v.y) / 2 * h; });
    const sorted = [...L].sort((p, q) => p.ay - q.ay), gap = mobile ? 26 : 38, top0 = h / 2 - gap * (L.length - 1) / 2;
    sorted.forEach((l, i) => { l.ly = top0 + i * gap; });
    svg.setAttribute("viewBox", `0 0 ${w} ${h}`);
    svg.innerHTML = show ? L.map(l => `<path d="M${l.ax} ${l.ay} L${lx - 30} ${l.ly} L${lx - 6} ${l.ly}" stroke="${ALG.focus === l.k ? "#2EE6A6" : (ALG.theme === "light" ? "rgba(30,50,90,.4)" : "rgba(180,205,255,.45)")}" fill="none" stroke-width="1"/><circle cx="${l.ax}" cy="${l.ay}" r="3.5" fill="${ALG.focus === l.k ? "#2EE6A6" : (ALG.theme === "light" ? "#2c6fb4" : "#9FE3FF")}"/>`).join("") : "";
    L.forEach(l => {
      l.el.style.left = lx + "px"; l.el.style.top = l.ly + "px";
      l.el.classList.toggle("on", show); l.el.style.color = ALG.focus === l.k ? "#2EE6A6" : "";
    });
  };
}

/* ---------------- HIVE BUILDER ---------------- */
function hive() {
  const S = stage(document.getElementById("hive3d"), { bloom: 0.95 });
  const grp = new THREE.Group(); S.scene.add(grp);
  const slots = honeycomb(19), mods = slots.map(([x, y]) => { const m = makeModule(); m.position.set(x, y, 0); m.scale.setScalar(0.001); grp.add(m); return m; });
  S.camera.position.set(0, 0, 26);
  const ROT = { wall: [0.1, -0.35], lamp: [1.15, 0], floor: [-1.15, 0] };
  const clock = new THREE.Clock();
  return () => {
    if (!S.visible) return;
    const t = clock.getElapsedTime(), n = ALG.count || 7, [rx, ry] = ROT[ALG.mode] || ROT.wall;
    grp.rotation.x += (rx - grp.rotation.x) * 0.05; grp.rotation.y += (ry + Math.sin(t * 0.3) * 0.1 - grp.rotation.y) * 0.05;
    const fit = n <= 1 ? 1.6 : n <= 7 ? 1.05 : 0.68; grp.scale.setScalar(grp.scale.x + (fit - grp.scale.x) * 0.06);
    mods.forEach((m, i) => { const s = i < n ? 1 : 0.001; m.scale.setScalar(m.scale.x + (s - m.scale.x) * 0.12); m.visible = m.scale.x > 0.01; if (m.visible) animateBubbles(m, t + i * 0.5); });
    S.composer.render();
  };
}

/* ---------------- run ---------------- */
try {
  const loops = [hero(), exploded(), hive()]; applyTheme(ALG.theme || "dark");
  const loop = () => { loops.forEach(f => f()); requestAnimationFrame(loop); };
  loop();
} catch (err) {
  console.error("WebGL unavailable, using still images", err); ALG.ready = true;
  document.getElementById("hero3d").outerHTML = '<img src="media/hero.webp" alt="" style="position:absolute;right:0;top:0;height:100%;object-fit:cover;opacity:.8">';
}
