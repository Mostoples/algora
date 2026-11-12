// ALGORA landing page — UI, scroll story and simulations (3D lives in scene.js; shared state on window.ALG)
window.ALG = Object.assign(window.ALG || {}, { explode: 0, count: 7, mode: "wall" });
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const fmt = (v, d = 1) => v.toLocaleString(window.ALG.lang === "en" ? "en-US" : "id-ID", { minimumFractionDigits: d, maximumFractionDigits: d });

/* ---------- preloader ---------- */
let pct = 0; const pctEl = $("#loadpct");
const tick = setInterval(() => { pct = Math.min(pct + 3 + Math.random() * 6, window.ALG.ready ? 100 : 92); pctEl.textContent = Math.round(pct) + "%"; if (pct >= 100) finish(); }, 60);
setTimeout(() => { window.ALG.ready = true; }, 4500);               // never block on a slow CDN
function finish() { clearInterval(tick); $("#loader").classList.add("done"); intro(); }

/* ---------- smooth scroll ---------- */
gsap.registerPlugin(ScrollTrigger);
const lenis = new Lenis({ lerp: 0.09 });
lenis.on("scroll", ScrollTrigger.update);
gsap.ticker.add(t => lenis.raf(t * 1000)); gsap.ticker.lagSmoothing(0);
$$('a[href^="#"]').forEach(a => a.addEventListener("click", e => { const t = $(a.getAttribute("href")); if (t) { e.preventDefault(); lenis.scrollTo(t, { offset: -10 }); } }));

function intro() {
  gsap.from(".hero-copy h1 .w", { yPercent: 110, opacity: 0, duration: 1.2, stagger: 0.12, ease: "expo.out" });
  gsap.from([".hero-copy .tag", ".hero-copy p", ".hero-copy .row", ".ticker", ".hero-specs"], { y: 24, opacity: 0, duration: 1, stagger: 0.08, delay: 0.35, ease: "expo.out" });
}

/* ---------- reveals, kinetic type, counters ---------- */
$$(".sec h2:not(.kinetic), .sec .tag, .sec > p, .card, .facts > div, .tile, .grid, .vids figure, .panel, .cyc, .phones, .cta-end > *").forEach(el => {
  el.classList.add("up");
  gsap.to(el, { opacity: 1, y: 0, duration: 1.1, ease: "expo.out", scrollTrigger: { trigger: el, start: "top 88%" } });
});
$$(".kinetic span").forEach(s => ScrollTrigger.create({ trigger: s, start: "top 70%", end: "bottom 30%", toggleClass: "lit" }));
$$("[data-to]").forEach(el => {
  const to = +el.dataset.to, dec = +(el.dataset.dec || 0);
  ScrollTrigger.create({ trigger: el, start: "top 85%", once: true, onEnter: () => {
    const o = { v: 0 }; gsap.to(o, { v: to, duration: 1.6, ease: "power3.out", onUpdate: () => el.textContent = fmt(o.v, dec) });
  } });
});

/* ---------- hero CO2 ticker (simulated) ---------- */
const spark = [], ppmEl = $("#ppm"), poly = $("#spark polyline");
let ppm = 812;
setInterval(() => {
  ppm += (Math.random() - 0.55) * 6; ppm = Math.max(640, Math.min(900, ppm));
  spark.push(ppm); if (spark.length > 40) spark.shift();
  ppmEl.textContent = Math.round(ppm);
  poly.setAttribute("points", spark.map((v, i) => `${i * 3},${30 - (v - 620) / 300 * 28}`).join(" "));
}, 500);

/* ---------- exploded section (scroll-scrubbed) ---------- */
const order = ["A", "C", "W", "L", "B", "G"];
ScrollTrigger.create({ trigger: ".explode", start: "top top", end: "bottom bottom", scrub: true, onUpdate: s => {
  const p = s.progress; window.ALG.explode = Math.min(1, Math.max(0, (p - 0.08) / 0.5));
  const k = Math.min(order.length - 1, Math.floor(Math.max(0, p - 0.1) / 0.8 * order.length));
  $$("#partlist li").forEach(li => li.classList.toggle("on", window.ALG.explode > 0.15 && li.dataset.k === order[k]));
  window.ALG.focus = window.ALG.explode > 0.15 ? order[k] : null;
  exState();
} });
function exState() {
  const e = window.ALG.explode;
  $("#exstate").textContent = e < 0.05 ? t("TERAKIT · 300 × 40 MM", "ASSEMBLED · 300 × 40 MM") : e > 0.95 ? t("TERURAI · 5 LAPIS + ISI", "EXPLODED · 5 LAYERS + CORE") : t("MEMBONGKAR · ", "EXPLODING · ") + Math.round(e * 100) + "%";
}
exState();

/* ---------- builder ---------- */
const PER = { L: 1.7, led: 31, co2: 0.27, w: 5.2 };
function setCount(n) {
  n = Math.max(1, Math.min(19, n)); window.ALG.count = n;
  $("#nmod").textContent = n; $("#nbar").style.width = (n / 19 * 100) + "%";
  $("#rL").textContent = fmt(n * PER.L) + " L"; $("#rLED").textContent = n * PER.led;
  $("#rCO2").textContent = fmt(n * PER.co2) + " g"; $("#rW").textContent = fmt(n * PER.w, 0) + " W";
}
$("#minus").onclick = () => setCount(window.ALG.count - 1); $("#plus").onclick = () => setCount(window.ALG.count + 1);
$$("#modes button").forEach(b => b.onclick = () => { $$("#modes button").forEach(x => x.classList.toggle("on", x === b)); window.ALG.mode = b.dataset.m; });
setCount(7);

/* ---------- 24-hour cycle (same rules as the firmware simulation) ---------- */
const dial = $("#dial"); const NS = "http://www.w3.org/2000/svg";
const arc = (h0, h1, r, col, w) => {
  const a = h => (h / 24) * Math.PI * 2 - Math.PI / 2, p = h => [100 + r * Math.cos(a(h)), 100 + r * Math.sin(a(h))];
  const [x0, y0] = p(h0), [x1, y1] = p(h1), large = h1 - h0 > 12 ? 1 : 0;
  const e = document.createElementNS(NS, "path"); e.setAttribute("d", `M${x0} ${y0} A${r} ${r} 0 ${large} 1 ${x1} ${y1}`);
  e.setAttribute("fill", "none"); e.setAttribute("stroke", col); e.setAttribute("stroke-width", w); e.setAttribute("stroke-linecap", "butt"); dial.appendChild(e);
};
arc(0, 23.99, 84, "rgba(255,255,255,.07)", 10); arc(6, 18, 84, "#C04DB8", 10); arc(18, 22, 84, "#F5B43D", 10);
for (let h = 0; h < 24; h += 0.5) arc(h, h + 1 / 6, 70, "rgba(61,123,255,.85)", 6);
const hand = document.createElementNS(NS, "line"); hand.setAttribute("x1", 100); hand.setAttribute("y1", 100); hand.setAttribute("stroke", "#EAF1FF"); hand.setAttribute("stroke-width", 2); dial.appendChild(hand);
const dot = document.createElementNS(NS, "circle"); dot.setAttribute("r", 5); dot.setAttribute("fill", "#2EE6A6"); dial.appendChild(dot);
const LEDW = { grow: 31 * 20 * (128 / 255) * (375 / 255) / 1000 * 5, room: 31 * 20 * (128 / 255) * (475 / 255) / 1000 * 5 };
function setTime(m) {
  const h = m / 60, mode = h >= 6 && h < 18 ? "grow" : h >= 18 && h < 22 ? "room" : "off", air = (m % 30) < 10;
  const p = (1.8 + (LEDW[mode] || 0)) / 0.85 + (air ? 3.6 : 0);
  $("#ctime").textContent = `${String(Math.floor(h)).padStart(2, "0")}:${String(m % 60).padStart(2, "0")}`;
  $("#cmode").textContent = { grow: t("MODE TUMBUH", "GROW MODE"), room: t("MODE RUANGAN", "ROOM LIGHT"), off: t("ISTIRAHAT", "RESTING") }[mode];
  $("#sLED").textContent = { grow: t("Merah + biru", "Red + blue"), room: t("Putih hangat", "Warm white"), off: t("Mati", "Off") }[mode];
  $("#sAir").textContent = air ? t("Nyala", "On") : t("Mati", "Off"); $("#sP").textContent = fmt(p) + " W";
  $("#sDose").textContent = Math.floor(h) === 8 && m % 60 === 0 ? t("Menetes · 3 detik", "Dosing · 3 s") : t("08.00 · 3 detik", "08:00 · 3 s");
  const a = h / 24 * Math.PI * 2 - Math.PI / 2;
  hand.setAttribute("x2", 100 + 56 * Math.cos(a)); hand.setAttribute("y2", 100 + 56 * Math.sin(a));
  dot.setAttribute("cx", 100 + 84 * Math.cos(a)); dot.setAttribute("cy", 100 + 84 * Math.sin(a));
  window.ALG.timeMode = mode;
}
const range = $("#hour"); range.oninput = () => setTime(+range.value); setTime(540);
ScrollTrigger.create({ trigger: ".cyc", start: "top 75%", once: true, onEnter: () => {
  const o = { v: 0 }; gsap.to(o, { v: 540, duration: 2.4, ease: "power2.inOut", onUpdate: () => { range.value = Math.round(o.v); setTime(Math.round(o.v)); } });
} });

/* ---------- gallery + lightbox ---------- */
const G = {
  draw: [["cad.webp", ["Gambar rancangan detail · LibreCAD", "Detailed design · LibreCAD"], 1], ["gt1.webp", ["Rakitan & daftar bagian · A3", "Assembly & parts list · A3"], 1],
         ["gt2.webp", ["Part A & C · cincin R4", "Parts A & C · R4 rings"], 1], ["gt3.webp", ["Part B · posisi lubang P1–P4", "Part B · hole positions P1–P4"], 1],
         ["gt4.webp", ["Potongan A-A & detail lapisan", "Section A-A & layer detail"], 1], ["gt5.webp", ["Tata letak potong CNC", "CNC cutting layout"], 1]],
  render: [["exploded.webp", ["Exploded · prototipe CNC", "Exploded · CNC prototype"]], ["proto.webp", ["Prototipe terakit · LED menyala", "Assembled prototype · LEDs on"]],
           ["r4.webp", ["Close-up · sudut dalam R4", "Close-up · R4 inner corner"]], ["holes.webp", ["Close-up · gland P1–P3", "Close-up · glands P1–P3"]],
           ["hero.webp", ["Klaster 7 modul · konsep", "7-module cluster · concept"]], ["wall.webp", ["Mode dinding · konsep", "Wall mode · concept"]],
           ["lamp.webp", ["Mode lampu · konsep", "Lamp mode · concept"]], ["floor.webp", ["Mode jalan setapak · konsep", "Pathway mode · concept"]],
           ["roof.webp", ["Mode atap · konsep", "Canopy mode · concept"]]],
};
let gTab = "draw";
function gallery(k) {
  gTab = k;
  $("#ggrid").innerHTML = G[k].map(([f, cc, light]) => [f, t(cc[0], cc[1]), light]).map(([f, c, light]) => `<figure class="${light ? "light" : ""}"><img src="media/${f}" alt="${c}" loading="lazy"><figcaption class="mono">${c}</figcaption></figure>`).join("");
  $$("#ggrid figure").forEach(fig => fig.onclick = () => { const lb = $("#lightbox"); lb.querySelector("img").src = fig.querySelector("img").src; lb.querySelector("span").textContent = fig.querySelector("figcaption").textContent; lb.classList.add("on"); });
  ScrollTrigger.refresh();
}
$$("#gtabs button").forEach(b => b.onclick = () => { $$("#gtabs button").forEach(x => x.classList.toggle("on", x === b)); gallery(b.dataset.g); });
$("#lightbox").onclick = () => $("#lightbox").classList.remove("on");
gallery("draw");

/* remove the old cache-first worker from when the app lived at "/" */
addEventListener("alg:lang", () => { $$("[data-to]").forEach(el => { if (el.textContent !== "0") el.textContent = fmt(+el.dataset.to, +(el.dataset.dec || 0)); }); setCount(window.ALG.count); setTime(+range.value); gallery(gTab); exState(); ScrollTrigger.refresh(); });

if ("serviceWorker" in navigator) navigator.serviceWorker.getRegistrations().then(rs => rs.forEach(r => { if (new URL(r.scope).pathname === "/") r.unregister(); }));
