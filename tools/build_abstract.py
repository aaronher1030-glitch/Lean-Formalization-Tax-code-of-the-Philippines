import copy
import json
import sys
from pathlib import Path

from docx import Document
from docx.oxml.ns import qn
from docx.shared import Pt

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "msp" / "MSPR3-2026_Abstract_Template.docx"
CONTENT = ROOT / "msp" / "abstract.json"
OUT = ROOT / "msp" / "HERNANDEZ-MSPR3-2026-Abstract.docx"


def drop(paragraph):
    paragraph._element.getparent().remove(paragraph._element)


def set_text(paragraph, text, italic=False):
    for run in paragraph.runs[1:]:
        run._element.getparent().remove(run._element)
    first = paragraph.runs[0]
    first.text = text
    first.italic = italic


def clear_runs(paragraph):
    for run in list(paragraph.runs):
        run._element.getparent().remove(run._element)


def add_superscript(paragraph, text, size=12):
    run = paragraph.add_run(text)
    run.font.name = "Times New Roman"
    run.font.size = Pt(size)
    run.font.superscript = True
    return run


def add_plain(paragraph, text, italic=False, font="Times New Roman", size=12):
    run = paragraph.add_run(text)
    run.font.name = font
    run.font.size = Pt(size)
    run.italic = italic
    return run


def main():
    data = json.loads(CONTENT.read_text(encoding="utf-8"))
    doc = Document(str(TEMPLATE))
    paras = doc.paragraphs

    drop(paras[0])

    set_text(paras[1], data["title"])
    for run in paras[1].runs:
        run.font.name = "Times New Roman"
        run.font.size = Pt(14)
        run.bold = True

    author = paras[2]
    set_text(author, data["author"])
    add_superscript(author, "1,*")
    for run in author.runs[:1]:
        run.font.name = "Times New Roman"
        run.font.size = Pt(12)

    affiliation = paras[3]
    clear_runs(affiliation)
    add_superscript(affiliation, "1")
    add_plain(affiliation, data["affiliation"], italic=True)

    drop(paras[4])

    email = data.get("email", "").strip()
    if email:
        line = paras[5]
        clear_runs(line)
        add_superscript(line, "1")
        add_plain(line, email, font="Courier New", size=12)
    else:
        drop(paras[5])

    presenter = paras[6]
    set_text(presenter, "* presenting author", italic=True)
    presenter.runs[0].font.name = "Times New Roman"
    presenter.runs[0].font.size = Pt(10)

    body = paras[7]
    set_text(body, data["body"])
    body.runs[0].font.name = "Times New Roman"
    body.runs[0].font.size = Pt(12)

    heading = paras[8]
    set_text(heading, "References")
    heading.runs[0].font.name = "Times New Roman"
    heading.runs[0].font.size = Pt(12)
    heading.runs[0].bold = True

    ref_paras = [paras[9], paras[10]]
    prototype = copy.deepcopy(ref_paras[0]._element)
    for ref in ref_paras:
        drop(ref)

    anchor = heading._element
    for index, (prefix, italic, suffix) in enumerate(data["references"], start=1):
        element = copy.deepcopy(prototype)
        anchor.addnext(element)
        anchor = element
        from docx.text.paragraph import Paragraph

        paragraph = Paragraph(element, heading._parent)
        for run in list(paragraph.runs):
            run._element.getparent().remove(run._element)
        add_plain(paragraph, f"[{index}] {prefix}")
        if italic:
            add_plain(paragraph, italic, italic=True)
        if suffix:
            add_plain(paragraph, suffix)

    props = doc.core_properties
    props.title = data["title"]
    props.author = data["author"]
    props.subject = "MSP Region 3 Convention 2026 abstract"
    props.keywords = "Lean 4; formalization; Philippine tax code; NIRC; certificate checker"

    doc.save(str(OUT))
    print("wrote", OUT)
    print("body words", len(data["body"].split()))


if __name__ == "__main__":
    main()
