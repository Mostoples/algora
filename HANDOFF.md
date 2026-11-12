# Handoff: Algora showreel (2026-10-08)

## Status
- [x] Web app `app/` (ID/EN, demo mode) dan aset 3D UI `app/assets/img/`.
- [x] Konsep A1, B1–B4 disetujui klien. Render Cycles 1280×720, 40 spp.
- [x] Semua frame final ada di `output/frames/{hero,wall,floor,lamp,roof}`. Hero 0–80 dan floor sudah dirender ulang dengan perbaikan.
- [x] Rekaman app: `showreel/build/rec_id/` dan `rec_en/` (rec.mp4 + marks.json).
- [x] Showreel dirakit + QA: `output/ALGORA_showreel_id.mp4` & `_en.mp4` (60,6 dtk = 12 segmen 67,2 dtk − 11 xfade × 0,6). Perbaikan QA: label hero `bottom` dipindah ke kanan (dulu menabrak kartu caption).
- [ ] Sisa: review klien; opsional naikkan kontras teks kredit outro.

## Langkah berikutnya
```sh
cd /c/Users/mosto/Desktop/algora
python showreel/compose.py id      # -> output/ALGORA_showreel_id.mp4 (~70 dtk)
python showreel/compose.py en      # -> output/ALGORA_showreel_en.mp4
```
QA: ambil 1 frame per segmen dengan `ffmpeg -ss <t> -frames:v 1`, buat contact sheet lewat `python tools/sheet.py out.png 360 ...`, lalu cek:
- label exploded di hero (detik ±4–5);
- kartu caption tiap scene tidak menutupi aktor;
- xfade tidak patah;
- kredit CC-BY terbaca di outro.

## Catatan
- Jangan menyentuh proses `blender.exe` milik proyek `meguru`.
- Render panjang: jalankan detached (`powershell Start-Process ... bash -c tools/queue2.sh`), karena background task Claude ikut mati saat sesi berakhir.
- Bug yang sudah diperbaiki: Fresnel pada backface → TIR hitam (`lib.thin_glass`), `hide_render` pada empty tidak menurun ke children, dan IK stretch Rigify harus 0.

## File CNC hexagon (2026-10-13)
- `python cnc/make_cnc.py` -> `output/cnc/*.dxf|*.svg` (1:1 mm, layer POTONG_LUAR/POTONG_DALAM) + `output/dokumen/Algora_Gambar_Teknik_Hexagon.pdf` (A3, 5 lembar).
- Prototipe: 300 flat, tebal 40 (5 + 3x10 + 5), cincin dinding 11, sudut dalam R4 (pahat CNC), lubang P1 Ø15,2 dan P2-P4 Ø12,5.
- Jumlah potong diatur N_HEX di make_cnc.py (sekarang 1: A x1, B x1, C x3).
- Tidak ada CorelDRAW di PC ini: CDR dibuat operator dengan Import DXF/SVG lalu Save As.
- Buku rancangan (Claude Docs) bab 3 masih menyebut "potong laser"; perlu diubah ke CNC + R4.

## Video gambar teknik 3D untuk siswa (2026-10-13)
- Model: `blender/tech_video.py` (prototipe CNC, ukuran dari `output/cnc/dims.json`), 75 dtk, 2250 frame, Cycles 1920x1080 32 spp (~2,2 dtk/frame).
- Render detached: `tools/render_tech.sh` (auto-resume) -> `output/frames/tech/` ; log `output/render_tech.log` (baris TECHDONE saat selesai).
- Anchor label: `ALG_ANCHORS=1 blender -b -P blender/tech_video.py` -> `output/frames/tech/anchors.json` (hitung ulang setiap kali KEYS/anchor diubah).
- Komposit: `python showreel/tech_compose.py` -> `output/ALGORA_gambar_teknik_3D.mp4`; uji cepat `--test 17.5,46.5` (TECH_FR=folder frame uji).
- PDF siswa: `python cnc/make_smp.py` -> `output/dokumen/Algora_Gambar_Teknik_Versi_SMP.pdf`.

## Full paper I2ASPO (2026-11-10)
- `python tools/paper_cad.py` (DXF berukuran -> LibreCAD dxf2pdf -> fig_cad.png), `python tools/paper_sims.py` (CNC, kontrol 24 jam, pertumbuhan/CO2 -> sim_results.json + grafik), `python tools/paper_figs.py` (diagram EN), lalu `python tools/make_paper.py --pdf`.
- Output: `output/paper/ALGORA_Full_Paper.docx/.pdf` (cover s.d. Bab 5 = 12 halaman, References hal. 13). Hasil Bab 4 = CAD + perhitungan + simulasi berasumsi (tertulis di 3.5); belum ada data uji fisik.
