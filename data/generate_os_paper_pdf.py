"""
Operating System 2026 Predicted Paper - PDF Generator (Hindi + English)
For B.Tech 4th Semester CSE/IT student
"""

from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm, mm
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_JUSTIFY
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, Spacer, PageBreak,
    Table, TableStyle, KeepTogether
)
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# Register Nirmala UI font (supports Devanagari)
NIRMALA_PATH = r"C:\Windows\Fonts\Nirmala.ttc"
try:
    pdfmetrics.registerFont(TTFont('Nirmala', NIRMALA_PATH, subfontIndex=0))
    pdfmetrics.registerFont(TTFont('NirmalaBold', NIRMALA_PATH, subfontIndex=1))
    HINDI_FONT = 'Nirmala'
    HINDI_BOLD = 'NirmalaBold'
    print("Loaded Nirmala UI (Devanagari)")
except Exception as e:
    print(f"Nirmala load failed: {e}")
    HINDI_FONT = 'Helvetica'
    HINDI_BOLD = 'Helvetica-Bold'

# Output path
OUTPUT = r"C:\Claude\AI_\OS_2026_Predicted_Paper.pdf"

# Document setup
doc = SimpleDocTemplate(
    OUTPUT,
    pagesize=A4,
    topMargin=2*cm,
    bottomMargin=2*cm,
    leftMargin=2*cm,
    rightMargin=2*cm,
    title="Operating System 2026 Predicted Paper",
    author="ByteFlow Tech - Master Teacher"
)

styles = getSampleStyleSheet()

# Custom styles
title_style = ParagraphStyle(
    'TitleCenter', parent=styles['Title'],
    fontName=HINDI_BOLD, fontSize=16, alignment=TA_CENTER,
    spaceAfter=4, textColor=colors.HexColor('#0D47A1')
)

subtitle_style = ParagraphStyle(
    'SubtitleCenter', parent=styles['Normal'],
    fontName=HINDI_BOLD, fontSize=12, alignment=TA_CENTER,
    spaceAfter=2, textColor=colors.HexColor('#1565C0')
)

header_info = ParagraphStyle(
    'HeaderInfo', parent=styles['Normal'],
    fontName=HINDI_BOLD, fontSize=11, alignment=TA_LEFT
)

note_style = ParagraphStyle(
    'Note', parent=styles['Normal'],
    fontName=HINDI_FONT, fontSize=10, leftIndent=0.5*cm,
    spaceAfter=4
)

question_main = ParagraphStyle(
    'QMain', parent=styles['Normal'],
    fontName=HINDI_BOLD, fontSize=12, spaceBefore=12, spaceAfter=4,
    textColor=colors.HexColor('#B71C1C')
)

question_sub = ParagraphStyle(
    'QSub', parent=styles['Normal'],
    fontName=HINDI_FONT, fontSize=10.5, leftIndent=0.8*cm,
    spaceBefore=4, spaceAfter=2, leading=14
)

mcq_option = ParagraphStyle(
    'MCQOpt', parent=styles['Normal'],
    fontName=HINDI_FONT, fontSize=10, leftIndent=1.5*cm,
    spaceBefore=1, spaceAfter=1, leading=13
)

short_note_item = ParagraphStyle(
    'ShortNote', parent=styles['Normal'],
    fontName=HINDI_FONT, fontSize=10.5, leftIndent=1.2*cm,
    spaceBefore=3, spaceAfter=3, leading=14
)

# ========= BUILD CONTENT =========
story = []

# Header
story.append(Paragraph("?/2026/7486", header_info))
story.append(Spacer(1, 4))
header_table = Table(
    [[Paragraph("Enrolment No. ........................", header_info),
      Paragraph("Total Pages : 4", header_info)]],
    colWidths=[10*cm, 7*cm]
)
story.append(header_table)
story.append(Spacer(1, 12))

# Title
story.append(Paragraph("Fourth Semester", title_style))
story.append(Paragraph("Computer Science &amp; Engineering / IT", subtitle_style))
story.append(Paragraph("Scheme OCBC, July 2022", subtitle_style))
story.append(Spacer(1, 4))
story.append(Paragraph("OPERATING SYSTEM", title_style))
story.append(Paragraph("(Predicted Paper - 2026)", subtitle_style))
story.append(Spacer(1, 12))

# Time and Marks
tm_table = Table(
    [[Paragraph("<b>Time : Three Hours</b>", header_info),
      Paragraph("<b>[Maximum Marks : 70]</b>", header_info)]],
    colWidths=[9*cm, 8*cm]
)
story.append(tm_table)
story.append(Spacer(1, 10))

# Note
story.append(Paragraph("<b>Note :</b>", header_info))
story.append(Paragraph(
    "(i) कुल आठ में से <b>छ:</b> प्रश्न हल कीजिए। प्रश्न क्रमांक <b>1</b> "
    "(वस्तुनिष्ठ प्रकार) अनिवार्य है। शेष सात प्रश्नों में से किन्हीं "
    "<b>पाँच</b> प्रश्नों (वर्णनात्मक) को हल कीजिए।", note_style))
story.append(Paragraph(
    "(ii) Attempt <b>six</b> questions out of <b>eight</b>. Question No. 1 "
    "(Objective type) is <b>compulsory</b>. Attempt any <b>five</b> "
    "(Descriptive type) from the remaining seven.", note_style))
story.append(Paragraph(
    "(iii) किसी भी प्रकार के संदेह की स्थिति में अंग्रेजी भाषा के "
    "प्रश्न को अन्तिम माना जायेगा।", note_style))
story.append(Spacer(1, 12))

# ================ QUESTION 1 - MCQ =================
story.append(Paragraph(
    "<b>1. सही उत्तर का चयन कीजिए।</b> &nbsp;&nbsp;&nbsp;&nbsp; "
    "<i>(Choose the correct answer.)</i> &nbsp;&nbsp; <b>[2 × 5 = 10]</b>",
    question_main))

# MCQ 1
story.append(Paragraph(
    "<b>(i)</b> ऑपरेटिंग सिस्टम का मुख्य कार्य क्या है? "
    "<i>(Main function of OS?)</i>", question_sub))
story.append(Paragraph("(a) Hardware को manage करना", mcq_option))
story.append(Paragraph("(b) Software run करना", mcq_option))
story.append(Paragraph("(c) User को interface देना", mcq_option))
story.append(Paragraph("<b>(d) उपरोक्त सभी (All of these)</b>", mcq_option))

# MCQ 2
story.append(Paragraph(
    "<b>(ii)</b> निम्न में से कौनसा CPU scheduling algorithm है? "
    "<i>(Which is a CPU scheduling algorithm?)</i>", question_sub))
story.append(Paragraph("(a) FIFO", mcq_option))
story.append(Paragraph("<b>(b) SJF (Shortest Job First)</b>", mcq_option))
story.append(Paragraph("(c) LRU", mcq_option))
story.append(Paragraph("(d) इनमें से कोई नहीं", mcq_option))

# MCQ 3
story.append(Paragraph(
    "<b>(iii)</b> Process Control Block (PCB) में क्या स्टोर होता है? "
    "<i>(What is stored in PCB?)</i>", question_sub))
story.append(Paragraph("(a) Process ID", mcq_option))
story.append(Paragraph("(b) Program Counter", mcq_option))
story.append(Paragraph("(c) Register values", mcq_option))
story.append(Paragraph("<b>(d) उपरोक्त सभी (All of these)</b>", mcq_option))

# MCQ 4
story.append(Paragraph(
    "<b>(iv)</b> Virtual memory का मुख्य उद्देश्य क्या है? "
    "<i>(Main purpose of virtual memory?)</i>", question_sub))
story.append(Paragraph("<b>(a) RAM को logically बढ़ाना</b>", mcq_option))
story.append(Paragraph("(b) Disk space बचाना", mcq_option))
story.append(Paragraph("(c) CPU speed बढ़ाना", mcq_option))
story.append(Paragraph("(d) इनमें से कोई नहीं", mcq_option))

# MCQ 5
story.append(Paragraph(
    "<b>(v)</b> Deadlock के लिए कितनी necessary conditions हैं? "
    "<i>(Number of necessary conditions for deadlock?)</i>", question_sub))
story.append(Paragraph("(a) 2", mcq_option))
story.append(Paragraph("(b) 3", mcq_option))
story.append(Paragraph(
    "<b>(c) 4</b> (Mutual Exclusion, Hold &amp; Wait, No Preemption, Circular Wait)",
    mcq_option))
story.append(Paragraph("(d) 5", mcq_option))

story.append(Spacer(1, 6))

# ================ QUESTION 2 =================
story.append(Paragraph("<b>2.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> Kernel क्या है? <i>(What is Kernel?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> Operating System की विभिन्न सेवाएँ (services) लिखिए। "
    "<i>(Write services provided by OS.)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> System call क्या है? इसके types को उदाहरण सहित समझाइये। "
    "<i>(What is System call? Explain its types with example.)</i> &nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 3 =================
story.append(Paragraph("<b>3.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> Process और Program में क्या अंतर है? "
    "<i>(Difference between Process and Program?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> Process state diagram को चित्र सहित समझाइये। "
    "<i>(Explain Process State Diagram with figure.)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> FCFS और SJF scheduling को उदाहरण (Gantt chart) सहित समझाइये। "
    "Average waiting time निकालिए। &nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 4 =================
story.append(Paragraph("<b>4.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> Thread क्या है? Process से कैसे अलग है? "
    "<i>(What is Thread? How different from Process?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> Multithreading के लाभ (benefits) और चुनौतियाँ (challenges) क्या हैं? "
    "<i>(Benefits and challenges of multithreading?)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> Thread Synchronization क्या है? Semaphore को उदाहरण सहित समझाइये। "
    "<i>(What is Thread Sync? Explain semaphore with example.)</i> &nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 5 =================
story.append(Paragraph("<b>5.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> Memory management की आवश्यकता क्यों है? "
    "<i>(Why memory management is required?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> Fragmentation क्या है? Internal और External fragmentation में अंतर बताइए। "
    "<i>(What is Fragmentation? Internal vs External.)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> Paging और Segmentation में अंतर लिखिए। दोनों को diagram सहित समझाइये। "
    "<i>(Paging vs Segmentation with diagrams.)</i> &nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 6 =================
story.append(Paragraph("<b>6.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> Virtual memory क्या है? इसके लाभ बताइए। "
    "<i>(What is Virtual Memory? Its benefits?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> Page fault क्या है? Operating system इसे कैसे handle करता है? "
    "<i>(What is page fault? How OS handles it?)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> LRU page replacement algorithm को उदाहरण सहित समझाइये। "
    "Reference string: <b>7, 0, 1, 2, 0, 3, 0, 4, 2, 3</b> के लिए कुल कितने "
    "page faults होंगे? (3 frames) &nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 7 =================
story.append(Paragraph("<b>7.</b>", question_main))
story.append(Paragraph(
    "<b>(a)</b> File और Directory में अंतर बताइए। "
    "<i>(Difference between File and Directory?)</i> &nbsp;&nbsp;<b>[2]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(b)</b> File management में होने वाले मुख्य operations कौन से हैं? "
    "<i>(Main file management operations?)</i> &nbsp;&nbsp;<b>[4]</b>",
    question_sub))
story.append(Paragraph(
    "<b>(c)</b> Disk scheduling के प्रकार बताइए। SSTF (Shortest Seek Time First) "
    "को उदाहरण सहित समझाइये। <i>(Disk scheduling types. Explain SSTF with example.)</i> "
    "&nbsp;&nbsp;<b>[6]</b>",
    question_sub))

# ================ QUESTION 8 =================
story.append(Paragraph(
    "<b>8.</b> निम्नलिखित पर संक्षिप्त टिप्पणी लिखिए <b>(कोई तीन)</b>: "
    "<i>(Write short notes on any THREE)</i> &nbsp;&nbsp;<b>[4 × 3 = 12]</b>",
    question_main))
story.append(Paragraph("<b>(i)</b> Deadlock (4 conditions + prevention)", short_note_item))
story.append(Paragraph("<b>(ii)</b> Authentication &amp; Access Control", short_note_item))
story.append(Paragraph("<b>(iii)</b> System Logs", short_note_item))
story.append(Paragraph("<b>(iv)</b> IPC (Inter-Process Communication)", short_note_item))
story.append(Paragraph("<b>(v)</b> Seek Time और Latency Time", short_note_item))

story.append(Spacer(1, 18))

# Footer separator
story.append(Paragraph(
    "<para alignment='center'><b>— END OF PAPER —</b></para>", note_style))

# ============= EXTRA SECTION PAGE =============
story.append(PageBreak())

extra_title = ParagraphStyle(
    'ExtraTitle', parent=styles['Title'],
    fontName=HINDI_BOLD, fontSize=15, alignment=TA_CENTER,
    spaceAfter=8, textColor=colors.HexColor('#1B5E20')
)
story.append(Paragraph("EXTRA PRACTICE QUESTIONS", extra_title))
story.append(Paragraph("(अतिरिक्त अभ्यास प्रश्न — Bonus)", subtitle_style))
story.append(Spacer(1, 12))

# Extra MCQs
story.append(Paragraph("<b>A. Extra MCQs (अतिरिक्त वस्तुनिष्ठ)</b>",
                       question_main))
extras_mcq = [
    "1. UNIX किस language में लिखा गया है? → <b>C</b>",
    "2. Multitasking और Multiprogramming में क्या अंतर है?",
    "3. Pre-emptive aur Non-preemptive scheduling में difference?",
    "4. Banker's Algorithm किस लिए use होता है? → <b>Deadlock avoidance</b>",
    "5. Cache memory कहाँ होती है? → <b>CPU के अंदर</b>",
    "6. RAID full form क्या है? → <b>Redundant Array of Independent Disks</b>",
    "7. Thrashing कब होती है?",
    "8. TLB का full form? → <b>Translation Lookaside Buffer</b>",
    "9. Round Robin scheduling में kya unique hai? → <b>Time Quantum</b>",
    "10. Spooling का full form? → <b>Simultaneous Peripheral Operation On-Line</b>",
]
for q in extras_mcq:
    story.append(Paragraph(q, short_note_item))

story.append(Spacer(1, 10))

# Extra Long Questions
story.append(Paragraph("<b>B. Extra Long Questions (बड़े प्रश्न)</b>",
                       question_main))
extras_long = [
    "1. Round Robin (RR) scheduling को time quantum के example सहित समझाइये।",
    "2. Producer-Consumer problem को semaphore के साथ समझाइये।",
    "3. Reader-Writer problem को समझाइये।",
    "4. Dining Philosophers problem की व्याख्या कीजिए।",
    "5. FIFO vs LRU vs Optimal page replacement की तुलना कीजिए।",
    "6. SCAN, C-SCAN, LOOK disk scheduling algorithms को समझाइये।",
    "7. UNIX file system structure (i-node) की व्याख्या कीजिए।",
    "8. Demand Paging को विस्तार से समझाइये।",
    "9. Thrashing क्या है? इसे कैसे handle किया जाता है?",
    "10. Banker's algorithm — deadlock avoidance example सहित।",
    "11. Context switching क्या है? इसका overhead क्यों होता है?",
    "12. Critical Section problem क्या है? तीन requirements बताइए।",
    "13. Belady's Anomaly क्या है?",
    "14. Compaction क्या है? कब करनी पड़ती है?",
    "15. Best Fit, First Fit, Worst Fit memory allocation में अंतर।",
]
for q in extras_long:
    story.append(Paragraph(q, short_note_item))

story.append(Spacer(1, 12))

# Tips Section
tips_title = ParagraphStyle(
    'TipsTitle', parent=styles['Title'],
    fontName=HINDI_BOLD, fontSize=14, alignment=TA_CENTER,
    spaceAfter=8, textColor=colors.HexColor('#E65100')
)
story.append(Paragraph("100/100 SCORE TIPS", tips_title))

tips = [
    "<b>1. Q1 MCQ:</b> सिर्फ 10 minute में निपटाएं।",
    "<b>2. हर 12-mark question:</b> 20-22 minute दें।",
    "<b>3. Diagram जरूर बनाएं</b> 5+ marks वाले प्रश्न में।",
    "<b>4. Bullet points और tables</b> use करें — paragraph से बेहतर।",
    "<b>5. Magic keywords:</b> Concurrent, Context switching, Race condition, Critical section, Mutual exclusion, Thrashing, Locality of reference, TLB.",
    "<b>6. Conclusion line</b> हर बड़े answer में लिखें।",
    "<b>7. Headings underline</b> करें — neat presentation।",
    "<b>8. Time management:</b> 3 hours = 180 min। 10 (MCQ) + 6×22 (long) = 142 min। 38 min revision।",
    "<b>9. Q8 short notes:</b> हर note 4-5 line + diagram।",
    "<b>10. Pencil से diagrams</b> बनाएं — गलती हो तो मिटा सकें।",
]
for t in tips:
    story.append(Paragraph(t, short_note_item))

story.append(Spacer(1, 20))
story.append(Paragraph(
    "<para alignment='center'><b>शुभकामनाएं! All the Best for 100/100 ✓</b></para>",
    title_style))

# Build PDF
doc.build(story)
print(f"\nPDF generated: {OUTPUT}")
print("Open in any PDF reader to view.")
