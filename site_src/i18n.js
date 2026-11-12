// Language (id/en) and theme (dark/light) switching. Indonesian text lives in the HTML; English lives here.
const EN = {
  nav1: "Module", nav2: "Build", nav3: "Cycle", nav4: "App", nav5: "Specs", nav6: "Gallery", try: "Try the app",
  h_tag: "ALGORA M1 · MODULAR MICROALGAE PHOTOBIOREACTOR",
  h1a: "Absorb.", h1b: "Grow.", h1c: "Glow.",
  h_p: "A modular hexagon lamp filled with living <i>Chlorella</i> microalgae that absorbs CO₂, releases O₂ and looks after itself with sensors and an ESP32.",
  h_b1: "Explore the module ↓", h_b2: "Try the demo app", tick: "ROOM CO₂ · SIMULATED",
  hs1: "MODULE", hs2: "CULTURE", hs2v: "1.7 L Chlorella", hs3: "LIGHT", hs3v: "31 LEDs · 16 h",
  strip: "<span>ABSORBS CO₂</span><b>◆</b><span>RELEASES O₂</span><b>◆</b><span>2-IN-1 ROOM LAMP</span><b>◆</b><span>SELF-MAINTAINING · ESP32</span><b>◆</b><span>CNC-CUT · 5 ACRYLIC LAYERS</span><b>◆</b><span>MODULAR LIKE A HONEYCOMB</span><b>◆</b><span>ABSORBS CO₂</span><b>◆</b><span>RELEASES O₂</span><b>◆</b><span>2-IN-1 ROOM LAMP</span><b>◆</b><span>SELF-MAINTAINING · ESP32</span><b>◆</b><span>CNC-CUT · 5 ACRYLIC LAYERS</span><b>◆</b><span>MODULAR LIKE A HONEYCOMB</span><b>◆</b>",
  p_tag: "02 · THE PROBLEM", k1: "Our rooms are", k2: "full of <em class=\"warm\">CO₂.</em>", k3: "Plants need", k4: "space & <em class=\"grad\">time.</em>",
  c1k: "OUTDOOR CO₂", c1p: "The starting point. In crowded, poorly ventilated classrooms, CO₂ climbs far above it.",
  c2k: "PER 1 KG OF ALGAL BIOMASS", c2p: "Microalgae fix CO₂ more efficiently than land plants because every cell touches the water directly.",
  c3k: "LIGHT PATH", c3p: "Photobioreactors are usually large lab equipment. ALGORA is just 4 cm thick and hangs on a wall.",
  f1h: "Stuffy air", f1p: "Classrooms and small homes often have limited ventilation.", f2h: "Forgotten care", f2p: "Indoor plants wilt without a watering and light routine.",
  f3h: "Closed technology", f3p: "Photobioreactors rarely appear as everyday objects.", f4h: "Lamp energy", f4p: "Lamps are on every night — why not grow algae at the same time?",
  e_tag: "03 · ALGORA M1 · EXPLODED", e_h: "Five layers.<br><span class=\"grad\">One ecosystem.</span>",
  e_p: "A clear front sheet, three 10 mm frame rings and a frosted back sheet, bonded with silicone into a 30 mm culture chamber.",
  pA: "01 · FRONT SHEET A · CLEAR 5 MM", pC: "02 · RINGS C1–C3 · 3 × 10 MM, R4", pW: "03 · CHLORELLA CULTURE · ~1.7 L", pL: "04 · LED STRIP · 31 × WS2812B",
  pB: "05 · BACK SHEET B · FROSTED 5 MM", pG: "06 · CABLE GLANDS P1–P4",
  b_tag: "04 · MODULAR LIKE A HONEYCOMB", b_h: "Stack.<br>Connect.<br><span class=\"grad\">Breathe.</span>",
  b_p: "Every module has its own light; one main module carries the ESP32 brain and the sensors. Add modules and watch the numbers change.",
  mods: "MODULES", mw: "WALL", ml: "LAMP", mf: "FLOOR", r1: "CULTURE", r3: "CO₂ / DAY*", r4: "AVERAGE POWER*",
  b_fine: "*Simulated: peak uptake 0.27 g CO₂/day and 5.2 W average per module (growth rate 0.35/day).",
  y_tag: "05 · SELF-MAINTAINING, 24 H", y_h: "Days grow.<br><span class=\"grad\">Nights glow.</span>", s2: "AIR PUMP", s3: "NUTRIENTS", s4: "POWER 12 V",
  st1: "<b>Read sensors</b> — water temperature, light, algae density (OD) and CO₂ every 60 seconds.",
  st2: "<b>Set the light</b> by the clock: grow 06–18, room light 18–22, off at night.",
  st3: "<b>Aerate</b> 10 minutes every 30 minutes to mix the culture and supply CO₂.",
  st4: "<b>Dose nutrients</b> once a day and warn when the temperature leaves 20–32 °C.",
  st5: "<b>Send data</b> as JSON over Wi-Fi to your phone.",
  y_fine: "Power data from a simulation of the firmware logic (5.2 W average · 126 Wh/day).",
  a_tag: "06 · APP", a_h: "Every module.<br><span class=\"grad\">One hand.</span>",
  a_p: "Track CO₂ captured, algae density, light and the care schedule. It currently runs in demo mode with simulated data.", a_b: "Open the demo app →",
  sp_tag: "07 · PROTOTYPE SPECS", sp_h: "CNC precision.<br><span class=\"grad\">Honest numbers.</span>",
  t1: "ACROSS FLATS", t2: "ACROSS CORNERS", t2v: "346.4 mm", t3: "THICKNESS", t4: "CULTURE CHAMBER", t4v: "2.0 L", t4s: "filled ~1.7 L",
  t5: "FILLED MASS", t5v: "~3.1 kg", t6: "INNER CORNERS", t6s: "CNC end mill", t7: "CUTTING PATH", t7v: "8.24 m", t7s: "~37 minutes", t8: "CONTROLLER",
  t9s: "temp · lux · OD · CO₂", t10: "POWER", t10v: "5.2 W*", t10s: "max 9.1 W", t11: "BIOMASS, 14 DAYS*", t11v: "0.46–0.98", t12: "60 L BOX · 2 H*", t12s: "ppm CO₂ (control −10)",
  sp_fine: "*Calculated and simulated with stated assumptions; physical testing is the next step.",
  g_tag: "08 · DRAWINGS & RENDERS", g_h: "From DXF<br><span class=\"grad\">to the wall.</span>", g1: "TECHNICAL DRAWINGS", g2: "3D RENDERS",
  v_h: "See ALGORA<br><span class=\"grad\">at work.</span>", v1: "SHOWREEL · 60 SECONDS", v2: "3D TECHNICAL DRAWING · EXPLODED · 360° · CLOSE-UP",
  z_h: "Clean air,<br><span class=\"grad\">one hexagon at a time.</span>",
  z_p: "Made by a team of students from SMP Muhammadiyah Program Khusus (PK) Kottabarat Surakarta, mentored by Mersif Academy, for the I2ASPO 2026 competition.",
  z_d1: "Technical drawings (PDF)", z_d2: "Technical document (PDF)",
  ft1: "ALGORA · MODULAR · ALIVE · SELF-MAINTAINING", ft2: "© 2026 TEAM ALGORA · RENDERS: SKETCHFAB CC-BY, MAKEHUMAN CC0",
};

window.ALG = Object.assign(window.ALG || {}, { lang: document.documentElement.lang === "en" ? "en" : "id", theme: document.documentElement.dataset.theme || "dark" });
window.t = (id, en) => (window.ALG.lang === "en" ? en : id);
const nodes = [...document.querySelectorAll("[data-i18n]")];
nodes.forEach(el => { el.dataset.id = el.innerHTML; });

function setLang(l) {
  window.ALG.lang = l; document.documentElement.lang = l;
  nodes.forEach(el => { const en = EN[el.dataset.i18n]; el.innerHTML = l === "en" && en ? en : el.dataset.id; });
  document.getElementById("langLbl").textContent = l === "en" ? "ID" : "EN";
  document.title = l === "en" ? "ALGORA — Absorb. Grow. Glow." : "ALGORA — Serap. Tumbuh. Bersinar.";
  try { localStorage.setItem("alg-lang", l); } catch (e) {}
  dispatchEvent(new CustomEvent("alg:lang", { detail: l }));
}
function setTheme(th) {
  window.ALG.theme = th; document.documentElement.dataset.theme = th;
  document.querySelector('meta[name="theme-color"]').content = th === "light" ? "#EEF3FA" : "#050B16";
  try { localStorage.setItem("alg-theme", th); } catch (e) {}
  dispatchEvent(new CustomEvent("alg:theme", { detail: th }));
}
document.getElementById("langBtn").onclick = () => setLang(window.ALG.lang === "en" ? "id" : "en");
document.getElementById("themeBtn").onclick = () => setTheme(window.ALG.theme === "light" ? "dark" : "light");
setLang(window.ALG.lang); setTheme(window.ALG.theme);
