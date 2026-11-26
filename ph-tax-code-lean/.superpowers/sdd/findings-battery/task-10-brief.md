# Task brief (generated from the plan)

Read the plan section below as your requirements. Also binding: the Global
Constraints section of the plan, reproduced here:

- Lean 4.35.0 pinned toolchain, core library only.
- No `native_decide`, no `sorry`; axiom audit must stay at `propext`.
- Do NOT stage, commit, or push anything (standing user rule).
- Python runs as `python -X utf8`; writes use encoding="utf-8".
- Generated `lean/_harness/Findings.lean` stays gitignored.
- `LEAN` env override honored; default ROOT/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe.
- 59/82 hand-written counts must not change.
- Windows: run from repo root `C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean`.
- Toolchain export for compiles: LEAN="C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/tools/lean/dist/lean-4.35.0-windows/bin/lean.exe".

Frozen row schema for any task using rows:

    {"id": "F001", "family": "...", "kind": "equivalence|divergence|boundary|incentive|identity|gap",
     "theorem": "f001_<family>_001", "prop": "...", "tactic": "rfl"|"decide",
     "witness": "...", "value": int|None, "source": "...", "note": "..."}

---
### Task 10: Re-render DOCX and PDF, inspect the new pages

**Files:**
- Modify: `Verified_Core_Tax_Governance_PH.docx`, `Verified_Core_Tax_Governance_PH.pdf`
- Create: `previews/findings-page-*.png` (workspace scratch, gitignored)

**Interfaces:**
- Consumes: Task 7's edited Markdown.
- Produces: a 23+-page PDF containing §5.11 and the renumbered tables, visually inspected.

- [ ] **Step 1: Render the DOCX from the workspace tool**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && DOCX_FOOTER="How Strong Is a Verified Tax Code? — Research Paper" python -X utf8 tools/md_to_docx.py ph-tax-code-lean/Verified_Core_Tax_Governance_PH.md ph-tax-code-lean/Verified_Core_Tax_Governance_PH.docx`
Expected: `Wrote ...Verified_Core_Tax_Governance_PH.docx`.

- [ ] **Step 2: Export the PDF through Word**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && python -X utf8 - <<'PY'
from pathlib import Path
import win32com.client as win32
root = Path(r"C:\Users\Ma Christine\Downloads\LEAN FORMALIZATION OF TAX CODE\ph-tax-code-lean")
docx = root / "Verified_Core_Tax_Governance_PH.docx"
pdf = root / "Verified_Core_Tax_Governance_PH.pdf"
app = win32.DispatchEx("Word.Application")
app.Visible = False
try:
    doc = app.Documents.Open(str(docx))
    doc.SaveAs(str(pdf), FileFormat=17)
    doc.Close(False)
finally:
    try:
        app.Quit()
    except Exception:
        pass
print("wrote", pdf, pdf.stat().st_size)
PY
```

Expected: `wrote ...pdf <size>`. A `com_error` on Quit is harmless if the PDF exists.

- [ ] **Step 3: Locate and screenshot the new pages**

Run:

```bash
cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE" && mkdir -p previews && python -X utf8 - <<'PY'
import fitz
pdf = "ph-tax-code-lean/Verified_Core_Tax_Governance_PH.pdf"
doc = fitz.open(pdf)
print("pages", len(doc))
hits = [i + 1 for i in range(len(doc))
        if "5.11" in doc[i].get_text() or "findings battery" in doc[i].get_text().lower()]
print("hits", hits)
for p in hits:
    pix = doc[p - 1].get_pixmap(dpi=80)
    out = f"previews/findings-page-{p:02d}.png"
    pix.save(out)
    print("saved", out)
PY
```

Expected: page count 24 or more; at least one hit; PNG paths printed.

- [ ] **Step 4: Inspect the screenshots**

Read each `previews/findings-page-*.png` with the Read tool. Check: §5.11 heading present, Table 9 renders as a table with eight rows and a total, the roadmap table shows rows 1–9 with no duplicated numbers, no overflow or clipped columns. If anything is clipped, adjust the Markdown table widths (the paper uses a width comment line above tables) and repeat Steps 1–4.

- [ ] **Step 5: Verify and leave uncommitted**

Run: `cd "C:/Users/Ma Christine/Downloads/LEAN FORMALIZATION OF TAX CODE/ph-tax-code-lean" && git status --short Verified_Core_Tax_Governance_PH.docx Verified_Core_Tax_Governance_PH.pdf`
Expected: both modified; not staged. Do not commit.

---

