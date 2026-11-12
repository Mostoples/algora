"""Formulir panduan wawancara & pengamatan budidaya Spirulina (Albitec), A4, siap cetak.
python tools/panduan_wawancara.py -> output/dokumen/Panduan_Wawancara_Albitec.pdf"""
import os
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.colors import HexColor

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, "output", "dokumen", "Panduan_Wawancara_Albitec.pdf")
PW, PH = 210, 297
INK, MUTED, LINE, BLUE, BAND = HexColor("#16233F"), HexColor("#5B6B86"), HexColor("#B7C2D3"), HexColor("#1F6FEB"), HexColor("#EAF1FB")
L, R = 18, PW - 18

SECTIONS = [
    ("A", "Profil tempat budidaya", [
        ("Sejak kapan Albitec membudidayakan Spirulina? Untuk apa hasilnya dipakai?", 2),
        ("Spirulina jenis apa yang dibudidayakan? Dari mana bibit awalnya didapat?", 2),
        ("Seberapa besar skala budidayanya (jumlah wadah atau kolam, total volume)?", 2),
    ]),
    ("B", "Wadah dan sistem budidaya", [
        ("Wadah apa yang dipakai (kolam terbuka, raceway, tangki, fotobioreaktor)? Apa bahannya?", 2),
        ("Berapa ukuran, kedalaman, dan volume air setiap wadah?", 2),
        ("Bagaimana air diaduk atau diberi udara? Berapa lama dan seberapa sering?", 2),
    ]),
    ("C", "Air, media, dan nutrisi", [
        ("Air apa yang dipakai (tawar, payau, laut)? Berapa kadar garamnya?", 2),
        ("Nutrisi atau pupuk apa yang diberikan? Berapa takaran dan seberapa sering?", 2),
        ("Berapa pH yang dijaga? Bagaimana cara mengukur dan mengaturnya?", 2),
    ]),
    ("D", "Cahaya dan suhu", [
        ("Sumber cahaya dari matahari atau lampu? Berapa jam sehari? Jika lampu, jenis dan warnanya apa?", 2),
        ("Berapa suhu air yang paling baik? Apa yang dilakukan jika terlalu panas atau dingin?", 2),
    ]),
    ("E", "Pemantauan dan masalah", [
        ("Bagaimana cara mengetahui Spirulina tumbuh baik (warna, kekeruhan, mikroskop, alat ukur)?", 2),
        ("Masalah apa yang paling sering terjadi (kontaminasi, alga lain, bau, mengendap)? Cara mengatasinya?", 3),
        ("Alat ukur apa saja yang dipakai sehari-hari?", 2),
    ]),
    ("F", "Panen dan pascapanen", [
        ("Kapan Spirulina siap dipanen (hari ke berapa, tandanya apa)?", 2),
        ("Bagaimana cara memanen (saringan, ukuran mesh) dan berapa bagian yang diambil?", 2),
        ("Berapa hasil panen per wadah atau per liter? Bagaimana cara mengeringkan dan menyimpannya?", 2),
    ]),
    ("G", "Hubungan dengan alat Algora", [
        ("Algora berupa wadah akrilik tegak setebal 3 cm berisi 1,7 liter, diterangi lampu LED di dalam ruangan. "
         "Apakah Spirulina bisa tumbuh di wadah seperti ini? Apa yang perlu diperhatikan?", 3),
        ("Mana yang lebih cocok untuk wadah kecil di dalam ruangan: Spirulina atau Chlorella? Mengapa?", 2),
        ("Warna lampu dan lama penyinaran apa yang disarankan? Perlukah gelembung udara terus-menerus?", 2),
        ("Apa saran Bapak/Ibu untuk penelitian kami?", 2),
    ]),
]

def T(c, x, y, s, size=10, color=INK, bold=False, anchor="start", italic=False):
    c.setFillColor(color); c.setFont("Helvetica-BoldOblique" if bold and italic else "Helvetica-Bold" if bold else "Helvetica-Oblique" if italic else "Helvetica", size)
    {"start": c.drawString, "middle": c.drawCentredString, "end": c.drawRightString}[anchor](x * mm, y * mm, s)

def wrap(c, s, size, width, bold=False):
    font = "Helvetica-Bold" if bold else "Helvetica"
    words, lines, cur = s.split(), [], ""
    for w in words:
        t = (cur + " " + w).strip()
        if c.stringWidth(t, font, size) / mm > width and cur:
            lines.append(cur); cur = w
        else:
            cur = t
    return lines + [cur]

def lines(c, y, n, x0=L, x1=R, gap=7.5):
    c.setStrokeColor(LINE); c.setLineWidth(0.4); c.setDash([1, 1.5], 0)
    for k in range(n):
        y -= gap; c.line(x0 * mm, y * mm, x1 * mm, y * mm)
    c.setDash([], 0)
    return y

class Doc:
    def __init__(s):
        s.c = canvas.Canvas(OUT, pagesize=A4); s.c.setTitle("Panduan Wawancara Budidaya Spirulina - Albitec"); s.c.setAuthor("Kelompok Algora")
        s.page = 0; s.new_page()
    def new_page(s):
        if s.page: s.c.showPage()
        s.page += 1; c = s.c
        T(c, L, PH - 15, "Panduan Wawancara dan Pengamatan", 15, bold=True)
        T(c, L, PH - 21.5, "Budidaya Mikroalga Spirulina  ·  Albitec  ·  Kelompok Algora", 9.5, MUTED)
        c.setStrokeColor(INK); c.setLineWidth(0.8); c.line(L * mm, (PH - 27) * mm, R * mm, (PH - 27) * mm)
        T(c, PW / 2, 9, f"Halaman {s.page}", 8, MUTED, anchor="middle")
        s.y = PH - 34
    def need(s, h):
        if s.y - h < 16: s.new_page()
    def band(s, txt):
        s.need(34); c = s.c
        c.setFillColor(BAND); c.roundRect(L * mm, (s.y - 6.5) * mm, (R - L) * mm, 8.5 * mm, 2 * mm, stroke=0, fill=1)
        T(c, L + 3, s.y - 3.8, txt, 11, INK, bold=True); s.y -= 12

def build():
    d = Doc(); c = d.c
    # identitas
    d.band("Identitas wawancara")
    rows = [("Hari / tanggal", "Kamis, 29 Oktober 2026"), ("Tempat", "Albitec"), ("Nama narasumber", ""), ("Jabatan / peran", ""),
            ("Pewawancara", ""), ("Pencatat", ""), ("Dokumentasi (foto/video)", ""), ("Izin merekam / memotret", "BOX")]
    for k, v in rows:
        T(c, L + 2, d.y, k, 10, MUTED); T(c, L + 52, d.y, ":", 10, MUTED)
        if v == "BOX":
            for xx, lab in ((L + 55, "Diizinkan"), (L + 85, "Tidak diizinkan")):
                c.setStrokeColor(INK); c.setLineWidth(0.6); c.rect(xx * mm, (d.y - 0.6) * mm, 3.2 * mm, 3.2 * mm); T(c, xx + 5, d.y, lab, 10)
        elif v: T(c, L + 55, d.y, v, 10)
        else:
            c.setStrokeColor(LINE); c.setLineWidth(0.4); c.setDash([1, 1.5], 0); c.line((L + 55) * mm, (d.y - 1) * mm, R * mm, (d.y - 1) * mm); c.setDash([], 0)
        d.y -= 7.2
    d.y -= 3
    d.band("Petunjuk untuk pewawancara")
    tips = ["Perkenalkan diri dan kelompok, jelaskan tujuan: studi pendahuluan untuk lomba I2ASPO.",
            "Minta izin sebelum merekam suara, memotret, atau menyentuh peralatan.",
            "Bagi tugas: 2 orang bertanya, 2 orang mencatat, 1 orang memotret, 1 orang mengamati.",
            "Catat angka lengkap dengan satuannya (liter, cm, °C, gram, hari). Jika jawabannya kurang jelas, tanya \"mengapa?\" atau \"bisa dicontohkan?\".",
            "Jangan memotong jawaban narasumber. Tutup dengan ucapan terima kasih."]
    for i, tip in enumerate(tips):
        ls = wrap(c, tip, 9.5, R - L - 10)
        T(c, L + 3, d.y, f"{i + 1}.", 9.5, BLUE, bold=True)
        for j, ln in enumerate(ls): T(c, L + 9, d.y - j * 4.6, ln, 9.5)
        d.y -= 4.6 * len(ls) + 1.6
    d.y -= 2
    d.band("Contoh kalimat pembuka")
    op = ("\"Assalamualaikum, selamat siang Bapak/Ibu. Kami dari kelompok Algora, didampingi Mersif Academy. Kami sedang meneliti "
          "lampu hexagon berisi mikroalga untuk lomba I2ASPO. Hari ini kami ingin belajar langsung tentang cara budidaya Spirulina "
          "di Albitec. Apakah kami boleh bertanya, mencatat, dan mengambil foto?\"")
    for j, ln in enumerate(wrap(c, op, 9.5, R - L - 6)):
        T(c, L + 3, d.y - j * 4.6, ln, 9.5, INK, italic=True)
    d.y -= 4.6 * len(wrap(c, op, 9.5, R - L - 6)) + 4
    # pertanyaan
    no = 0
    for code, title, qs in SECTIONS:
        d.band(f"{code}. {title}")
        for q, n in qs:
            no += 1
            ql = wrap(c, q, 10, R - L - 10, bold=True)
            d.need(4.8 * len(ql) + 7.5 * n + 4)
            T(c, L + 1, d.y, f"{no}.", 10, BLUE, bold=True)
            for j, ln in enumerate(ql): T(c, L + 8, d.y - j * 4.8, ln, 10, INK, bold=True)
            d.y = lines(c, d.y - 4.8 * (len(ql) - 1), n, L + 8) - 5
    # angka penting
    d.new_page()
    d.band("Tabel angka penting (isi saat wawancara atau pengamatan)")
    rows = [("Volume air per wadah", "liter"), ("Kedalaman air", "cm"), ("Suhu air", "°C"), ("pH", "-"), ("Kadar garam", "ppt atau g/L"),
            ("Lama penyinaran", "jam/hari"), ("Lama aerasi / pengadukan", "jam/hari"), ("Takaran nutrisi", "g/L atau mL/L"),
            ("Waktu sampai panen", "hari"), ("Hasil panen", "gram per liter"), ("Ukuran mesh saringan panen", "µm")]
    x = [L, L + 72, L + 112]; rh = 9
    c.setStrokeColor(INK); c.setLineWidth(0.6); c.rect(L * mm, (d.y - rh * (len(rows) + 1)) * mm, (R - L) * mm, rh * (len(rows) + 1) * mm)
    for xx in x[1:]: c.line(xx * mm, d.y * mm, xx * mm, (d.y - rh * (len(rows) + 1)) * mm)
    for i, hd in enumerate(("Yang diukur", "Satuan", "Nilai dari narasumber / pengamatan")): T(c, x[i] + 2, d.y - 6, hd, 9.5, INK, bold=True)
    for r, (a, b) in enumerate(rows):
        yy = d.y - rh * (r + 1); c.setStrokeColor(LINE); c.setLineWidth(0.4); c.line(L * mm, yy * mm, R * mm, yy * mm)
        T(c, x[0] + 2, yy - 6, a, 9.5); T(c, x[1] + 2, yy - 6, b, 9.5, MUTED)
    d.y -= rh * (len(rows) + 1) + 9
    d.band("Lembar pengamatan (centang yang terlihat)")
    obs = [("Jenis wadah", ["Kolam terbuka", "Raceway", "Tangki/ember", "Tabung/fotobioreaktor"]),
           ("Pencahayaan", ["Matahari langsung", "Atap transparan", "Lampu", "Campuran"]),
           ("Pengadukan", ["Pompa udara/aerator", "Kincir/paddle", "Manual", "Tidak ada"]),
           ("Warna kultur", ["Hijau muda", "Hijau tua", "Hijau kebiruan", "Kekuningan/pucat"]),
           ("Alat ukur terlihat", ["Termometer", "pH meter", "Refraktometer", "Mikroskop"])]
    for k, opts in obs:
        T(c, L + 2, d.y, k, 10, INK, bold=True); xx = L + 42
        for o in opts:
            c.setStrokeColor(INK); c.setLineWidth(0.6); c.rect(xx * mm, (d.y - 0.6) * mm, 3.2 * mm, 3.2 * mm); T(c, xx + 4.5, d.y, o, 9); xx += 4.5 + c.stringWidth(o, "Helvetica", 9) / mm + 6
        d.y -= 8
    d.y -= 2
    d.band("Sketsa wadah / alur budidaya dan catatan tambahan")
    c.setStrokeColor(LINE); c.setLineWidth(0.6); c.setDash([2, 2], 0); c.roundRect(L * mm, 20 * mm, (R - L) * mm, (d.y - 22) * mm, 2 * mm); c.setDash([], 0)
    c.showPage(); c.save()
    print(OUT, d.page, "halaman")

if __name__ == "__main__":
    build()
