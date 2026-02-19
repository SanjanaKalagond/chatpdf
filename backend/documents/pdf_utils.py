from io import BytesIO
import re
from reportlab.platypus import (
    SimpleDocTemplate,
    Paragraph,
    Spacer,
    Table,
    TableStyle,
)
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
from reportlab.lib.units import inch
from reportlab.lib.pagesizes import A4


def clean_markdown(text):
    text = text.replace("\r\n", "\n")
    return text


def parse_markdown_table(lines):
    table_data = []

    for line in lines:
        line = line.strip()

        if not line or line.startswith("|:") or line.startswith("| :"):
            continue

        if "|" in line:
            cells = [c.strip() for c in line.strip("|").split("|")]
            table_data.append(cells)

    return table_data


def generate_pdf(title: str, content: str):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4)
    elements = []

    styles = getSampleStyleSheet()
    heading1 = styles["Heading1"]
    heading2 = styles["Heading2"]
    normal = styles["Normal"]

    content = clean_markdown(content)
    lines = content.split("\n")

    i = 0
    while i < len(lines):
        line = lines[i].strip()

        if not line:
            elements.append(Spacer(1, 0.2 * inch))
            i += 1
            continue

        # Detect markdown table
        if "|" in line and i + 1 < len(lines) and "---" in lines[i + 1]:
            table_lines = []
            while i < len(lines) and "|" in lines[i]:
                table_lines.append(lines[i])
                i += 1

            table_data = parse_markdown_table(table_lines)

            if table_data:
                table = Table(table_data, repeatRows=1)
                table.setStyle(
                    TableStyle(
                        [
                            ("BACKGROUND", (0, 0), (-1, 0), colors.lightgrey),
                            ("GRID", (0, 0), (-1, -1), 0.5, colors.grey),
                            ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
                            ("FONTSIZE", (0, 0), (-1, -1), 9),
                            ("VALIGN", (0, 0), (-1, -1), "TOP"),
                        ]
                    )
                )
                elements.append(table)
                elements.append(Spacer(1, 0.3 * inch))

            continue

        # Headings
        if line.startswith("###"):
            elements.append(Paragraph(line.replace("###", "").strip(), heading2))
        elif line.startswith("##"):
            elements.append(Paragraph(line.replace("##", "").strip(), heading1))
        elif line.startswith("#"):
            elements.append(Paragraph(line.replace("#", "").strip(), heading1))
        elif line.startswith("*"):
            bullet = line.replace("*", "").strip()
            elements.append(Paragraph("• " + bullet, normal))
        else:
            elements.append(Paragraph(line, normal))

        elements.append(Spacer(1, 0.15 * inch))
        i += 1

    doc.build(elements)
    buffer.seek(0)
    return buffer
