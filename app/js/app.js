/* ALGORA app — native JS, no framework. Demo data runs when ?demo or file:// (or no backend). */
(() => {
const $ = (s, el = document) => el.querySelector(s);
const $$ = (s, el = document) => [...el.querySelectorAll(s)];

// ------------------------------------------------------------------ i18n --
const TEXT = {
  id: {
    tagline: "Fotobioreaktor mikroalga modular · AIoT",
    c_home: "01 · Beranda", h_home1: "Udara hidup,", h_home2: "cahaya hijau.",
    d_home: "Setiap modul hexagon berisi mikroalga yang menyerap CO₂, menghasilkan O₂, dan merawat dirinya sendiri.",
    co2_today: "CO₂ terserap hari ini", o2_today: "O₂ dihasilkan", modules: "modul aktif",
    mode_title: "Mode pemasangan", mode_hint: "satu modul, 4 fungsi",
    m_wall: "Dinding", m_floor: "Lantai", m_lamp: "Lampu", m_roof: "Genting",
    bio_title: "Skor Bio", bio_desc: "Kesehatan kultur gabungan dari pH, suhu, densitas & cahaya.", growing: "Tumbuh optimal",
    live: "Sensor langsung", see_all: "Lihat modul",
    s_ph: "pH kultur", s_temp: "Suhu", s_od: "Densitas (OD)", s_lux: "Cahaya", s_co2: "CO₂ masuk", s_do: "O₂ terlarut",
    st_ok: "Normal", st_hi: "Tinggi", st_low: "Rendah",
    c_hive: "02 · Modul", h_hive1: "Sambung,", h_hive2: "dan terus tumbuh.",
    d_hive: "Modul saling mengunci di 6 sisi: konektor magnet pogo untuk daya & data, plus quick-connect untuk aliran kultur.",
    lg_ok: "Sehat", lg_harvest: "Siap panen", lg_new: "Baru", add_mod: "Tambah", scan: "Pindai",
    snap_title: "Snap & play", snap1: "Tempel", snap1d: "Dekatkan sisi modul, magnet mengunci otomatis.",
    snap2: "Terdeteksi", snap2d: "Inti AIoT mengenali tetangga & membuka katup aliran.",
    snap3: "Sinkron", snap3d: "Kultur, cahaya & jadwal disamakan dengan seluruh jaringan.",
    c_light: "03 · Cahaya", h_light1: "Lampu yang", h_light2: "ikut bernapas.",
    d_light: "LED tepi menyinari kultur dari dalam: jadi lampu ruangan, sekaligus energi fotosintesis.",
    warm: "Hangat 2700K", cool: "Sejuk 6500K", bright: "Kecerahan", scenes: "Suasana",
    sc_focus: "Fokus", sc_relax: "Santai", sc_grow: "Tumbuh", sc_night: "Malam",
    photo: "Fotoperiode alga", photo_d: "16 jam terang · 8 jam gelap", circ: "Ritme sirkadian AI", circ_d: "Suhu warna mengikuti matahari",
    presence: "Sensor kehadiran", presence_d: "Redup otomatis saat ruangan kosong",
    c_care: "04 · Rawat mandiri", h_care1: "Merawat dirinya", h_care2: "sendiri.",
    d_care: "Dosis nutrien, sirkulasi udara, pembersihan dan panen berjalan otomatis lewat base station.",
    t_nut: "Nutrien", t_water: "Air", t_harv: "Panen", today: "Hari ini", harvest_now: "Panen sekarang",
    care: [
      ["06:00", "Aerasi pagi", "Gelembung mikro dari inti modul mengaduk kultur & memasok CO₂."],
      ["09:30", "Dosis nutrien", "AI menghitung kebutuhan N-P-K dari laju tumbuh; 4,2 ml disuntikkan."],
      ["13:00", "Self-cleaning", "Sirkulasi balik + UV-C mencegah biofilm menempel di akrilik."],
      ["17:45", "Panen parsial", "15% kultur dialirkan ke tangki panen, diganti medium segar."],
      ["22:00", "Mode gelap", "LED ke 0%, respirasi malam dipantau."],
    ],
    c_ai: "05 · AI Insight", h_ai1: "Tahu kapan", h_ai2: "harus panen.",
    d_ai: "Model AI memprediksi pertumbuhan, mendeteksi anomali, dan menyetel cahaya & nutrien tiap modul.",
    forecast: "Prediksi pertumbuhan", lg_od: "Densitas aktual", lg_pred: "Prediksi AI",
    days: " hari", next_harv: "Panen berikutnya", co2_year: "CO₂ / tahun (est.)", insights: "Rekomendasi",
    ins: [
      ["ic_leaf", "Modul C-04 siap panen", "OD 1,82 — panen 30% untuk menjaga laju tumbuh puncak."],
      ["ic_temp", "Modul genting B-02 hangat", "33 °C siang ini. AI menaikkan aliran sirkulasi 20%."],
      ["ic_bolt", "Hemat energi 18%", "Cahaya matahari cukup — LED dinding diturunkan otomatis."],
    ],
    n_home: "Beranda", n_hive: "Modul", n_light: "Cahaya", n_care: "Rawat",
    link: "Konektor sisi", flow: "Aliran kultur", close: "Tutup",
    toast_new: "Modul baru tersambung & tersinkron", toast_harv: "Panen dimulai — 180 ml biomassa",
    toast_mode: "Mode diubah ke ",
  },
  en: {
    tagline: "Modular microalgae photobioreactor · AIoT",
    c_home: "01 · Home", h_home1: "Living air,", h_home2: "green light.",
    d_home: "Every hexagon module holds microalgae that capture CO₂, release O₂ and look after themselves.",
    co2_today: "CO₂ captured today", o2_today: "O₂ produced", modules: "modules live",
    mode_title: "Install mode", mode_hint: "one module, 4 uses",
    m_wall: "Wall", m_floor: "Floor", m_lamp: "Lamp", m_roof: "Roof tile",
    bio_title: "Bio Score", bio_desc: "Combined culture health from pH, temperature, density & light.", growing: "Growing well",
    live: "Live sensors", see_all: "See modules",
    s_ph: "Culture pH", s_temp: "Temperature", s_od: "Density (OD)", s_lux: "Light", s_co2: "CO₂ in", s_do: "Dissolved O₂",
    st_ok: "Normal", st_hi: "High", st_low: "Low",
    c_hive: "02 · Modules", h_hive1: "Snap together,", h_hive2: "keep growing.",
    d_hive: "Modules lock on all 6 sides: magnetic pogo connectors for power & data, plus quick-connects for culture flow.",
    lg_ok: "Healthy", lg_harvest: "Ready to harvest", lg_new: "New", add_mod: "Add", scan: "Scan",
    snap_title: "Snap & play", snap1: "Snap", snap1d: "Bring sides together — magnets lock automatically.",
    snap2: "Detected", snap2d: "The AIoT core recognises neighbours & opens the flow valves.",
    snap3: "Synced", snap3d: "Culture, light & schedules match the whole network.",
    c_light: "03 · Light", h_light1: "A lamp that", h_light2: "breathes.",
    d_light: "Edge LEDs light the culture from within: room light and photosynthesis energy in one.",
    warm: "Warm 2700K", cool: "Cool 6500K", bright: "Brightness", scenes: "Scenes",
    sc_focus: "Focus", sc_relax: "Relax", sc_grow: "Grow", sc_night: "Night",
    photo: "Algae photoperiod", photo_d: "16 h light · 8 h dark", circ: "AI circadian rhythm", circ_d: "Colour temperature follows the sun",
    presence: "Presence sensor", presence_d: "Dims automatically when the room is empty",
    c_care: "04 · Self-care", h_care1: "Looks after", h_care2: "itself.",
    d_care: "Nutrient dosing, aeration, cleaning and harvesting run automatically via the base station.",
    t_nut: "Nutrient", t_water: "Water", t_harv: "Harvest", today: "Today", harvest_now: "Harvest now",
    care: [
      ["06:00", "Morning aeration", "Micro-bubbles from the module core mix the culture & feed CO₂."],
      ["09:30", "Nutrient dose", "AI computes N-P-K need from growth rate; 4.2 ml injected."],
      ["13:00", "Self-cleaning", "Reverse flow + UV-C stop biofilm sticking to the acrylic."],
      ["17:45", "Partial harvest", "15% of culture flows to the harvest tank, refilled with fresh medium."],
      ["22:00", "Dark mode", "LEDs to 0%, night respiration monitored."],
    ],
    c_ai: "05 · AI Insight", h_ai1: "Knows when", h_ai2: "to harvest.",
    d_ai: "The AI model forecasts growth, spots anomalies and tunes light & nutrients per module.",
    forecast: "Growth forecast", lg_od: "Measured density", lg_pred: "AI forecast",
    days: " days", next_harv: "Next harvest", co2_year: "CO₂ / year (est.)", insights: "Recommendations",
    ins: [
      ["ic_leaf", "Module C-04 ready to harvest", "OD 1.82 — harvest 30% to keep peak growth rate."],
      ["ic_temp", "Roof module B-02 running warm", "33 °C this afternoon. AI raised circulation flow by 20%."],
      ["ic_bolt", "18% energy saved", "Enough daylight — wall LEDs dimmed automatically."],
    ],
    n_home: "Home", n_hive: "Modules", n_light: "Light", n_care: "Care",
    link: "Side connectors", flow: "Culture flow", close: "Close",
    toast_new: "New module connected & synced", toast_harv: "Harvest started — 180 ml biomass",
    toast_mode: "Mode switched to ",
  },
};
const qs = new URLSearchParams(location.search);
let lang = qs.get("lang") || localStorageGet("alg_lang") || (navigator.language || "id").slice(0, 2);
if (!TEXT[lang]) lang = "id";
const T = k => TEXT[lang][k] ?? k;
function localStorageGet(k) { try { return localStorage.getItem(k); } catch (e) { return null; } }
function localStorageSet(k, v) { try { localStorage.setItem(k, v); } catch (e) {} }

function applyText() {
  document.documentElement.lang = lang;
  $$("[data-t]").forEach(el => { el.textContent = T(el.dataset.t); });
  $("#langBtn").textContent = lang === "id" ? "EN" : "ID";
  renderSensors(); renderCare(); renderInsights(); renderGauge();
}

// ----------------------------------------------------------------- state ---
const DEMO = qs.has("demo") || location.protocol === "file:" || !qs.has("live");
const S = {
  mode: "wall", co2: 412, o2: 300, score: 92, cct: 4000, bri: 72,
  ph: 7.4, temp: 27.6, od: 1.42, lux: 5400, co2in: 640, dox: 8.6,
  nut: 78, wat: 64, harv: 41,
  cells: [],
};
const LAYOUTS = {  // axial (q,r) per install mode
  wall: [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,-1],[-1,1],[2,-1],[-2,1],[1,1],[-1,-1],[2,0],[-2,0]],
  floor: [[-2,0],[-1,0],[0,0],[1,0],[2,0],[-2,1],[-1,1],[0,1],[1,1],[-1,-1],[0,-1],[1,-1],[2,-1],[-3,1],[3,-1]],
  lamp: [[0,0],[1,0],[-1,0],[0,1],[0,-1],[1,-1],[-1,1]],
  roof: [[-2,0],[-1,0],[0,0],[1,0],[2,0],[-2,1],[-1,1],[0,1],[1,1],[2,1],[-1,-1],[0,-1],[1,-1],[2,-1],[3,-1]],
};
function seedCells() {
  S.cells = LAYOUTS[S.mode].map(([q, r], i) => ({ q, r, id: String.fromCharCode(65 + (i % 5)) + "-" + String(i + 1).padStart(2, "0"),
    od: 0.9 + Math.random() * 0.9, state: i === 4 ? "harvest" : "ok" }));
}

// -------------------------------------------------------------- sensors ---
const SENS = [
  ["s_ph", "ph", "", "ic_ph", 6.5, 8.5, v => v.toFixed(2)],
  ["s_temp", "temp", "°C", "ic_temp", 20, 35, v => v.toFixed(1)],
  ["s_od", "od", "", "ic_leaf", 0, 2.2, v => v.toFixed(2)],
  ["s_lux", "lux", "lx", "ic_bolt", 0, 9000, v => Math.round(v).toLocaleString(lang)],
  ["s_co2", "co2in", "ppm", "ic_co2", 400, 1200, v => Math.round(v)],
  ["s_do", "dox", "mg/L", "ic_drop", 0, 14, v => v.toFixed(1)],
];
function renderSensors(target = "#sensors", src = S) {
  const el = $(target); if (!el) return;
  el.innerHTML = SENS.map(([k, key, u, ic, lo, hi, f]) => {
    const v = src[key], pct = Math.max(4, Math.min(100, (v - lo) / (hi - lo) * 100));
    return `<div class="card sm sensor"><div class="between"><div class="ic"><img src="assets/img/${ic}.png" alt=""></div>
      <span class="pill ok"><b></b>${T("st_ok")}</span></div>
      <div class="v" data-k="${key}">${f(v)}<small>${u}</small></div><p class="muted">${T(k)}</p>
      <div class="bar ${key === "od" ? "alg" : ""}"><i style="width:${pct}%"></i></div></div>`;
  }).join("");
}
function renderGauge() {
  const r = 54, c = 2 * Math.PI * r, p = S.score / 100;
  $("#gScore").innerHTML = `<svg width="132" height="132" viewBox="0 0 132 132">
    <defs><linearGradient id="gg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#43D17E"/><stop offset="1" stop-color="#2F7BFF"/></linearGradient></defs>
    <circle cx="66" cy="66" r="${r}" fill="none" stroke="#DCE4EF" stroke-width="12"/>
    <circle cx="66" cy="66" r="${r}" fill="none" stroke="url(#gg)" stroke-width="12" stroke-linecap="round"
      stroke-dasharray="${c * p} ${c}" style="filter:drop-shadow(0 4px 6px rgba(47,123,255,.35));transition:stroke-dasharray 1s"/></svg>
    <div class="c"><div><b>${Math.round(S.score)}</b><span>BIO</span></div></div>`;
}

// ------------------------------------------------------------------ hive ---
const HX = 30; // svg circumradius
function hexPts(cx, cy, r) {
  return Array.from({ length: 6 }, (_, i) => { const a = Math.PI / 3 * i; return `${(cx + r * Math.cos(a)).toFixed(1)},${(cy + r * Math.sin(a)).toFixed(1)}`; }).join(" ");
}
function axial(q, r) { return [1.5 * HX * q * 1.06, Math.sqrt(3) * HX * (r + q / 2) * 1.06]; }
function renderHive(newIdx = -1) {
  const svg = $("#hive");
  const defs = `<defs>
    <radialGradient id="hg" cx=".45" cy=".4" r=".75"><stop offset="0" stop-color="#9BF0B8"/><stop offset=".55" stop-color="#2FB86A"/><stop offset="1" stop-color="#0E6B3A"/></radialGradient>
    <radialGradient id="hh" cx=".45" cy=".4" r=".75"><stop offset="0" stop-color="#FFE1A6"/><stop offset=".6" stop-color="#C9B23A"/><stop offset="1" stop-color="#6B6A1E"/></radialGradient>
    <radialGradient id="hn" cx=".45" cy=".4" r=".75"><stop offset="0" stop-color="#FFFFFF"/><stop offset="1" stop-color="#8CC6FF"/></radialGradient>
    <filter id="hs" x="-30%" y="-30%" width="160%" height="160%"><feDropShadow dx="3" dy="5" stdDeviation="4" flood-color="#7C93B8" flood-opacity=".45"/></filter></defs>`;
  const cells = S.cells.map((c, i) => {
    const [x, y] = axial(c.q, c.r);
    const fill = c.state === "new" ? "url(#hn)" : c.state === "harvest" ? "url(#hh)" : "url(#hg)";
    const op = c.state === "new" ? 1 : 0.55 + Math.min(c.od, 2) / 4.5;
    return `<g class="cell ${i === newIdx ? "new" : ""}" data-i="${i}" style="transform-origin:${x}px ${y}px">
      <polygon points="${hexPts(x, y, HX)}" fill="#F3F6FA" filter="url(#hs)"/>
      <polygon points="${hexPts(x, y, HX - 4)}" fill="${fill}" opacity="${op.toFixed(2)}"/>
      <polygon points="${hexPts(x, y, HX - 4)}" fill="none" stroke="#fff" stroke-opacity=".7" stroke-width="1"/>
      <circle cx="${x}" cy="${y}" r="6" fill="#F7F9FC"/><circle cx="${x}" cy="${y}" r="4" fill="none" stroke="#2F7BFF" stroke-width="1.4"/>
      <text x="${x}" y="${y + 19}" text-anchor="middle" font-size="7.5" font-weight="800" fill="#fff" opacity=".9">${c.id}</text></g>`;
  }).join("");
  svg.innerHTML = defs + cells;
  // fit
  const xs = S.cells.map(c => axial(c.q, c.r)[0]), ys = S.cells.map(c => axial(c.q, c.r)[1]);
  const pad = HX + 12, x0 = Math.min(...xs) - pad, x1 = Math.max(...xs) + pad, y0 = Math.min(...ys) - pad, y1 = Math.max(...ys) + pad;
  svg.setAttribute("viewBox", `${x0} ${y0} ${x1 - x0} ${y1 - y0}`);
  $$(".cell", svg).forEach(g => g.addEventListener("click", () => openSheet(+g.dataset.i)));
  $("#kMods").textContent = S.cells.length;
}
function addModule() {
  const taken = new Set(S.cells.map(c => c.q + "," + c.r));
  const dirs = [[1, 0], [1, -1], [0, -1], [-1, 0], [-1, 1], [0, 1]];
  for (const c of S.cells) for (const [dq, dr] of dirs) {
    const k = (c.q + dq) + "," + (c.r + dr);
    if (!taken.has(k)) {
      S.cells.push({ q: c.q + dq, r: c.r + dr, id: "N-" + String(S.cells.length + 1).padStart(2, "0"), od: 0.3, state: "new" });
      renderHive(S.cells.length - 1); toast(T("toast_new"), "ic_bolt");
      setTimeout(() => { const n = S.cells[S.cells.length - 1]; if (n) { n.state = "ok"; renderHive(); } }, 2600);
      return;
    }
  }
}

// ----------------------------------------------------------------- sheet ---
function openSheet(i) {
  const c = S.cells[i]; if (!c) return;
  $("#shId").textContent = c.id;
  $("#shTitle").textContent = (lang === "id" ? "Modul " : "Module ") + c.id;
  const m = { ...S, od: c.od, ph: S.ph + (i % 3 - 1) * 0.05, temp: S.temp + (i % 4) * 0.2 };
  renderSensors("#shSensors", m);
  $("#shLink").textContent = lang === "id" ? "Daya 24 V · data CAN · 6 tetangga terdeteksi" : "24 V power · CAN data · 6 neighbours found";
  $("#shFlow").textContent = lang === "id" ? "38 ml/menit · katup terbuka" : "38 ml/min · valves open";
  $("#scrim").classList.add("on"); $("#sheet").classList.add("on");
}
function closeSheet() { $("#scrim").classList.remove("on"); $("#sheet").classList.remove("on"); }

// ------------------------------------------------------------------ care ---
function renderCare() {
  const now = new Date(), hm = now.getHours() * 60 + now.getMinutes();
  const steps = T("care");
  let runSet = false;
  $("#careTL").innerHTML = steps.map(([t, h, p], i) => {
    const [H, Mi] = t.split(":").map(Number), m = H * 60 + Mi;
    let cls = m <= hm ? "done" : (!runSet ? (runSet = true, "run") : "");
    if (DEMO && i < 2) cls = "done"; if (DEMO && i === 2) cls = "run"; if (DEMO && i > 2) cls = "";
    return `<div class="st ${cls}"><span class="n">${i + 1}</span><h3>${h}<em>${t}</em></h3><p>${p}</p></div>`;
  }).join("");
}
function renderTanks() {
  [["tNut", "nut"], ["tWat", "wat"], ["tHar", "harv"]].forEach(([id, k]) => {
    $("#" + id).style.height = S[k] + "%"; $("#" + id + "V").textContent = Math.round(S[k]) + "%";
  });
}

// -------------------------------------------------------------------- AI ---
function renderChart() {
  const W = 340, H = 150, n = 14;
  const act = Array.from({ length: 8 }, (_, i) => 0.4 + 1.5 / (1 + Math.exp(-(i - 4) * 0.7)) + (Math.sin(i * 1.7) * 0.03));
  const pred = Array.from({ length: n }, (_, i) => 0.4 + 1.5 / (1 + Math.exp(-(i - 4) * 0.7)));
  const X = i => 12 + i / (n - 1) * (W - 24), Y = v => H - 10 - v / 2.2 * (H - 30);
  const path = a => a.map((v, i) => (i ? "L" : "M") + X(i).toFixed(1) + " " + Y(v).toFixed(1)).join(" ");
  const area = path(act) + ` L${X(act.length - 1)} ${H - 10} L${X(0)} ${H - 10} Z`;
  const hx = X(9.5);
  $("#chart").innerHTML = `<defs><linearGradient id="ca" x1="0" y1="0" x2="0" y2="1"><stop offset="0" stop-color="#2FB86A" stop-opacity=".35"/><stop offset="1" stop-color="#2FB86A" stop-opacity="0"/></linearGradient></defs>
    ${[0.5, 1, 1.5, 2].map(v => `<line x1="12" x2="${W - 12}" y1="${Y(v)}" y2="${Y(v)}" stroke="#C6D2E3" stroke-dasharray="3 5"/><text class="ax" x="${W - 10}" y="${Y(v) - 3}" text-anchor="end">${v}</text>`).join("")}
    <line x1="${hx}" x2="${hx}" y1="14" y2="${H - 10}" stroke="#F5A524" stroke-width="2" stroke-dasharray="4 4"/>
    <text class="ax" x="${hx + 4}" y="22" style="fill:#F5A524">${lang === "id" ? "panen" : "harvest"}</text>
    <path d="${area}" fill="url(#ca)"/>
    <path d="${path(pred)}" fill="none" stroke="#2F7BFF" stroke-width="2.5" stroke-dasharray="6 6" stroke-linecap="round"/>
    <path d="${path(act)}" fill="none" stroke="#2FB86A" stroke-width="3.5" stroke-linecap="round" style="filter:drop-shadow(0 4px 6px rgba(47,184,106,.4))"/>
    <circle cx="${X(7)}" cy="${Y(act[7])}" r="6" fill="#fff" stroke="#2FB86A" stroke-width="3"/>`;
}
function renderInsights() {
  $("#insights").innerHTML = T("ins").map(([ic, h, p]) => `<div class="li"><div class="ic"><img src="assets/img/${ic}.png" alt=""></div><div class="t"><h3>${h}</h3><p>${p}</p></div></div>`).join("");
}

// ---------------------------------------------------------------- light ---
function setLight(k, b) {
  S.cct = k; S.bri = b;
  $("#cct").value = k; $("#bri").value = b;
  $("#dialV").textContent = k; $("#briV").textContent = b + "%";
  const p = (k - 2700) / 3800;
  $("#dialArc").setAttribute("stroke-dasharray", `${(0.75 * 2 * Math.PI * 94 * Math.max(.02, p)).toFixed(1)} 1000`);
}

// --------------------------------------------------------------- toast ---
let tt;
function toast(msg, ic = "ic_leaf") {
  const el = $("#toast"); $("span", el).textContent = msg; $("img", el).src = `assets/img/${ic}.png`;
  el.classList.add("on"); clearTimeout(tt); tt = setTimeout(() => el.classList.remove("on"), 2600);
}

// ------------------------------------------------------------ navigation --
const ORDER = ["home", "hive", "light", "care", "ai"];
let cur = "home";
function go(name) {
  if (!ORDER.includes(name) || name === cur) return;
  const a = ORDER.indexOf(cur), b = ORDER.indexOf(name);
  const from = $("#s-" + cur), to = $("#s-" + name);
  from.classList.remove("active"); from.classList.toggle("left", b > a);
  to.classList.remove("left"); to.scrollTop = 0; to.classList.add("active");
  $$("#nav button").forEach(x => x.classList.toggle("on", x.dataset.go === name));
  cur = name;
  if (name === "ai") renderChart();
  if (name === "care") renderTanks();
}
function setMode(m) {
  S.mode = m; seedCells(); renderHive();
  $$("#modes .mode").forEach(x => x.classList.toggle("on", x.dataset.mode === m));
}

// ------------------------------------------------------------------ demo --
function count(el, to, dec = 0) {
  const from = parseFloat(el.textContent.replace(",", ".")) || 0, t0 = performance.now();
  const step = t => { const k = Math.min(1, (t - t0) / 900), e = 1 - Math.pow(1 - k, 3);
    el.textContent = (from + (to - from) * e).toFixed(dec); if (k < 1) requestAnimationFrame(step); };
  requestAnimationFrame(step);
}
function tick() {
  const t = Date.now() / 1000;
  S.ph = 7.4 + Math.sin(t / 9) * 0.06; S.temp = 27.6 + Math.sin(t / 13) * 0.4; S.od = 1.42 + Math.sin(t / 20) * 0.03;
  S.lux = 5400 + Math.sin(t / 7) * 300; S.co2in = 640 + Math.sin(t / 5) * 25; S.dox = 8.6 + Math.sin(t / 11) * 0.2;
  S.co2 += 0.6; S.o2 += 0.44; S.score = 92 + Math.sin(t / 15) * 2;
  count($("#kCO2"), S.co2); count($("#kO2"), S.o2);
  $$("#sensors .v").forEach(v => { const s = SENS.find(x => x[1] === v.dataset.k); if (s) v.firstChild.textContent = s[6](S[s[1]]); });
}

// ------------------------------------------------------------------ init --
function init() {
  seedCells(); renderHive(); applyText(); setLight(S.cct, S.bri); renderTanks(); renderChart();
  $$("[data-go]").forEach(b => b.addEventListener("click", e => { e.preventDefault(); go(b.dataset.go); }));
  $$("#modes .mode").forEach(b => b.addEventListener("click", () => { setMode(b.dataset.mode); toast(T("toast_mode") + T("m_" + b.dataset.mode), "m_" + b.dataset.mode); }));
  $("#langBtn").addEventListener("click", () => { lang = lang === "id" ? "en" : "id"; localStorageSet("alg_lang", lang); applyText(); renderChart(); });
  $("#addMod").addEventListener("click", addModule);
  $("#scanMod").addEventListener("click", () => toast(lang === "id" ? `${S.cells.length} modul terpindai · semua sehat` : `${S.cells.length} modules scanned · all healthy`, "ic_ai"));
  $("#scrim").addEventListener("click", closeSheet); $("#shClose").addEventListener("click", closeSheet);
  $("#cct").addEventListener("input", e => setLight(+e.target.value, S.bri));
  $("#bri").addEventListener("input", e => setLight(S.cct, +e.target.value));
  $$("#scenes .scene").forEach(b => b.addEventListener("click", () => {
    $$("#scenes .scene").forEach(x => x.classList.remove("on")); b.classList.add("on"); setLight(+b.dataset.k, +b.dataset.b); }));
  $$("[data-tg]").forEach(b => b.addEventListener("click", () => b.classList.toggle("on")));
  $("#harvestBtn").addEventListener("click", () => { S.harv = Math.min(100, S.harv + 12); renderTanks(); toast(T("toast_harv"), "ic_leaf"); });
  setTimeout(() => $("#splash").classList.add("off"), qs.has("nosplash") ? 0 : 1400);
  if (DEMO) { tick(); setInterval(tick, 2000); setInterval(() => { S.nut = Math.max(20, S.nut - 0.2); S.harv = Math.min(95, S.harv + 0.15); if (cur === "care") renderTanks(); }, 3000); }
  if ("serviceWorker" in navigator && location.protocol.startsWith("http")) navigator.serviceWorker.register("sw.js").catch(() => {});
}
// API for recorder / showreel
window.APP = { go, setMode, addModule, openSheet, closeSheet, setLight, toast, set: o => Object.assign(S, o), state: S,
  lang: l => { lang = l; applyText(); renderChart(); } };
document.addEventListener("DOMContentLoaded", init);
})();
