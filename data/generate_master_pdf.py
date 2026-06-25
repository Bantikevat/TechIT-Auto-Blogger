"""
Generate PDF version of the master file for easy sharing
"""
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, PageBreak
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from html import escape

# Register Nirmala UI for Hindi
try:
    pdfmetrics.registerFont(TTFont('Nirmala', r"C:\Windows\Fonts\Nirmala.ttc", subfontIndex=0))
    pdfmetrics.registerFont(TTFont('NirmalaBold', r"C:\Windows\Fonts\Nirmala.ttc", subfontIndex=1))
    FONT = 'Nirmala'
    FONT_BOLD = 'NirmalaBold'
except:
    FONT = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

INPUT = r"C:\Claude\AI_\GURU_JI_MASTER_FILE.txt"
OUTPUT = r"C:\Claude\AI_\GURU_JI_MASTER_FILE.pdf"

doc = SimpleDocTemplate(
    OUTPUT, pagesize=A4,
    topMargin=1.5*cm, bottomMargin=1.5*cm,
    leftMargin=1.5*cm, rightMargin=1.5*cm,
    title="Guru Ji's Master Training File"
)

styles = getSampleStyleSheet()

heading = ParagraphStyle(
    'H', fontName=FONT_BOLD, fontSize=14,
    textColor=colors.HexColor('#0D47A1'),
    spaceBefore=12, spaceAfter=8
)

subheading = ParagraphStyle(
    'SH', fontName=FONT_BOLD, fontSize=11,
    textColor=colors.HexColor('#1565C0'),
    spaceBefore=6, spaceAfter=4
)

body = ParagraphStyle(
    'B', fontName=FONT, fontSize=9,
    leading=12, spaceBefore=2, spaceAfter=2
)

with open(INPUT, 'r', encoding='utf-8') as f:
    lines = f.readlines()

story = []
in_section = False

for line in lines:
    line = line.rstrip()
    if not line:
        story.append(Spacer(1, 4))
        continue

    safe = escape(line).replace('  ', '&nbsp;&nbsp;')

    # Detect headings
    if line.startswith('=' * 30) or line.startswith('═'):
        continue
    elif line.strip().startswith('TEACHER ') or 'POWER UPGRADE' in line:
        story.append(PageBreak())
        story.append(Paragraph(safe, heading))
    elif line.startswith('##') or line.startswith('━━'):
        continue
    elif line.startswith('──'):
        story.append(Spacer(1, 4))
    elif any(line.startswith(p) for p in ['WHO YOU ARE', 'STUDENT', 'PHILOSOPHY', 'COVERAGE', 'RULES', 'GOAL', 'FIRST MESSAGE', 'TEACHING']):
        story.append(Paragraph(f"<b>{safe}</b>", subheading))
    else:
        try:
            story.append(Paragraph(safe, body))
        except:
            story.append(Paragraph(escape(line), body))

print("Building PDF... this may take a moment")
doc.build(story)
import os
print(f"PDF created: {OUTPUT}")
print(f"Size: {os.path.getsize(OUTPUT)/1024:.1f} KB")
