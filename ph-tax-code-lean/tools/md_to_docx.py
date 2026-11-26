# -*- coding: utf-8 -*-
"""Render the feasibility study Markdown as a styled DOCX."""

import os
import re
import sys

from docx import Document
from docx.enum.section import WD_SECTION
from docx.enum.table import WD_ALIGN_VERTICAL, WD_TABLE_ALIGNMENT
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_TAB_ALIGNMENT
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Inches, Pt, RGBColor
from docx.opc.constants import RELATIONSHIP_TYPE as RT

NAVY = RGBColor(0x1F, 0x38, 0x64)
BLUE = RGBColor(0x2E, 0x54, 0x96)
GRAY = RGBColor(0x55, 0x5F, 0x6D)
LIGHT = RGBColor(0x6C, 0x8E, 0xBF)
WHITE = RGBColor(0xFF, 0xFF, 0xFF)
BODY_FONT = "Calibri"
CODE_FONT = "Consolas"
CONTENT_WIDTH = 6.25  # inches, with 1-inch A4 margins
FOOTER_TEXT = os.environ.get(
    "DOCX_FOOTER", "How Strong Is a Verified Tax Code? — Research Paper"
)

TOKEN_RE = re.compile(r"(\*\*[^*]+\*\*|\*[^*]+\*|`[^`]+`|\[[^\]]+\]\([^)]+\))")


def shade(cell, fill):
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:shd")):
        tc_pr.remove(old)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:fill"), fill)
    tc_pr.append(shd)


def set_cell_margins(cell, top=60, left=80, bottom=60, right=80):
    tc_pr = cell._tc.get_or_add_tcPr()
    for old in tc_pr.findall(qn("w:tcMar")):
        tc_pr.remove(old)
    mar = OxmlElement("w:tcMar")
    for side, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{side}")
        el.set(qn("w:w"), str(val))
        el.set(qn("w:type"), "dxa")
        mar.append(el)
    tc_pr.append(mar)


def set_table_borders(table, color="BFC9D9", sz=4):
    tbl_pr = table._tbl.tblPr
    for old in tbl_pr.findall(qn("w:tblBorders")):
        tbl_pr.remove(old)
    borders = OxmlElement("w:tblBorders")
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single")
        el.set(qn("w:sz"), str(sz))
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)
    tbl_pr.append(borders)


def set_cell_border(cell, edge, color, sz=8, val="single"):
    tc_pr = cell._tc.get_or_add_tcPr()
    borders = tc_pr.first_child_found_in("w:tcBorders")
    if borders is None:
        borders = OxmlElement("w:tcBorders")
        tc_pr.append(borders)
    tag = f"w:{edge}"
    el = borders.find(qn(tag))
    if el is None:
        el = OxmlElement(tag)
        borders.append(el)
    el.set(qn("w:val"), val)
    el.set(qn("w:sz"), str(sz))
    el.set(qn("w:space"), "0")
    el.set(qn("w:color"), color)


def add_hyperlink(paragraph, url, text):
    part = paragraph.part
    r_id = part.relate_to(url, RT.HYPERLINK, is_external=True)
    hyperlink = OxmlElement("w:hyperlink")
    hyperlink.set(qn("r:id"), r_id)
    new_run = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    color = OxmlElement("w:color")
    color.set(qn("w:val"), "1F4E79")
    r_pr.append(color)
    underline = OxmlElement("w:u")
    underline.set(qn("w:val"), "single")
    r_pr.append(underline)
    new_run.append(r_pr)
    t = OxmlElement("w:t")
    t.set(qn("xml:space"), "preserve")
    t.text = text
    new_run.append(t)
    hyperlink.append(new_run)
    paragraph._p.append(hyperlink)


def add_runs(paragraph, text, size=None, color=None, bold_all=False, italic_all=False):
    for token in TOKEN_RE.split(text):
        if not token:
            continue
        if token.startswith("**") and token.endswith("**") and len(token) > 4:
            run = paragraph.add_run(token[2:-2])
            run.bold = True
        elif token.startswith("*") and token.endswith("*") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            run.italic = True
        elif token.startswith("`") and token.endswith("`") and len(token) > 2:
            run = paragraph.add_run(token[1:-1])
            run.font.name = CODE_FONT
            run._element.rPr.rFonts.set(qn("w:eastAsia"), CODE_FONT)
            run.font.size = Pt(9.2)
        elif token.startswith("[") and "](" in token and token.endswith(")"):
            label, url = token[1:-1].split("](", 1)
            add_hyperlink(paragraph, url, label)
            continue
        else:
            run = paragraph.add_run(token)
        if bold_all:
            run.bold = True
        if italic_all:
            run.italic = True
        if size is not None:
            run.font.size = Pt(size)
        if color is not None:
            run.font.color.rgb = color
    return paragraph


def widths_for(headers):
    h = [x.lower().strip() for x in headers]
    n = len(h)
    if n == 2:
        return [0.28, 0.72]
    if n == 3:
        if h[0] == "" and "discretion" in h[1]:
            return [0.16, 0.42, 0.42]
        if "sections" in h[1] and "sample" in h[2]:
            return [0.58, 0.21, 0.21]
        if "count" in h[1]:
            return [0.34, 0.12, 0.54]
        if h[0].startswith("day"):
            return [0.14, 0.48, 0.38]
        if "risk" in h[0]:
            return [0.30, 0.18, 0.52]
        return [0.22, 0.18, 0.60]
    if n == 4:
        if h[0] == "date":
            return [0.14, 0.42, 0.26, 0.18]
        if "words" in h[2]:
            return [0.16, 0.54, 0.10, 0.20]
        if "dimension" in h[0]:
            return [0.22, 0.10, 0.46, 0.22]
        if "code" in h[0]:
            return [0.08, 0.18, 0.44, 0.30]
        if "direction" in h[0]:
            return [0.22, 0.26, 0.12, 0.40]
        if "subject" in h[1] and "sections" in h[2]:
            return [0.12, 0.48, 0.18, 0.22]
        return [0.25, 0.25, 0.25, 0.25]
    return [1.0 / n] * n


def add_table(doc, rows, ratios=None):
    if not rows:
        return
    ncols = len(rows[0])
    rows = [r + [""] * (ncols - len(r)) for r in rows]
    table = doc.add_table(rows=len(rows), cols=ncols)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    set_table_borders(table)

    if ratios is None or len(ratios) != ncols:
        ratios = widths_for(rows[0])
    else:
        total_r = sum(ratios)
        ratios = [r / total_r for r in ratios]
    total = CONTENT_WIDTH
    widths = [Inches(total * r) for r in ratios]

    tbl_pr = table._tbl.tblPr
    layout = OxmlElement("w:tblLayout")
    layout.set(qn("w:type"), "fixed")
    tbl_pr.append(layout)
    for c_idx, width in enumerate(widths):
        table.columns[c_idx].width = width

    for r_idx, row in enumerate(rows):
        tr_pr = table.rows[r_idx]._tr.get_or_add_trPr()
        cant = OxmlElement("w:cantSplit")
        tr_pr.append(cant)
        if r_idx == 0:
            header = OxmlElement("w:tblHeader")
            tr_pr.append(header)
        for c_idx, text in enumerate(row):
            cell = table.cell(r_idx, c_idx)
            cell.width = widths[c_idx]
            cell.vertical_alignment = (
                WD_ALIGN_VERTICAL.CENTER if r_idx == 0 else WD_ALIGN_VERTICAL.TOP
            )
            set_cell_margins(cell)
            p = cell.paragraphs[0]
            p.paragraph_format.space_after = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.line_spacing = 1.0
            if r_idx == 0:
                shade(cell, "1F3864")
                add_runs(p, text, size=8.6, color=WHITE, bold_all=True)
            else:
                if r_idx % 2 == 0:
                    shade(cell, "F4F6FA")
                if "total" in row[0].lower():
                    shade(cell, "E8EEF8")
                add_runs(p, text, size=8.6)

    # Keep the table from touching the next paragraph.
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(4)
    spacer.paragraph_format.line_spacing = 1.0
    for run in spacer.runs:
        run.font.size = Pt(2)


def add_callout(doc, text):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    cell.width = Inches(CONTENT_WIDTH)
    set_cell_margins(cell, top=100, left=140, bottom=100, right=120)
    shade(cell, "EAF1FB")
    set_cell_border(cell, "left", "1F3864", sz=22)
    set_cell_border(cell, "top", "BFC9D9", sz=4)
    set_cell_border(cell, "bottom", "BFC9D9", sz=4)
    set_cell_border(cell, "right", "BFC9D9", sz=4)
    p = cell.paragraphs[0]
    p.paragraph_format.space_after = Pt(0)
    p.paragraph_format.line_spacing = 1.1
    add_runs(p, text, size=10.2)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(2)


def add_code_block(doc, lines):
    table = doc.add_table(rows=1, cols=1)
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    table.style = "Table Grid"
    cell = table.cell(0, 0)
    cell.width = Inches(CONTENT_WIDTH)
    set_cell_margins(cell, top=100, left=120, bottom=100, right=120)
    shade(cell, "F5F7FA")
    for edge in ("top", "left", "bottom", "right"):
        set_cell_border(cell, edge, "D5DCE8", sz=4)
    first = True
    for line in lines:
        p = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        p.paragraph_format.space_before = Pt(0)
        p.paragraph_format.space_after = Pt(0)
        p.paragraph_format.line_spacing = 1.0
        run = p.add_run(line if line else " ")
        run.font.name = CODE_FONT
        run._element.rPr.rFonts.set(qn("w:eastAsia"), CODE_FONT)
        run.font.size = Pt(8.2)
        run.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    spacer = doc.add_paragraph()
    spacer.paragraph_format.space_before = Pt(0)
    spacer.paragraph_format.space_after = Pt(2)


def add_rule(doc):
    p = doc.add_paragraph()
    p.paragraph_format.space_before = Pt(10)
    p.paragraph_format.space_after = Pt(0)
    p_pr = p._p.get_or_add_pPr()
    borders = OxmlElement("w:pBdr")
    bottom = OxmlElement("w:bottom")
    bottom.set(qn("w:val"), "single")
    bottom.set(qn("w:sz"), "8")
    bottom.set(qn("w:space"), "1")
    bottom.set(qn("w:color"), "1F3864")
    borders.append(bottom)
    p_pr.append(borders)


def page_number_footer(section):
    footer = section.footer
    p = footer.paragraphs[0]
    p.text = ""
    p.paragraph_format.tab_stops.add_tab_stop(
        Inches(CONTENT_WIDTH), WD_TAB_ALIGNMENT.RIGHT
    )
    run = p.add_run(FOOTER_TEXT)
    run.font.size = Pt(8)
    run.font.color.rgb = GRAY
    p.add_run("\t")
    run = p.add_run("Page ")
    run.font.size = Pt(8)
    run.font.color.rgb = GRAY
    fld = OxmlElement("w:fldSimple")
    fld.set(qn("w:instr"), "PAGE")
    r = OxmlElement("w:r")
    r_pr = OxmlElement("w:rPr")
    sz = OxmlElement("w:sz")
    sz.set(qn("w:val"), "16")
    r_pr.append(sz)
    r.append(r_pr)
    t = OxmlElement("w:t")
    t.text = "1"
    r.append(t)
    fld.append(r)
    p._p.append(fld)


def main(md_path, out_path):
    with open(md_path, encoding="utf-8") as f:
        lines = f.read().splitlines()

    doc = Document()
    section = doc.sections[0]
    section.page_width = Inches(8.27)
    section.page_height = Inches(11.69)
    section.top_margin = Inches(1)
    section.bottom_margin = Inches(1)
    section.left_margin = Inches(1)
    section.right_margin = Inches(1)

    styles = doc.styles
    normal = styles["Normal"]
    normal.font.name = BODY_FONT
    normal.font.size = Pt(10.5)
    normal.font.color.rgb = RGBColor(0x1A, 0x1A, 0x1A)
    normal.paragraph_format.line_spacing = 1.12
    normal.paragraph_format.space_after = Pt(6)
    normal._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)

    for name, size, color, before, after in (
        ("Heading 1", 15, NAVY, 14, 6),
        ("Heading 2", 12.5, BLUE, 11, 4),
        ("Heading 3", 11, RGBColor(0x33, 0x33, 0x33), 8, 3),
    ):
        st = styles[name]
        st.font.name = BODY_FONT
        st.font.size = Pt(size)
        st.font.bold = True
        st.font.color.rgb = color
        st.paragraph_format.space_before = Pt(before)
        st.paragraph_format.space_after = Pt(after)
        st.paragraph_format.keep_with_next = True
        st._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)

    styles["List Bullet"].font.name = BODY_FONT
    styles["List Bullet"].font.size = Pt(10.5)
    styles["List Bullet"].paragraph_format.space_after = Pt(2)

    core = doc.core_properties
    core.title = os.environ.get(
        "DOCX_TITLE",
        "How Strong Is a Verified Tax Code? A Critical Study of Formalizing "
        "Philippine Tax Rules in Lean 4, with a Proven Certificate Checker",
    )
    core.author = "Aaron Y. Hernandez"
    core.subject = os.environ.get(
        "DOCX_SUBJECT", "Lean formalization, Philippine tax code, governance automation"
    )
    core.comments = os.environ.get("DOCX_COMMENTS", "Prepared 18 November 2026")

    page_number_footer(section)

    title_page = True
    title_done = False
    subtitle_done = False
    pending_widths = None
    i = 0
    n = len(lines)

    while i < n:
        raw = lines[i]
        line = raw.rstrip()
        s = line.strip()

        if not s:
            i += 1
            continue

        m = re.match(r"^<!--\s*widths:\s*([\d.,\s]+)-->$", s)
        if m:
            pending_widths = [float(x) for x in m.group(1).split(",") if x.strip()]
            i += 1
            continue

        if s == "<!-- pagebreak -->":
            if title_page:
                add_rule(doc)
            doc.add_page_break()
            title_page = False
            i += 1
            continue

        if s.startswith("```"):
            code = []
            i += 1
            while i < n and not lines[i].strip().startswith("```"):
                code.append(lines[i])
                i += 1
            i += 1
            add_code_block(doc, code)
            continue

        if s.startswith("|"):
            rows = []
            while i < n and lines[i].strip().startswith("|"):
                cells = [c.strip() for c in lines[i].strip().strip("|").split("|")]
                if not all(re.match(r"^:?-{3,}:?$", c) for c in cells):
                    rows.append(cells)
                i += 1
            if rows:
                add_table(doc, rows, pending_widths)
            pending_widths = None
            continue

        if s.startswith("> "):
            quote = []
            while i < n and lines[i].strip().startswith("> "):
                quote.append(lines[i].strip()[2:].strip())
                i += 1
            add_callout(doc, " ".join(quote))
            continue

        m = re.match(r"^(#{1,6})\s+(.*)$", s)
        if m:
            level = len(m.group(1))
            text = m.group(2).strip()
            if title_page:
                if level == 1 and not title_done:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(80)
                    p.paragraph_format.space_after = Pt(6)
                    run = p.add_run(text)
                    run.font.name = BODY_FONT
                    run.font.size = Pt(26)
                    run.font.bold = True
                    run.font.color.rgb = NAVY
                    run._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
                    title_done = True
                elif level == 2 and not subtitle_done:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    p.paragraph_format.space_before = Pt(0)
                    p.paragraph_format.space_after = Pt(28)
                    run = p.add_run(text)
                    run.font.name = BODY_FONT
                    run.font.size = Pt(14)
                    run.font.color.rgb = GRAY
                    run._element.rPr.rFonts.set(qn("w:eastAsia"), BODY_FONT)
                    subtitle_done = True
                else:
                    p = doc.add_paragraph()
                    p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    add_runs(p, text, size=10.5, color=GRAY)
                i += 1
                continue
            style = {1: "Heading 1", 2: "Heading 2"}.get(level, "Heading 3")
            p = doc.add_paragraph(style=style)
            add_runs(p, text)
            i += 1
            continue

        m = re.match(r"^!\[(.*?)\]\((.*?)\)$", s)
        if m:
            alt, path = m.group(1), m.group(2)
            img_path = path if os.path.isabs(path) else os.path.join(os.path.dirname(md_path), path)
            if os.path.exists(img_path):
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                p.paragraph_format.space_before = Pt(4)
                p.paragraph_format.space_after = Pt(2)
                p.add_run().add_picture(img_path, width=Inches(6.0))
            else:
                p = doc.add_paragraph()
                p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                add_runs(p, f"[Missing image: {alt}]", size=9, color=GRAY)
            i += 1
            continue

        if re.match(r"^[-*]\s+", s):
            while i < n and re.match(r"^[-*]\s+", lines[i].strip()):
                text = re.sub(r"^[-*]\s+", "", lines[i].strip())
                p = doc.add_paragraph(style="List Bullet")
                add_runs(p, text)
                i += 1
            continue

        if re.match(r"^\d+\.\s+", s):
            text = s
            p = doc.add_paragraph()
            p.paragraph_format.left_indent = Inches(0.28)
            p.paragraph_format.first_line_indent = Inches(-0.28)
            p.paragraph_format.space_after = Pt(3)
            add_runs(p, text)
            i += 1
            continue

        # Plain paragraph: gather until a blank line or a new block.
        buf = [s]
        start = i
        i += 1
        while i < n:
            nxt = lines[i].strip()
            if (
                not nxt
                or nxt.startswith("#")
                or nxt.startswith("|")
                or nxt.startswith("> ")
                or nxt.startswith("```")
                or nxt.startswith("![")
                or nxt == "<!-- pagebreak -->"
                or re.match(r"^[-*]\s+", nxt)
                or re.match(r"^\d+\.\s+", nxt)
            ):
                break
            buf.append(nxt)
            i += 1
        text = " ".join(buf)
        p = doc.add_paragraph()
        if title_page:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(2)
            if text.startswith("*") and not text.startswith("**"):
                p.paragraph_format.space_after = Pt(14)
        if text.startswith("*Figure"):
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.space_after = Pt(8)
            add_runs(p, text, size=8.6, color=GRAY)
        else:
            prev = lines[start - 2].strip() if start >= 2 else ""
            follows_list = bool(re.match(r"^([-*]|\d+\.)\s+", prev))
            if text.startswith("**") and follows_list and not title_page:
                p.paragraph_format.space_before = Pt(8)
            add_runs(p, text)

    doc.save(out_path)
    print(f"Wrote {out_path}")


if __name__ == "__main__":
    md = sys.argv[1] if len(sys.argv) > 1 else "paper/Verified_Core_Tax_Governance_PH.md"
    out = sys.argv[2] if len(sys.argv) > 2 else "paper/Verified_Core_Tax_Governance_PH.docx"
    main(md, out)
