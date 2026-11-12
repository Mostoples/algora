"""Calculations and simulations for the paper (results chapter).
python tools/paper_sims.py -> output/paper/sim_results.json, fig_sim_control.png, fig_sim_growth.png
All assumptions are listed in ASSUME and printed into the JSON so the paper can state them."""
import json, math, os
import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "output", "paper")
D = json.load(open(os.path.join(ROOT, "output", "cnc", "dims.json")))
plt.rcParams.update({"font.family": "Arial", "font.size": 9, "axes.spines.top": False, "axes.spines.right": False})
BLUE, GREEN, ORANGE, GREY, RED = "#1F6FEB", "#2EA043", "#E5822B", "#8A94A6", "#D64545"

ASSUME = dict(
    feed_mm_min=1000, pass_depth_mm=2.0,                       # CNC: typical acrylic router setting (assumed)
    led_ma_per_channel_full=20.0, brightness=128,              # WS2812B: ~20 mA per colour channel at 255
    esp32_w=1.3, sensors_w=0.5, buck_eff=0.85, pump_air_w=3.6, pump_dose_w=3.6, dose_s=3, ambient_lux="< 2000 lux all day (indoor)",
    x0_g_l=0.05, xmax_g_l=1.0, mu_low=0.20, mu_mid=0.35, mu_high=0.50, days=14, vol_l=1.7, co2_per_biomass=1.83,
    box_l=60.0, box_c0_ppm=1000.0, leak_ppm_h=5.0, temp_c=25.0,
)
A = ASSUME
R = D["FLAT"] / math.sqrt(3); R_IN = D["FLAT_IN"] / math.sqrt(3); RF = D["R_IN_FILLET"]

# ------------------------------------------------------------ 1. CNC -----
def poly_area_perim(pts):
    a = 0.5 * abs(sum(pts[i][0] * pts[i - 1][1] - pts[i - 1][0] * pts[i][1] for i in range(len(pts))))
    p = sum(math.dist(pts[i], pts[i - 1]) for i in range(len(pts)))
    return a, p

def hexpts(flat):
    r = flat / math.sqrt(3); return [(r * math.cos(math.radians(a)), r * math.sin(math.radians(a))) for a in range(0, 360, 60)]

def fillet_pts(pts, r, seg=64):
    out = []
    for i in range(len(pts)):
        V, Pp, N = np.array(pts[i]), np.array(pts[i - 1]), np.array(pts[(i + 1) % len(pts)])
        u1 = (Pp - V) / np.linalg.norm(Pp - V); u2 = (N - V) / np.linalg.norm(N - V)
        th = math.acos(np.clip(u1 @ u2, -1, 1)); C = V + (u1 + u2) / np.linalg.norm(u1 + u2) * (r / math.sin(th / 2))
        T1, T2 = V + u1 * r / math.tan(th / 2), V + u2 * r / math.tan(th / 2)
        a1, a2 = math.atan2(*(T1 - C)[::-1]), math.atan2(*(T2 - C)[::-1])
        while a2 < a1: a2 += 2 * math.pi
        out += [tuple(C + r * np.array([math.cos(a), math.sin(a)])) for a in np.linspace(a1, a2, seg)]
    return out

a_out, p_out = poly_area_perim(hexpts(D["FLAT"]))
a_in, p_in = poly_area_perim(fillet_pts(hexpts(D["FLAT_IN"]), RF))
holes = D["HOLES"]; p_holes = sum(math.pi * h["d"] for h in holes); a_holes = sum(math.pi * h["d"] ** 2 / 4 for h in holes)
parts = [("A front sheet", 1, D["T_SHEET"], a_out, p_out), ("B back sheet", 1, D["T_SHEET"], a_out - a_holes, p_out + p_holes),
         ("C frame ring", D["N_RING"], D["T_RING"], a_out - a_in, p_out + p_in)]
cnc = []
for name, n, t, area, perim in parts:
    passes = math.ceil(t / A["pass_depth_mm"]); path = perim * passes * n
    cnc.append(dict(part=name, qty=n, t=t, area_cm2=area / 100, cut_m=perim * n / 1000, passes=passes,
                    time_min=path / A["feed_mm_min"], mass_g=area * t * n * 1.19e-3))
cnc_tot = dict(cut_m=sum(c["cut_m"] for c in cnc), time_min=sum(c["time_min"] for c in cnc), mass_g=sum(c["mass_g"] for c in cnc))
scrap_inner_cm2 = a_in / 100

# ------------------------------------------------- 2. 24-hour control -----
def led_w(rgb):
    ma = A["led_ma_per_channel_full"] * (A["brightness"] / 255) * sum(rgb) / 255
    return 31 * ma / 1000 * 5.0
GROW, ROOM = (255, 0, 120), (255, 160, 60)
t = np.arange(0, 24 * 60)                       # minutes
hour = t / 60
led = np.where((hour >= 6) & (hour < 18), led_w(GROW), np.where((hour >= 18) & (hour < 22), led_w(ROOM), 0.0))
air = np.where((t % 30) < 10, A["pump_air_w"], 0.0)
base5 = A["esp32_w"] + A["sensors_w"]
p12 = (base5 + led) / A["buck_eff"] + air
dose_wh = A["pump_dose_w"] * A["dose_s"] / 3600
e_led = led.sum() / 60; e_air = air.sum() / 60; e_tot = p12.sum() / 60 + dose_wh
ctrl = dict(led_grow_w=led_w(GROW), led_room_w=led_w(ROOM), led_hours=16, air_hours=float((air > 0).sum() / 60),
            p_min=float(p12.min()), p_max=float(p12.max()), p_avg=float(p12.mean()), e_day_wh=float(e_tot),
            e_led_wh=float(e_led / A["buck_eff"]), e_air_wh=float(e_air), e_month_kwh=float(e_tot * 30 / 1000))

fig, ax = plt.subplots(2, 1, figsize=(6.3, 3.1), gridspec_kw=dict(height_ratios=[1, 2.4]), sharex=True)
modes = np.where((hour >= 6) & (hour < 18), 2, np.where((hour >= 18) & (hour < 22), 1, 0))
for m, c, lab in ((2, "#C04DB8", "LED grow (red+blue)"), (1, "#F2B33D", "LED room (warm white)")):
    ax[0].fill_between(hour, 1.1, 1.9, where=modes == m, color=c, step="post", label=lab, lw=0)
ax[0].fill_between(hour, 0.1, 0.9, where=air > 0, color=BLUE, step="post", label="air pump", lw=0)
ax[0].set_yticks([0.5, 1.5]); ax[0].set_yticklabels(["pump", "LED"]); ax[0].set_ylim(0, 2); ax[0].spines["left"].set_visible(False)
ax[0].legend(loc="upper center", bbox_to_anchor=(0.5, 1.75), ncol=3, frameon=False, fontsize=8)
ax[1].step(hour, p12, where="post", color=INK if (INK := "#16233F") else "k", lw=0.8)
ax[1].axhline(ctrl["p_avg"], color=ORANGE, lw=1, ls="--"); ax[1].text(0.2, max(p12) * 1.12, f"average {ctrl['p_avg']:.1f} W (dashed)", ha="left", color=ORANGE, fontsize=8)
ax[1].set_ylabel("Power at 12 V (W)"); ax[1].set_xlabel("Time of day (h)"); ax[1].set_xlim(0, 24); ax[1].set_xticks(range(0, 25, 3))
ax[1].set_ylim(0, max(p12) * 1.25)
fig.tight_layout(h_pad=0.3); fig.savefig(os.path.join(P, "fig_sim_control.png"), dpi=300); plt.close(fig)

# ------------------------------------------- 3. growth and CO2 uptake -----
days = np.linspace(0, A["days"], 400)
def logistic(mu, d): return A["xmax_g_l"] / (1 + (A["xmax_g_l"] / A["x0_g_l"] - 1) * np.exp(-mu * d))
growth = {}
for key in ("low", "mid", "high"):
    mu = A["mu_" + key]; X = logistic(mu, days); x14 = float(logistic(mu, A["days"]))
    co2_total = A["co2_per_biomass"] * (x14 - A["x0_g_l"]) * A["vol_l"]
    peak_rate = mu * A["xmax_g_l"] / 4 * A["vol_l"] * A["co2_per_biomass"]       # g CO2 / day at inflection
    growth[key] = dict(mu=mu, x14=x14, co2_14d_g=co2_total, peak_co2_g_day=peak_rate, X=X)
g_per_ppm = A["box_l"] * 1e-6 * 44.01 / (0.08206 * (273.15 + A["temp_c"]))            # g CO2 per ppm in the box
box = {}
tb = np.linspace(0, 2, 121)
for key in ("low", "mid", "high"):
    rate_ppm_h = growth[key]["peak_co2_g_day"] * 1.5 / 24 / g_per_ppm               # light phase: 24/16 of daily mean
    box[key] = dict(rate_ppm_h=rate_ppm_h, drop_2h=rate_ppm_h * 2 + A["leak_ppm_h"] * 2)
ctrl_drop = A["leak_ppm_h"] * 2

fig, ax = plt.subplots(1, 2, figsize=(6.3, 2.5))
for key, c, ls in (("low", GREY, ":"), ("mid", GREEN, "-"), ("high", BLUE, "--")):
    ax[0].plot(days, growth[key]["X"], color=c, ls=ls, lw=1.4, label=f"μ = {growth[key]['mu']:.2f} /day")
    ax[1].plot(tb * 60, A["box_c0_ppm"] - (box[key]["rate_ppm_h"] + A["leak_ppm_h"]) * tb, color=c, ls=ls, lw=1.4)
ax[1].plot(tb * 60, A["box_c0_ppm"] - A["leak_ppm_h"] * tb, color=RED, lw=1.4, label="control (no algae)")
ax[0].set_xlabel("Day"); ax[0].set_ylabel("Biomass (g/L)"); ax[0].set_title("(a) Simulated growth, 1.7 L", fontsize=9, loc="left")
ax[0].legend(frameon=False, fontsize=7.5)
ax[1].set_xlabel("Time (min)"); ax[1].set_ylabel("CO2 in 60 L box (ppm)"); ax[1].set_title("(b) Simulated closed-box CO2", fontsize=9, loc="left")
ax[1].legend(frameon=False, fontsize=7.5, loc="lower left")
fig.tight_layout(); fig.savefig(os.path.join(P, "fig_sim_growth.png"), dpi=300); plt.close(fig)

out = dict(assume=A, cnc=cnc, cnc_total=cnc_tot, scrap_inner_cm2=scrap_inner_cm2, control=ctrl,
           growth={k: {kk: vv for kk, vv in v.items() if kk != "X"} for k, v in growth.items()},
           box=box, box_control_drop=ctrl_drop, g_per_ppm=g_per_ppm)
json.dump(out, open(os.path.join(P, "sim_results.json"), "w"), indent=1)
print(json.dumps({k: v for k, v in out.items() if k != "assume"}, indent=1))
