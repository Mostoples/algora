# Algora

Fotobioreaktor mikroalga modular berbentuk hexagon akrilik. Satu modul bisa dipakai sebagai **dinding, lantai/paving, lampu, atau genting**, dan dirawat otomatis oleh sistem AIoT. Semua visual dihasilkan oleh skrip, jadi revisi cukup dengan mengubah konstanta lalu menjalankan ulang skripnya.

## Struktur

| Path | Isi |
|---|---|
| `app/` | Web app HTML/CSS/JS native (neumorph putih-biru), bilingual ID/EN, PWA. Buka `app/index.html` (mode demo otomatis). `window.APP` = API untuk recorder. |
| `blender/lib.py` | Library bersama: palet, `DIM` (mm), material akrilik/alga, `hex_module()`, `import_glb()` (Sketchfab), `make_human()` (MPFB + **Rigify**). |
| `blender/assets.py` | Ikon dan aset 3D app (PNG transparan) → `app/assets/img/`. |
| `blender/scenes.py` | 4 scene in-use: `wall`, `floor`, `lamp`, `roof` (still konsep). |
| `blender/film.py` | Shot animasi `hero wall floor lamp roof` (frame per frame, auto-resume) → `output/frames/<shot>/`. |
| `showreel/record.py` | Merekam app (Playwright + CDP screencast) → `showreel/build/rec_<lang>/`. |
| `showreel/compose.py` | Merakit showreel 1080p (PIL + FFmpeg + musik synth numpy) → `output/ALGORA_showreel_<lang>.mp4`. |
| `showreel/concept_board.py` | Papan konsep A1/B1–B4 → `output/concept/`. |
| `tools/` | `sf_search.py`/`sf_download.py` (Sketchfab API), `render_all.sh`, `test_shots.sh`, `app_shots.py`, `sheet.py`. |

## Build ulang

```sh
B="/c/Program Files/Blender Foundation/Blender 5.2/blender.exe"
python tools/sf_download.py                                  # aset Sketchfab + CREDITS.json (token di tools/.sketchfab_token, atau env SKETCHFAB_TOKEN)
"$B" -b --factory-startup -P blender/assets.py -- app/assets/img
ALG_RES=960 "$B" -b -P blender/scenes.py -- output/concept wall      # still konsep
./tools/render_all.sh                                        # semua shot final (1280x720, 40 spp)
python showreel/record.py id && python showreel/record.py en
python showreel/compose.py id && python showreel/compose.py en
```

Env render: `ALG_W/ALG_H` (default 1280×720, di-upscale ke 1080p saat compose), `ALG_SPP` (40), `ALG_STEP` (frame jarang untuk uji), `ALG_OUT`.

## Desain modul (`DIM`, mm)

- Hexagon flat-to-flat 300, tebal 42.
- Rim polimer 11, sheet akrilik 5 mm (atas bening, bawah frosted/difuser).
- 6 sekat radial, inti AIoT Ø68 (sensor pH/suhu/OD/cahaya, cincin LED, diffuser gelembung).
- LED tepi di dalam rim.
- Pad konektor di 6 sisi: 2 pin pogo magnet (daya 24 V + data CAN) dan 1 port fluida quick-connect.
- Mode paving memakai rim abu dan akrilik tebal anti-slip. Mode genting memakai daylight (tanpa LED).

## Karakter

MakeHuman/MPFB (CC0) dengan rig dari add-on **Rigify** Blender. Metarig `rigify.human` di-generate, lalu mesh tubuh dan pakaian di-retarget ke rig kontrol. Pose dibuat lewat kontrol IK (`hand_ik.*`, `foot_ik.*`, `torso`, `head`) dengan IK stretch dimatikan. Siklus jalan dibuat prosedural (`pose_walk`).

## Kredit aset 3D (Sketchfab, CC Attribution)

| Aset | Pembuat | Link |
|---|---|---|
| Modern  Sofa | 3dimentionalben | https://sketchfab.com/3d-models/modern-sofa-ac92f6e97eaa43c4ad6cb8f7c65ac43f |
| Monstera Deliciosa Potted Mid-Century plant | Giora | https://sketchfab.com/3d-models/monstera-deliciosa-potted-mid-century-plant-1ab9bf841df04c07b1819be596327629 |
| [FREE] Pothos Potted Plant - Money Plant | AllQuad | https://sketchfab.com/3d-models/free-pothos-potted-plant-money-plant-e9832f38484f4f85b3f9081b51fa3799 |
| [FREE] Dyspis Lutescens - Potted Palm | AllQuad | https://sketchfab.com/3d-models/free-dyspis-lutescens-potted-palm-92f75abd656049608248cf76a8c88136 |
| Japanese Maple Tree | OliverMatheGames | https://sketchfab.com/3d-models/japanese-maple-tree-b6eb627413ed40fdb8b0a1e1c9038fa9 |
| Garden Lounge | scailman | https://sketchfab.com/3d-models/garden-lounge-cd2c67402ea8426c90d0fcebb0fa60b4 |
| Modern Bench 1 | Elasta Kristya | https://sketchfab.com/3d-models/modern-bench-1-caa4515e36444e4c8c100296463e83c1 |
| [Free] Dining Set Scandinavian Style | AllQuad | https://sketchfab.com/3d-models/free-dining-set-scandinavian-style-61275205fe084208887d74876919aac6 |

Catatan lisensi:
- `prayer_plant` (CC **NonCommercial**) dan `phone` sudah diunduh tetapi **tidak dipakai**. Ponsel dibuat prosedural dengan screenshot app asli.
- Karena CC-BY, cantumkan kredit di deskripsi video atau publikasi.

## Keputusan klien

- Mode pemasangan: dinding, lantai/paving, lampu, genting.
- Konsep A1, B1–B4 disetujui. Render Cycles 1280p + upscale.

## Asumsi / konsep (belum diverifikasi)

- Angka CO₂/O₂, skor bio, prediksi panen, dan seluruh data sensor di app adalah **data simulasi** (mode demo). Belum ada backend atau firmware.
- Base station (pompa, tangki nutrien/panen, UV-C, gateway ESP32) baru konsep dan belum dimodelkan 3D.
- Dimensi modul masih estimasi desain, belum hasil uji struktur. Mode paving butuh uji beban dan anti-slip.
