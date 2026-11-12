"""ALGORA full paper (I2ASPO format): Arial 12, single spacing, margins L4 R3 T3 B3 cm, justified, A4.
python tools/make_paper.py  ->  output/paper/ALGORA_Full_Paper.docx (+ .pdf via MS Word)
Text in [[double brackets]] is highlighted yellow: data the team must fill in from real measurements."""
import os, re, sys
from docx import Document
from docx.shared import Pt, Cm, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_BREAK, WD_COLOR_INDEX
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml.ns import qn
from docx.oxml import OxmlElement

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = os.path.join(ROOT, "output", "paper")
OUT = os.path.join(P, "ALGORA_Full_Paper.docx")

TITLE = "ALGORA: A MULTIPURPOSE MODULAR MICROALGAE PHOTOBIOREACTOR LAMP WITH A SELF-MAINTAINED SYSTEM BASED ON AIoT"
AUTHORS = ["Naura Prashanti", "Anabella Mercya Widianto", "Shafiya Ghaisani Althafunnisa", "Kayla Aulia Khairunnisa",
           "Tsaqif Alfarizqi W", "Naufal Dzaky Hamdhani"]
INSTITUTION = "SMP MUHAMMADIYAH PROGRAM KHUSUS (PK) KOTTABARAT SURAKARTA"
YEAR = "2026"

doc = Document()
st = doc.styles["Normal"]; st.font.name = "Arial"; st.font.size = Pt(12)
st.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
pf = st.paragraph_format; pf.line_spacing = 1.0; pf.space_before = Pt(0); pf.space_after = Pt(6)
for name, size in (("Heading 1", 12), ("Heading 2", 12), ("Heading 3", 12)):
    h = doc.styles[name]; h.font.name = "Arial"; h.font.size = Pt(size); h.font.bold = True; h.font.italic = False
    h.font.color.rgb = RGBColor(0, 0, 0); h.element.rPr.rFonts.set(qn("w:eastAsia"), "Arial")
    rf = h.element.rPr.rFonts
    for a in ("w:ascii", "w:hAnsi", "w:cs"): rf.set(qn(a), "Arial")
    h.paragraph_format.space_before = Pt(6 if name != "Heading 1" else 0); h.paragraph_format.space_after = Pt(6)
    h.paragraph_format.keep_with_next = True
doc.styles["Heading 1"].paragraph_format.alignment = WD_ALIGN_PARAGRAPH.CENTER
for name in ("Heading 1", "Heading 2", "Heading 3"):
    rf = doc.styles[name].element.rPr.rFonts
    for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
        if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
sec = doc.sections[0]
sec.page_width, sec.page_height = Cm(21.0), Cm(29.7)
sec.left_margin, sec.right_margin, sec.top_margin, sec.bottom_margin = Cm(4), Cm(3), Cm(3), Cm(3)
sec.different_first_page_header_footer = True

def page_number_footer():
    p = sec.footer.paragraphs[0]; p.alignment = WD_ALIGN_PARAGRAPH.CENTER
    r = p.add_run(); r.font.size = Pt(10)
    for t, txt in (("begin", None), (None, "PAGE"), ("end", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
page_number_footer()

def runs(p, text, size=None, bold=False, italic=False):
    for part in re.split(r"(\[\[.*?\]\]|\*\*.*?\*\*|\*[^*]+?\*)", text):
        if not part: continue
        hl = part.startswith("[[")
        b = part.startswith("**"); it = part.startswith("*") and not b
        body = part[2:-2] if (hl or b) else (part[1:-1] if it else part)
        r = p.add_run(body); r.bold = bold or b; r.italic = italic or it
        if size: r.font.size = Pt(size)
        if hl: r.font.highlight_color = WD_COLOR_INDEX.YELLOW

def para(text, align="justify", size=None, bold=False, italic=False, indent=True, after=None):
    p = doc.add_paragraph()
    p.alignment = {"justify": WD_ALIGN_PARAGRAPH.JUSTIFY, "center": WD_ALIGN_PARAGRAPH.CENTER, "left": WD_ALIGN_PARAGRAPH.LEFT}[align]
    if indent and align == "justify": p.paragraph_format.first_line_indent = Cm(1)
    if after is not None: p.paragraph_format.space_after = Pt(after)
    runs(p, text, size, bold, italic); return p

def bullets(items, numbered=False):
    for i, t in enumerate(items):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.75); p.paragraph_format.first_line_indent = Cm(-0.6); p.paragraph_format.space_after = Pt(3)
        runs(p, (f"{i + 1}." if numbered else "•") + "\t" + t)
        p.paragraph_format.tab_stops.add_tab_stop(Cm(0.75))

def heading(text, level):
    h = doc.add_paragraph(style=f"Heading {level}"); runs(h, text, bold=True)
    for r in h.runs:
        r.font.name = "Arial"; r.font.size = Pt(12); r.font.color.rgb = RGBColor(0, 0, 0)
        rf = r._r.get_or_add_rPr().get_or_add_rFonts()
        for a in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"): rf.set(qn(a), "Arial")
        for a in ("w:asciiTheme", "w:hAnsiTheme", "w:cstheme", "w:eastAsiaTheme"):
            if rf.get(qn(a)) is not None: del rf.attrib[qn(a)]
    return h

def chapter(num, title):
    heading(f"CHAPTER {num}", 1).paragraph_format.page_break_before = True; heading(title, 2)

def figure(path, width_cm, caption):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.paragraph_format.space_after = Pt(2)
    p.paragraph_format.keep_with_next = True
    p.add_run().add_picture(os.path.join(P, path), width=Cm(width_cm))
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(c, caption, size=10)

def table(caption, header, rows, widths, size=9):
    c = doc.add_paragraph(); c.alignment = WD_ALIGN_PARAGRAPH.CENTER; c.paragraph_format.keep_with_next = True
    c.paragraph_format.space_after = Pt(2); runs(c, caption, size=10)
    t = doc.add_table(rows=1, cols=len(header)); t.style = "Table Grid"; t.alignment = WD_TABLE_ALIGNMENT.CENTER; t.autofit = False
    for i, h in enumerate(header):
        cell = t.rows[0].cells[i]; cell.paragraphs[0].paragraph_format.space_after = Pt(0); runs(cell.paragraphs[0], h, size, bold=True)
    for r in rows:
        cells = t.add_row().cells
        for i, v in enumerate(r):
            cells[i].paragraphs[0].paragraph_format.space_after = Pt(0); runs(cells[i].paragraphs[0], v, size)
    for row in t.rows:
        for i, w in enumerate(widths): row.cells[i].width = Cm(w)
    doc.add_paragraph().paragraph_format.space_after = Pt(0)

def equation(text):
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, text, italic=False)

# ------------------------------------------------------------------ cover --
def cover():
    for _ in range(2): para("", align="center")
    para(TITLE, align="center", bold=True, size=14, after=24)
    for _ in range(2): para("", align="center")
    logo = os.path.join(P, "logo_school.png")
    if os.path.exists(logo):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; p.add_run().add_picture(logo, width=Cm(4))
    else:
        para("[[INSTITUTION LOGO]]", align="center", bold=True, after=24)
    for _ in range(2): para("", align="center")
    para("COMPILED BY", align="center", bold=True, after=12)
    for a in AUTHORS: para(a.upper(), align="center", bold=True, after=2)
    for _ in range(4): para("", align="center")
    para(INSTITUTION, align="center", bold=True, after=2)
    para(YEAR, align="center", bold=True)

def toc():
    p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.CENTER; runs(p, "TABLE OF CONTENTS", bold=True)
    p.paragraph_format.page_break_before = True
    p = doc.add_paragraph(); r = p.add_run()
    for t, txt in (("begin", None), (None, 'TOC \\o "1-2" \\h \\z \\u'), ("separate", None)):
        if t:
            e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), t); r._r.append(e)
        else:
            e = OxmlElement("w:instrText"); e.set(qn("xml:space"), "preserve"); e.text = txt; r._r.append(e)
    r2 = p.add_run("Right-click and choose Update Field to refresh the table of contents.")
    e = OxmlElement("w:fldChar"); e.set(qn("w:fldCharType"), "end"); r2._r.append(e)

def abstract():
    heading("ABSTRACT", 1).paragraph_format.page_break_before = True
    para("Indoor spaces such as classrooms often lack plants and active air renewal, while conventional microalgae photobioreactors are "
         "bulky laboratory devices. This study designs ALGORA, a modular hexagonal photobioreactor lamp that cultivates the microalga "
         "*Chlorella vulgaris* to absorb carbon dioxide (CO2) and produce oxygen while also serving as a room lamp. The research follows "
         "a Research and Development (R&D) approach: literature study, a preliminary field study at a Spirulina cultivation site (Albitec), "
         "design, fabrication, testing, evaluation and finalization. One module is a flat-panel reactor 300 mm across flats and 40 mm thick, "
         "built from five CNC-cut acrylic layers (5 + 3 x 10 + 5 mm) that enclose a 30 mm culture chamber of 2.0 L, filled to about 1.7 L. "
         "Thirty-one addressable LEDs on the frame provide red-blue grow light by day and warm white room light in the evening. An ESP32 "
         "microcontroller reads water temperature, ambient light, culture optical density (OD) and CO2 concentration, schedules aeration and "
         "nutrient dosing, and publishes the data as JSON over Wi-Fi every 60 s. The design was verified with a dimensioned CAD drawing in "
         "LibreCAD, CNC path calculation and simulation. The cutting path is 8.24 m (about 37 min) for "
         "1.32 kg of acrylic. A 24-hour simulation of the control logic gives an average power of 5.2 W and "
         "126 Wh per day. A logistic growth model (growth rate 0.20-0.50 per day) predicts 0.46-0.98 g/L "
         "of biomass after 14 days, fixing 1.3-2.9 g of CO2, and a CO2 drop of "
         "190-460 ppm in a 60 L closed box within 2 hours, versus 10 ppm "
         "without algae. Physical tests are prepared to validate these values. "
         "calibration, a 14-day integrated run and a closed-box CO2 test against a control without algae. "
         "ALGORA shows that a compact, self-maintaining photobioreactor can be built with school-level tools and can serve as both an air-quality "
         "aid and a learning medium.", indent=False)
    para("**Keywords:** microalgae, *Chlorella vulgaris*, photobioreactor, Internet of Things, ESP32, carbon dioxide", indent=False, italic=False)

# -------------------------------------------------------------- chapters --
def ch1():
    chapter(1, "Introduction")
    heading("1.1 Background", 3)
    para("Carbon dioxide (CO2) is the main greenhouse gas produced by human activity, and its concentration is also a practical indicator of "
         "indoor air quality. In closed rooms with many occupants, such as classrooms, exhaled CO2 accumulates well above the outdoor level of "
         "about 420 ppm when ventilation is poor. Plants help, but most indoor plants grow slowly and need space and care that schools and "
         "small houses often cannot provide.")
    para("Microalgae are single-celled photosynthetic organisms that grow much faster than terrestrial plants and fix CO2 efficiently because "
         "every cell is in direct contact with the CO2-carrying medium [1], [2]. Producing 1 kg of dry algal biomass fixes about 1.83 kg of CO2 [1]. "
         "Microalgae are normally cultivated in open ponds or in closed photobioreactors that control light, temperature, mixing and gas "
         "supply [3], [4]. Closed photobioreactors give cleaner cultures and better control, but most designs are large, technical and placed "
         "in laboratories or factories, not in living spaces.")
    para("Low-cost microcontrollers and the Internet of Things (IoT) now make it possible to monitor and automate small cultivation systems "
         "[8]. Combining a thin, well-lit photobioreactor with LED lighting and IoT control could turn a culture of microalgae into an everyday "
         "object: a lamp that also cleans the air and can be maintained largely by itself.")
    para("Based on this idea, the team designed ALGORA, a modular hexagonal photobioreactor lamp. The hexagon shape lets several modules be "
         "joined like a honeycomb on a wall, while each module carries its own lighting, sensors and automatic care. This paper reports the "
         "design and the first prototype module.")
    heading("1.2 Research Problems", 3)
    bullets(["How is the ALGORA modular photobioreactor lamp designed and built?",
             "What is the expected performance of the ALGORA prototype in growing microalgae, reducing CO2 and using energy?"], numbered=True)
    heading("1.3 Research Objectives", 3)
    bullets(["To design and build one ALGORA module that cultivates *Chlorella vulgaris* with automatic lighting, aeration and nutrient dosing.",
             "To evaluate the expected performance of the prototype by calculation and simulation, including culture growth, CO2 reduction and energy use.",
             "To provide a learning medium about photosynthesis, microalgae and IoT for students."], numbered=True)
    heading("1.4 Benefits", 3)
    bullets(["**Students:** a hands-on medium for learning biology, physics and programming.",
             "**Schools:** an additional, decorative source of oxygen and a demonstration of green technology.",
             "**Community:** a compact way to help keep indoor air fresh in homes and offices.",
             "**Government:** an example of CO2 absorption that does not require additional land."])
    heading("1.5 Scope of the Study", 3)
    para("This study covers one prototype module (the main module with all sensors) cultivated with *Chlorella vulgaris* indoors. Connecting "
         "several modules, sharing water between modules and the cloud-based mobile application are outside the scope of this stage. Performance "
         "is evaluated by calculation and simulation; physical tests are the next validation step.")

def ch2():
    chapter(2, "Literature Review")
    heading("2.1 Microalgae and *Chlorella vulgaris*", 3)
    para("Microalgae are microscopic photosynthetic organisms that live in fresh or salt water. *Chlorella vulgaris* is a spherical green "
         "microalga, 2-10 um in diameter, that grows rapidly, tolerates a wide range of conditions and is widely used for food, feed and "
         "research [6]. Its robustness and easy availability make it suitable for a small reactor maintained by students. *Spirulina* "
         "(*Arthrospira platensis*), a filamentous cyanobacterium cultivated commercially in alkaline media, was studied as a comparison "
         "during the preliminary field study.")
    heading("2.2 Photosynthesis and CO2 Fixation", 3)
    para("In photosynthesis, light energy converts CO2 and water into glucose and oxygen [7]:")
    equation("6 CO2 + 6 H2O + light  →  C6H12O6 + 6 O2")
    para("Because microalgae grow in suspension, CO2 dissolved in the medium reaches every cell, giving higher CO2 fixation rates per unit "
         "area than land plants [2]. Bubbling air through the culture supplies CO2, keeps cells suspended and removes accumulated oxygen [3], [4].")
    heading("2.3 Photobioreactors", 3)
    para("A photobioreactor (PBR) is a closed, transparent vessel for growing phototrophic microorganisms under controlled conditions [3]. "
         "Common types are tubular, column and flat-panel reactors. Flat-panel reactors have a short light path, so light penetrates the whole "
         "culture, and they are easy to mix by aeration [4]. Light path, mixing, temperature and contamination control are the key design "
         "principles [4]. ALGORA uses a flat-panel geometry with a 30 mm light path.")
    heading("2.4 Light for Microalgae", 3)
    para("Chlorophyll absorbs mainly blue (about 430-450 nm) and red (about 640-680 nm) light [7]. Light-emitting diodes (LEDs) can deliver "
         "these wavelengths efficiently with little heat, and their intensity and photoperiod can be controlled electronically. A photoperiod "
         "with a dark phase is commonly used in microalgae cultivation.")
    heading("2.5 Optical Density as a Growth Indicator", 3)
    para("As algal cells multiply, the culture absorbs and scatters more light. Optical density (OD) expresses this attenuation as the "
         "logarithm of the ratio between incident and transmitted light, so OD increases with cell concentration and is widely used to follow "
         "culture growth.")
    heading("2.6 Internet of Things and Sensors", 3)
    para("The IoT connects physical devices to networks so that data can be monitored and devices controlled remotely. The ESP32 is a low-cost "
         "microcontroller with integrated Wi-Fi and Bluetooth [8]. Digital sensors used in this study include the DS18B20 waterproof "
         "temperature sensor with +/-0.5 °C accuracy, the BH1750 digital light sensor (lux) and the MH-Z19B non-dispersive infrared CO2 "
         "sensor [9]. WS2812B addressable LEDs allow the color and brightness of each LED to be set through a single data line [9].")
    heading("2.7 Research and Development Method", 3)
    para("Research and Development (R&D) is a research method used to produce and test a product [10], [11]. Its typical stages are "
         "information gathering, design, product development, testing, revision and final product, which are adapted in this study.")

def ch3():
    chapter(3, "Research Methods")
    heading("3.1 Research Design, Time and Place", 3)
    para("This study uses a six-stage R&D design: literature study, preliminary field study (observation and interview at Albitec on "
         "29 October 2026), design, fabrication, testing and evaluation, and finalization. The work was carried out at Mersif Academy, "
         "Sukoharjo, Central Java, in October-November 2026.")
    heading("3.2 Tools and Materials", 3)
    table("Table 1. Main tools and materials of one ALGORA module",
          ["Part", "Specification", "Qty"],
          [["Front sheet (A)", "Clear acrylic, 5 mm, hexagon 300 mm across flats", "1"],
           ["Frame rings (C)", "Clear acrylic, 10 mm, outer 300 mm, inner 278 mm, inner corners R4", "3"],
           ["Back sheet (B)", "Frosted acrylic, 5 mm, holes P1 Ø15.2 mm and P2-P4 Ø12.5 mm", "1"],
           ["Electronics", "ESP32 DevKit V1; DS18B20, 2 x BH1750, MH-Z19B; WS2812B strip (31 LEDs); 12 V air pump and peristaltic pump; 2 x MOSFET D4184; 12 V 3 A adapter, 3 A fuse, LM2596", "1 set"],
           ["Others and tools", "Aquarium silicone, PG7/PG9 glands, air stone, tubing, *C. vulgaris* starter, Walne medium; CNC router, multimeter, pH pen, thermometer", "1 set"]],
          [3.0, 9.6, 1.4])
    heading("3.3 Mechanical Design", 3)
    para("The module is a vertical flat-panel reactor with a flat side on top (Figure 1). Five acrylic layers are bonded with aquarium "
         "silicone: a clear front sheet, three 10 mm frame rings and a frosted back sheet, giving a 40 mm module with a 30 mm culture "
         "chamber. The parts were cut on a CNC router from 1:1 DXF files; the inner ring corners have a 4 mm radius because a round end mill "
         "cannot cut sharp internal corners. Back-sheet holes hold cable glands for filling and venting (P1), the air tube (P2), the "
         "temperature probe (P3) and draining (P4); P1-P3 lie 25 mm below the top edge, above the water line.")
    figure("fig_exploded.jpg", 6.3, "Figure 1. Exploded view: front sheet A, rings C1-C3 with the culture, and back sheet B")
    heading("3.4 Electronic and Control Design", 3)
    para("The 12 V adapter drives the pumps through MOSFET modules, and an LM2596 converter supplies 5 V to the ESP32, LEDs and CO2 sensor "
         "(Figure 2). Every 60 s the ESP32 reads all sensors and applies the schedule in Figure 3: red-blue grow light at 06:00-18:00 (dimmed "
         "above 2,000 lux of ambient light), warm white at 18:00-22:00, aeration 10 minutes every 30 minutes, nutrient dosing at 08:00, a "
         "warning outside 20-32 °C, and JSON data on the local Wi-Fi. Culture density is read by a second BH1750 facing a red LED "
         "across the chamber, where E0 is the illuminance through clear water and E through the culture:")
    equation("OD = log10 (E0 / E)")
    figure("fig_architecture_en.png", 12.5, "Figure 2. System architecture of the ALGORA prototype")
    figure("fig_flowchart_en.png", 5.2, "Figure 3. Control flowchart of the 60-second cycle")
    heading("3.5 Verification by CAD, Calculation and Simulation", 3)
    bullets(["**CAD:** all parts were drawn as dimensioned DXF files and plotted in LibreCAD; CNC path length and time were calculated from "
             "the geometry (feed 1,000 mm/min, 2 mm per pass, assumed).",
             "**Control simulation:** the firmware rules were run minute by minute for 24 h with a power model (ESP32 1.3 W, sensors 0.5 W, "
             "WS2812B 20 mA per channel at full scale with 50% brightness, converter 85%, air pump 3.6 W, indoor light below 2,000 lux).",
             "**Growth and CO2 model:** X(t) = Xmax / (1 + (Xmax/X0 - 1) e^(-\u03bct)) with X0 = 0.05 g/L, Xmax = 1.0 g/L and \u03bc = 0.20, "
             "0.35 and 0.50 per day (assumed range); fixed CO2 = 1.83 x biomass gain x 1.7 L [1]. Closed box: 60 L, 1,000 ppm, 25 \u00b0C, "
             "5 ppm/h leakage for both boxes, uptake at the fastest growth phase during the light period."])

def ch4():
    chapter(4, "Results and Discussion")
    heading("4.1 Detailed Design", 3)
    para("Figure 4 shows the detailed design drawn as a DXF file and plotted with LibreCAD. All dimensions match the CNC cutting files: "
         "300 mm across flats, 346.4 mm across corners, 40 mm thickness in five layers, an 11 mm ring wall and four gland holes. The 30 mm "
         "light path is typical of flat-panel reactors, so light reaches the whole culture [4]. The hydrostatic pressure at the bottom is "
         "only about 3 kPa, which aquarium silicone can hold if the bottom joint and the drain gland P4 are sealed carefully.")
    figure("fig_cad.png", 13.2, "Figure 4. Detailed design of one module plotted with LibreCAD (dimensions in mm)")
    heading("4.2 CNC Fabrication Calculation", 3)
    table("Table 2. Calculated CNC cutting data (feed 1,000 mm/min, 2 mm per pass)",
          ["Part", "Qty", "t (mm)", "Area (cm2)", "Cut (m)", "Passes", "Time (min)", "Mass (g)"],
          [["A front sheet", "1", "5", "779", "1.04", "3", "3.1", "464"],
           ["B back sheet", "1", "5", "774", "1.20", "3", "3.6", "460"],
           ["C frame ring", "3", "10", "110", "6.00", "5", "30.0", "393"],
           ["Total", "5", "-", "-", "8.24", "-", "36.7", "1318"]],
          [3.0, 1.0, 1.2, 1.8, 1.6, 1.5, 1.8, 1.6])
    para("Cutting the five parts needs 8.24 m of tool path and about 37 minutes of machine time, of which the "
         "three 10 mm rings take 30 minutes. Each ring leaves a 278 mm hexagonal offcut of 669 cm2, "
         "which can be reused, for example as a mounting plate. The acrylic body weighs 1.32 kg, or about 3.1 kg when filled.")
    heading("4.3 Control Logic Simulation", 3)
    figure("fig_sim_control.png", 12.4, "Figure 5. Simulated 24-hour LED and pump schedule and power at 12 V")
    para("The simulation confirms that the firmware produces 16 hours of light (12 h grow light and 4 h room light) and 8 hours of aeration "
         "per day (Figure 5). Power ranges from 2.1 W at night to 9.1 W when the room light and the air pump run "
         "together, with an average of 5.2 W. Daily energy is 126 Wh, about 3.8 kWh per month, "
         "so one module costs less to run than a typical 10 W LED bulb used for the same hours.")
    heading("4.4 Growth and CO2 Simulation", 3)
    figure("fig_sim_growth.png", 12.4, "Figure 6. Simulated (a) biomass growth and (b) CO2 in a 60 L closed box for three growth rates")
    para("With growth rates of 0.20, 0.35 and 0.50 per day, the culture reaches 0.46, 0.88 and "
         "0.98 g/L after 14 days and fixes 1.3, 2.6 and "
         "2.9 g of CO2 (Figure 6a). In the closed-box test, CO2 is predicted to fall by 190, "
         "325 and 460 ppm in 2 hours, compared with 10 ppm in the control "
         "(Figure 6b), so the effect of the algae is clearly measurable with the MH-Z19B sensor.")
    para("At room scale the effect of one module is small: its peak uptake of about 0.27 g CO2 per day is far "
         "below the roughly 1 kg exhaled daily by one person. ALGORA is therefore best seen as a modular demonstrator and lamp; a honeycomb "
         "wall of many modules, larger volumes or a higher growth rate would be needed for a noticeable change in a classroom. The model "
         "assumes no nutrient or light limitation, so its values are upper estimates that must be confirmed by the planned physical tests.")

def ch5():
    chapter(5, "Conclusion")
    bullets(["ALGORA was designed as a modular hexagonal flat-panel photobioreactor lamp 300 mm across flats and 40 mm thick, made of five "
             "CNC-cut acrylic layers that hold about 1.7 L of *Chlorella vulgaris*. An ESP32 with temperature, light, optical density and CO2 "
             "sensors controls 31 LEDs, aeration and nutrient dosing and shares data over Wi-Fi. The parts need 8.24 m of CNC path "
             "(about 37 min) and weigh 1.32 kg.",
             "Simulation shows that the control program provides 16 h of light and 8 h of aeration per day at an average power of "
             "5.2 W (126 Wh per day). The growth model predicts 0.46-0.98 g/L "
             "of biomass and 1.3-2.9 g of CO2 fixed in 14 days, and a CO2 drop of "
             "190-460 ppm in a 60 L closed box within 2 h."], numbered=True)
    para("ALGORA can be applied as an energy-efficient room lamp and as a learning medium for photosynthesis and IoT. Future work should "
         "validate the simulation with the planned physical tests, connect several modules into a honeycomb wall, add a pH sensor, "
         "calibrate the OD sensor and build the cloud-connected mobile application.")

def references():
    heading("REFERENCES", 1).paragraph_format.page_break_before = True
    refs = ["Y. Chisti, Biodiesel from microalgae, Biotechnology Advances, 25 (2007) 294-306.",
            "B. Wang, Y. Li, N. Wu and C.Q. Lan, CO2 bio-mitigation using microalgae, Applied Microbiology and Biotechnology, 79 (2008) 707-718.",
            "C.U. Ugwu, H. Aoyagi and H. Uchiyama, Photobioreactors for mass cultivation of algae, Bioresource Technology, 99 (2008) 4021-4028.",
            "C. Posten, Design principles of photo-bioreactors for cultivation of microalgae, Engineering in Life Sciences, 9 (2009) 165-177.",
            "A. Richmond and Q. Hu (Eds.), Handbook of Microalgal Culture: Applied Phycology and Biotechnology, 2nd ed., Wiley-Blackwell, 2013.",
            "C. Safi, B. Zebib, O. Merah, P.-Y. Pontalier and C. Vaca-Garcia, Morphology, composition, production, processing and applications of Chlorella vulgaris: A review, Renewable and Sustainable Energy Reviews, 35 (2014) 265-278.",
            "N.A. Campbell, J.B. Reece et al., Biology, 8th ed., Pearson Benjamin Cummings, 2008.",
            "Espressif Systems, ESP32 Series Datasheet, Espressif Systems, Shanghai.",
            "Maxim Integrated, DS18B20 Datasheet; ROHM, BH1750FVI Datasheet; Winsen, MH-Z19B Datasheet; Worldsemi, WS2812B Datasheet.",
            "Sugiyono, Metode Penelitian Kuantitatif, Kualitatif, dan R&D, Alfabeta, Bandung, 2013.",
            "M.D. Gall, J.P. Gall and W.R. Borg, Educational Research: An Introduction, 7th ed., Allyn and Bacon, Boston, 2003."]
    for i, r in enumerate(refs):
        p = doc.add_paragraph(); p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
        p.paragraph_format.left_indent = Cm(0.9); p.paragraph_format.first_line_indent = Cm(-0.9); p.paragraph_format.space_after = Pt(4)
        runs(p, f"[{i + 1}]\t{r}")

if __name__ == "__main__":
    cover(); toc(); abstract(); ch1(); ch2(); ch3(); ch4(); ch5(); references()
    doc.save(OUT); print("saved", OUT)
    if "--pdf" in sys.argv:
        import win32com.client
        w = win32com.client.DispatchEx("Word.Application"); w.Visible = False
        d = w.Documents.Open(OUT)
        d.TablesOfContents(1).Update(); d.Fields.Update()
        d.Save(); d.SaveAs2(OUT[:-5] + ".pdf", FileFormat=17); d.Close(False); w.Quit()
        print("pdf ok")
