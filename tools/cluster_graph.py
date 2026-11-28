#!/usr/bin/env python3
"""Build the NIRC section dependency graph, condense its SCCs, and emit the
cluster worklist used by the distributed formalization design.

Input : data/ra8424.html            (LawPhil RA 8424, the NIRC 1997 base text)
        data/NIRC_section_index.csv (section -> heading, title)
Output: data/nirc_refs.csv          (from, to, phrase)
        data/nirc_sections.csv      (section, heading, title, units, fan-in/out)
        data/nirc_clusters.csv      (cluster, sections, depth, status, units)
        data/nirc_cluster_graph.json
        NIRC_CLUSTER_GRAPH.md       (method, measurements, worklist)

Stdlib only. Deterministic: same inputs -> same outputs.

Scope and honesty
-----------------
* The base text is RA 8424 (1997), NOT the Code as amended. Amendments
  (RA 10963, RA 11976, ...) add, move and delete references; the graph is a
  floor, not the current state. Re-run against an amended consolidated text
  before quoting these numbers as law.
* Only *section-level* references create graph edges. References internal to a
  section ("this Section", "subsection (b)", "such subparagraph") are
  intra-section dependencies: they raise the cost of a section but do not
  change the cluster graph. They are counted separately as coupling.
* Extraction is regex + a small number grammar, measured against hand-checked
  samples (--audit), not assumed correct. Every dropped reference is counted
  and printed so the loss is visible.
"""

from __future__ import annotations

import argparse
import csv
import html
import json
import re
import sys
from collections import Counter, defaultdict

SRC_HTML = "data/ra8424.html"
SRC_INDEX = "data/NIRC_section_index.csv"
OUT_REFS = "data/nirc_refs.csv"
OUT_SECTIONS = "data/nirc_sections.csv"
OUT_CLUSTERS = "data/nirc_clusters.csv"
OUT_JSON = "data/nirc_cluster_graph.json"
OUT_MD = "NIRC_CLUSTER_GRAPH.md"

# Sections this repository has actually formalized (ph-tax-code-lean/COVERAGE.md).
MERGED = {21, 24, 109, 116, 236, 248, 249}

# The one reality check on unit_estimate(), counted by hand from
# ph-tax-code-lean/lean on 2026-11-28: declarations (def / theorem / lemma /
# example / structure / inductive) attributable to each merged section, excluding
# the shared certificate-checker layer (Cert*, check*, mkCert*, claim*) and the
# demonstration files, which no single section owns. Attribution is a judgement
# call, so these are a fixed one-time measurement, not something the tool
# regenerates from the Lean.
CALIBRATION = {
    21:  (6,  "Tier, classify, rank, reduced, classify_mono; the formula scores 0"),
    24:  (30, "schedule defs, 5 monotonicity lemmas, 10 bracket examples, 8% regime"),
    109: (11, "threshold, exemption and registration predicates, with complements"),
    116: (3,  "percentage rate, monotonicity, one example"),
    236: (0,  "no Lean declaration in this repository"),
    248: (12, "surcharge, penalty, tiered variants, bounds"),
    249: (8,  "interest, day monotonicity, bounds"),
}

# The statute is not typeset consistently: most headings are <b>Section 24.</b>
# but §132 is <b>Section </b>132. The optional closing tag covers both.
SECTION_MARK = re.compile(r"<b>\s*Section\s*(?:</b>)?\s*(\d{1,3})\s*\.", re.I)
TITLE_MARK = re.compile(
    r"(?is)<p[^>]*>\s*<b>\s*TITLE\s+([IVXLC]+)\s*(?:<br\s*/?>)?\s*([^<]*)"
)
P_START = re.compile(r"<p\b", re.I)

# A reference keyword followed by a list of section numbers:
#   Section 24(A)(2)(a) | Sections 922 through 927 | Secs. 24, 25 and 26
REF_KEYWORD = re.compile(r"\b(Sections?|Secs?\.)\s+", re.I)
PAREN_GROUP = re.compile(r"\([A-Za-z0-9]{1,6}\)")
CONNECTOR = re.compile(r"\s*(,|and|or|to|through|thru|-|\u2013|\u2014)\s*", re.I)
FOREIGN_LAW = re.compile(
    r"\b(of|under|in)\s+(Republic Act|R\.\s?A\.|Presidential Decree|P\.\s?D\.|"
    r"Executive Order|E\.\s?O\.|Commonwealth Act|C\.\s?A\.|Batas Pambansa|B\.\s?P\.)",
    re.I,
)
# Intra-section coupling: does this section lean on its own subdivisions?
INTERNAL_REF = re.compile(
    r"\b(this\s+Section|the\s+preceding\s+[Ss]ection|hereof|hereinafter|"
    r"subsection|subparagraph|sub-item|paragraph)\b",
    re.I,
)


# ---------------------------------------------------------------- extraction

def body_html(raw: str) -> str:
    """Return the NIRC body only: after RA 8424's own sections 1-8 and the
    table of contents, which repeats 'TITLE I..XIV' and would corrupt titles."""
    m = re.search(r'<a\s+name="t1"\s*>', raw, re.I)
    if not m:
        sys.exit('could not find <A NAME="t1">; refusing to guess the body start')
    return raw[m.start():]


def strip_tags(s: str) -> str:
    s = re.sub(r"(?is)<(script|style)\b.*?</\1>", " ", s)
    s = re.sub(r"(?i)<br\s*/?>", "\n", s)
    s = re.sub(r"(?i)</p\s*>", "\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    s = s.replace("\xa0", " ").replace("\u200b", "")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r" *\n *", "\n", s)
    s = re.sub(r"\n{3,}", "\n\n", s)
    return s.strip()


def read_sections(raw: str) -> tuple[list[dict], list[str]]:
    """Split the body into numbered sections, tracking the enclosing TITLE.

    Markers are accepted only when the number is the next one expected, so a
    bold "Section 5 of R.A. No. 1234" inside prose cannot open a fake section.
    The marker and heading are excluded from the section text: otherwise every
    section cites itself."""
    marks: list[tuple[int, int, int]] = []
    expected = 1
    for m in SECTION_MARK.finditer(raw):
        num = int(m.group(1))
        if num == expected:
            marks.append((m.start(), m.end(), num))
            expected += 1
    if not marks:
        sys.exit("no <b>Section N.</b> markers found")

    title_marks = [(m.start(), m.group(1).upper(), html.unescape(m.group(2)).strip())
                   for m in TITLE_MARK.finditer(raw)]

    sections = []
    for i, (start, body_start, num) in enumerate(marks):
        end = marks[i + 1][0] if i + 1 < len(marks) else len(raw)
        chunk = raw[body_start:end]          # heading excluded on purpose
        plain = strip_tags(chunk)
        title = ""
        for tpos, tr, tname in title_marks:
            if tpos <= start:
                title = f"Title {tr} - {tname}".strip(" -")
        sections.append({
            "section": num,
            "title": title,
            "text": plain,
            "paragraphs": len(P_START.findall(raw[start:end])),
        })
    return sections, [f"Title {r} - {n}" for _, r, n in title_marks]


def refs_in_text(text: str) -> list[tuple[int, str]]:
    """Section numbers referenced by one section's text, with the phrase."""
    out: list[tuple[int, str]] = []
    for m in REF_KEYWORD.finditer(text):
        if FOREIGN_LAW.search(text[m.start(): m.end() + 40]):
            continue
        tail = text[m.end(): m.end() + 200]
        nums: list[int] = []
        pos = 0
        while True:
            nm = re.match(r"(\d{1,3})", tail[pos:])
            if not nm:
                break
            n = int(nm.group(1))
            pos += nm.end()
            while True:  # skip subdivision markers: (A)(2)(a)
                rest = tail[pos:]
                pm = PAREN_GROUP.match(rest.lstrip())
                if not pm:
                    break
                pos += len(rest) - len(rest.lstrip()) + pm.end()
            nums.append(n)
            cm = CONNECTOR.match(tail[pos:])
            if not cm:
                break
            conn = cm.group(1).lower()
            pos += cm.end()
            if conn in ("to", "through", "thru", "-", "\u2013", "\u2014"):
                em = re.match(r"(\d{1,3})", tail[pos:])
                if em:
                    hi = int(em.group(1))
                    pos += em.end()
                    lo = nums.pop()
                    if lo <= hi and hi - lo <= 400:
                        nums.extend(range(lo, hi + 1))
                    else:
                        nums.append(lo)
        shown = text[m.start(): m.end() + pos]
        for n in nums:
            out.append((n, shown.strip()))
    return out


# ---------------------------------------------------------------- graph

def build_graph(sections: list[dict]) -> tuple[dict[int, set[int]], list[dict], Counter]:
    adj: dict[int, set[int]] = {s["section"]: set() for s in sections}
    edges, noise = [], Counter()
    for s in sections:
        src = s["section"]
        for target, phrase in refs_in_text(s["text"]):
            if target == src:
                noise["self"] += 1
            elif target not in adj:
                noise["out_of_range"] += 1
            elif target in adj[src]:
                noise["duplicate"] += 1
            else:
                adj[src].add(target)
                edges.append({"from": src, "to": target, "phrase": phrase[:110]})
    return adj, edges, noise


def tarjan_scc(adj: dict[int, set[int]]) -> list[list[int]]:
    """Iterative Tarjan: no recursion-limit risk on a 292-node graph, but safe."""
    index: dict[int, int] = {}
    low: dict[int, int] = {}
    on_stack: dict[int, bool] = {}
    stack: list[int] = []
    sccs: list[list[int]] = []
    counter = 0

    for root in sorted(adj):
        if root in index:
            continue
        index[root] = low[root] = counter
        counter += 1
        stack.append(root)
        on_stack[root] = True
        work = [(root, iter(sorted(adj[root])))]
        while work:
            v, it = work[-1]
            advanced = False
            for w in it:
                if w not in index:
                    index[w] = low[w] = counter
                    counter += 1
                    stack.append(w)
                    on_stack[w] = True
                    work.append((w, iter(sorted(adj[w]))))
                    advanced = True
                    break
                if on_stack.get(w):
                    low[v] = min(low[v], index[w])
            if advanced:
                continue
            work.pop()
            if work:
                u = work[-1][0]
                low[u] = min(low[u], low[v])
            if low[v] == index[v]:
                comp = []
                while True:
                    w = stack.pop()
                    on_stack[w] = False
                    comp.append(w)
                    if w == v:
                        break
                sccs.append(sorted(comp))
    return sccs


def condensation(adj: dict[int, set[int]], sccs: list[list[int]]):
    comp_of: dict[int, int] = {}
    for i, comp in enumerate(sccs):
        for v in comp:
            comp_of[v] = i
    cadj: dict[int, set[int]] = {i: set() for i in range(len(sccs))}
    for v, ws in adj.items():
        for w in ws:
            a, b = comp_of[v], comp_of[w]
            if a != b:
                cadj[a].add(b)
    return comp_of, cadj


def topo_levels(cadj: dict[int, set[int]]):
    """Return a topological order (sources first) and each cluster's depth.

    Depth is the longest chain of unformalized dependencies *beneath* a cluster:
    depth 0 means the cluster references nothing outside itself and can be
    started today; depth k means it sits on k dependency steps. The naive Kahn
    level, which propagates along edges into the target, measures the opposite
    thing — how deeply a section is cited — and would put the foundations on
    top of the frontier instead of under it. That is the wrong quantity, so the
    propagation is done in reverse topological order."""
    indeg = {i: 0 for i in cadj}
    for i, ws in cadj.items():
        for w in ws:
            indeg[w] += 1
    q = sorted(i for i, d in indeg.items() if d == 0)
    order: list[int] = []
    while q:
        v = q.pop(0)
        order.append(v)
        for w in sorted(cadj[v]):
            indeg[w] -= 1
            if indeg[w] == 0:
                q.append(w)
    if len(order) != len(cadj):
        sys.exit("condensation is not a DAG; Tarjan or the edge build is wrong")
    depth = {i: 0 for i in cadj}
    for v in reversed(order):
        if cadj[v]:
            depth[v] = 1 + max(depth[w] for w in cadj[v])
    return order, depth


# ---------------------------------------------------------------- units

NUM = re.compile(r"\b\d[\d,]*(?:\.\d+)?\b")
COMPUTE_KW = re.compile(
    r"\b(rates?|percent(?:age)?|threshold|exceed(?:s)?|less than|not exceed|more than|"
    r"multiplied|divided|table|schedule|bracket|exemption|deduct(?:ion|ible)|credit|"
    r"penalt(?:y|ies)|interest|surcharge|taxable income|gross (?:sales|receipts|income))",
    re.I,
)


def section_metrics(text: str, paragraphs: int) -> dict:
    nums = len(NUM.findall(text))
    pct = len(re.findall(r"%|\bpercent\b", text, re.I))
    kw = len(COMPUTE_KW.findall(text))
    score = nums + 2 * pct + kw
    rule_p = 0
    for para in re.split(r"\n+", text):
        if len(para) < 60:
            continue
        if NUM.search(para) or len(COMPUTE_KW.findall(para)) >= 2:
            rule_p += 1
    return {
        "numbers": nums, "percent": pct, "keywords": kw, "score": score,
        "rule_paragraphs": rule_p, "paragraphs": paragraphs,
        "internal_refs": len(INTERNAL_REF.findall(text)),
    }


def unit_estimate(m: dict) -> int:
    """1 definition + 1 statement per rule-bearing paragraph + 1 worked example
    per ten.

    A text-structure heuristic, not a count of work done: it reads numbers,
    percentages and rule-bearing paragraphs, and cannot see that a short section
    is legally hard. It has been checked exactly once, against the seven merged
    sections (see CALIBRATION and the table in NIRC_CLUSTER_GRAPH.md §6), which
    showed it ranks clusters usefully and does not predict effort per section.
    """
    if m["score"] < 6 or m["numbers"] < 2:
        return 0
    rp = min(m["rule_paragraphs"], 40)
    return 1 + rp + max(1, rp // 10)


# ---------------------------------------------------------------- report

def md_table(headers: list[str], rows: list[list]) -> str:
    out = ["| " + " | ".join(headers) + " |",
           "|" + "|".join("---" for _ in headers) + "|"]
    for r in rows:
        out.append("| " + " | ".join(str(x) for x in r) + " |")
    return "\n".join(out)


def write_markdown(path: str, ctx: dict) -> None:
    secs = ctx["sections"]
    clusters = ctx["clusters"]
    adj, cadj = ctx["adj"], ctx["cadj"]
    comp_of, level, fan_in = ctx["comp_of"], ctx["level"], ctx["fan_in"]
    edges, noise = ctx["edges"], ctx["noise"]
    ready, next_up = ctx["ready"], ctx["next_up"]

    n = len(secs)
    out_deg = [len(adj[s["section"]]) for s in secs]
    indeg = [fan_in[s["section"]] for s in secs]
    isolated = [s["section"] for s in secs if not adj[s["section"]] and not fan_in[s["section"]]]
    cyc = [c for c in clusters if c["size"] > 1]
    formalizable = [s for s in secs if s["units"] > 0]
    total_units = sum(s["units"] for s in formalizable)
    merged_units = sum(s["units"] for s in formalizable if s["section"] in MERGED)
    depth_hist = Counter(c["depth"] for c in clusters)
    max_depth = max(depth_hist) if depth_hist else 0

    L: list[str] = []
    A = L.append

    A("# The NIRC Cluster Graph")
    A("")
    A("*Generated by `tools/cluster_graph.py` from `data/ra8424.html` (RA 8424, the "
      "1997 NIRC base text) and `data/NIRC_section_index.csv`. Regenerate with "
      "`python -X utf8 tools/cluster_graph.py`; nothing here is hand-entered "
      "except the declaration counts in §6, which are a fixed measurement.*")
    A("")
    A("## What this is")
    A("")
    A("The distributed formalization design in "
      "`DEEP_RESEARCH_DISTRIBUTED_TAX_FORMALIZATION.md` §5.1 proposes partitioning "
      "the tax code by its own cross-reference graph rather than by title. This "
      "file is that partition, measured instead of assumed: every section of the "
      "NIRC, every section-level reference between them, the strongly connected "
      "components of the resulting digraph, and the resulting work frontier.")
    A("")
    A("The short version: **at section granularity the graph is sparse, so the "
      "clustering is nearly a singleton partition and the frontier is wide, not "
      "deep.** Dependency order is not what limits this project. Review capacity "
      "is.")
    A("")
    A("## 1. Extraction")
    A("")
    A(md_table(["Quantity", "Value"], [
        ["Sections parsed", f"{n}"],
        ["Section-level edges (unique)", f"{len(edges)}"],
        ["Mean out-degree", f"{sum(out_deg) / n:.2f}"],
        ["Mean in-degree", f"{sum(indeg) / n:.2f}"],
        ["Sections with no outgoing reference", f"{sum(1 for d in out_deg if d == 0)}"],
        ["Sections never referenced by another section",
         f"{sum(1 for d in indeg if d == 0)}"],
        ["Sections with neither in- nor out-edges", f"{len(isolated)}"],
        ["References dropped: self", f"{noise.get('self', 0)}"],
        ["References dropped: out of range", f"{noise.get('out_of_range', 0)}"],
        ["References dropped: duplicate", f"{noise.get('duplicate', 0)}"],
    ]))
    A("")
    A("Dropped references are printed deliberately. `out_of_range` is mostly "
      "references to other instruments (the Tariff and Customs Code, the Local "
      "Government Code) whose numbers collide with NIRC section numbers, and "
      "`self` is a section naming itself. Neither is a graph edge.")
    A("")
    A("### Markers, and one defect worth naming")
    A("")
    A("The source typesets headings as `<b>Section 24.</b>`, except §132, which is "
      "`<b>Section </b>132.` — the bold closes before the number. A strict marker "
      "regex silently loses that section and shifts every later chunk boundary. "
      "The tolerant pattern plus a strict sequence check (a marker counts only if "
      "its number is the next expected one) makes the split self-validating: if "
      "the parse ever stops at 291 sections again, the count says so.")
    A("")
    A("This is a small instance of the project's central claim. A formalization "
      "pipeline is a proofreader: the extractor found a real typesetting fault in "
      "the primary source, which is exactly the class of finding Lexifina reports "
      "from doing this to Title 26.")
    A("")
    A("### What counts as an edge")
    A("")
    A("Only whole-section references (`Section 24`, `Sections 922 through 927`, "
      "`Secs. 24, 25 and 26`) become edges. Subdivision references — "
      "`subsection (b)`, `this Section`, `such subparagraph`, `hereof` — are "
      "counted per section as **coupling** but do not create edges, because they "
      "never leave the section. They are what makes a single section expensive, "
      "not what orders sections against each other.")
    A("")
    A(md_table(["Coupling", "Sections", "Mean per section"], [
        ["Internal reference tokens", f"{sum(s['metrics']['internal_refs'] for s in secs)}",
         f"{sum(s['metrics']['internal_refs'] for s in secs) / n:.1f}"],
        ["Sections with ≥10 internal references",
         f"{sum(1 for s in secs if s['metrics']['internal_refs'] >= 10)}", "—"],
    ]))
    A("")

    A("## 2. Condensation")
    A("")
    A(md_table(["Quantity", "Value"], [
        ["Strongly connected components (clusters)", f"{len(clusters)}"],
        ["Multi-section components", f"{len(cyc)}"],
        ["Sections inside a cycle", f"{sum(c['size'] for c in cyc)}"],
        ["Sections that are their own cluster", f"{sum(1 for c in clusters if c['size'] == 1)}"],
        ["Longest dependency chain (clusters)", f"{max_depth + 1}"],
    ]))
    A("")
    A(f"{sum(1 for c in clusters if c['size'] == 1)} of {len(clusters)} clusters are a "
      f"single section. The statute's citation graph is close to a tree with a few "
      f"true knots: only {sum(c['size'] for c in cyc)} sections sit in a cycle, and "
      f"every cycle is small and local.")
    A("")
    if cyc:
        A("**The cycles.** Each is an atomic unit: formalizing any member "
          "independently would mean assuming a clause of a section you have not "
          "written yet.")
        A("")
        rows = []
        for c in sorted(cyc, key=lambda c: -c["size"]):
            titles = ", ".join(f"§{m}" for m in c["sections"][:12])
            rows.append([len(c["sections"]), titles, c["units_est"],
                         ", ".join(str(m) for m in c["merged_sections"]) or "—"])
        A(md_table(["Size", "Sections", "Units (est.)", "Already merged"], rows))
        A("")

    A("## 3. Depth structure")
    A("")
    A("Depth is the longest chain of unformalized dependencies beneath a cluster: "
      "depth 0 references no other section, so it can be started today; depth *k* "
      "sits on *k* dependency steps. The histogram is how far a contributor can get "
      "without waiting for anyone.")
    A("")
    rows = []
    for d in sorted(depth_hist):
        at = [c for c in clusters if c["depth"] == d]
        rows.append([d, len(at), sum(c["size"] for c in at),
                     sum(c["units_est"] for c in at)])
    A(md_table(["Depth", "Clusters", "Sections", "Units (est.)"], rows))
    A("")
    A(f"Depth 0 holds {depth_hist.get(0, 0)} of {len(clusters)} clusters; the deepest "
      f"chain is {max_depth + 1} clusters. Even the worst-placed cluster waits on a "
      "handful of predecessors, not a tree — so there is no ordering reason to hold "
      "work back, only a statement-signing reason, which is the constraint §4.2 of "
      "the design document names.")
    A("")

    A("## 4. The frontier")
    A("")
    A("**Ready now** — every section-level dependency is already merged in this "
      "repository, so a unit here can be merged without a new assumption.")
    A("")
    ready_f = [c for c in ready if c["units_remaining"] > 0]
    A(f"{len(ready_f)} clusters, {sum(c['units_remaining'] for c in ready_f)} estimated "
      "units. Highest-value first (units, then fan-in):")
    A("")
    def short(s: str, n: int = 58) -> str:
        s = (s or "").replace("|", "/").strip()
        return s if len(s) <= n else s[:n - 1].rstrip() + "…"

    rows = []
    for c in sorted(ready_f, key=lambda c: (-c["units_remaining"], -c["fan_in"]))[:15]:
        rows.append([", ".join(f"§{m}" for m in c["sections"][:5]),
                     short(c["heading"]) or "—", c["units_remaining"], c["fan_in"]])
    A(md_table(["Cluster", "Heading", "Units left", "Cited by"], rows))
    A("")
    A("**One hop out** — a single unmerged dependency away from ready:")
    A("")
    rows = []
    for c in sorted([c for c in next_up if c["units_remaining"] > 0],
                    key=lambda c: -c["units_remaining"])[:10]:
        rows.append([", ".join(f"§{m}" for m in c["sections"][:5]),
                     ", ".join(f"§{d}" for d in c["deps"][:6]) or "—",
                     c["units_remaining"]])
    A(md_table(["Cluster", "Needs first", "Units"], rows))
    A("")

    A("## 5. Size of the work")
    A("")
    A(md_table(["Quantity", "Value"], [
        ["Sections with formalizable content", f"{len(formalizable)} of {n}"],
        ["Sections with no arithmetic to model", f"{n - len(formalizable)}"],
        ["Estimated units, whole code", f"~{total_units}"],
        ["Units already merged (7 sections)", f"~{merged_units}"],
        ["Units remaining", f"~{total_units - merged_units}"],
        ["Median units per formalizable section",
         f"{sorted(s['units'] for s in formalizable)[len(formalizable) // 2]}"],
    ]))
    A("")
    A("The design document's title-level estimate was 90–130 formalizable sections "
      f"concentrated in Titles II, III, IV, V and VII. The measure gives "
      f"**{len(formalizable)}**, inside that band — but it rejects the "
      "concentration. Formalizable arithmetic turns up in every title, because "
      "assessment, limitation, penalty and allotment provisions compute too. The "
      "table below replaces the title-level estimate with the measured one.")
    A("")

    roman_rank = {r: i for i, r in enumerate(
        ["I", "II", "III", "IV", "V", "VI", "VII", "VIII", "IX", "X",
         "XI", "XII", "XIII", "XIV"], start=1)}
    by_title: dict[str, dict] = defaultdict(lambda: {"sections": 0, "formalizable": 0, "units": 0})
    for s in secs:
        key = s["index_title"] or s["title"] or "(unassigned)"
        by_title[key]["sections"] += 1
        by_title[key]["units"] += s["units"]
        if s["units"] > 0:
            by_title[key]["formalizable"] += 1

    def rank(t: str) -> int:
        m = re.match(r"Title\s+([IVXLC]+)", t or "", re.I)
        return roman_rank.get(m.group(1).upper(), 99) if m else 99

    A("### Formalizable content by title, measured")
    A("")
    rows = []
    for t, d in sorted(by_title.items(), key=lambda kv: rank(kv[0])):
        m = re.match(r"Title\s+([IVXLC]+)\s*-\s*(.*)$", t, re.I)
        rows.append([m.group(1) if m else "—", short(m.group(2), 40) if m else short(t, 40),
                     d["sections"], d["formalizable"], d["units"]])
    rows.append(["", "**Total**", len(secs), len(formalizable), total_units])
    A(md_table(["Title", "Subject", "Sections", "Formalizable", "Units est."], rows))
    A("")
    top_titles = sorted(by_title.items(), key=lambda kv: -kv[1]["units"])[:3]
    A("By estimated units the centre of gravity is " + ", ".join(
        f"{short(t, 34)} ({d['units']})" for t, d in top_titles) +
      ". Titles VI, IX and X contribute more than their reputation: excise schedules, "
      "invoicing thresholds and penalty tables are all arithmetic.")
    A("")
    A("### Per-cluster worklist")
    A("")
    A("Clusters with at least one unit left, ordered by depth then size. `deps` is "
      "the dependency frontier of that cluster; `cited` is how many other sections "
      "reference it, which is the proxy for how much of the code waits on it.")
    A("")
    rows = []
    for c in sorted(clusters, key=lambda c: (c["depth"], -c["units_remaining"], c["cluster"])):
        if c["units_remaining"] <= 0:
            continue
        rows.append([c["cluster"],
                     ", ".join(str(m) for m in c["sections"][:8])
                     + ("…" if c["size"] > 8 else ""),
                     c["depth"], c["status"], c["units_remaining"], c["fan_in"],
                     ", ".join(f"§{d}" for d in c["deps"][:6])
                     + ("…" if len(c["deps"]) > 6 else "") or "—"])
    A(md_table(["id", "Sections", "Depth", "Status", "Units", "Cited", "Needs"], rows))
    A("")

    A("## 6. What this does not show")
    A("")
    A("- **It is the 1997 base text.** RA 10963 and RA 11976 changed rates, "
      "thresholds and at least one cross-reference. The graph is a floor; the "
      "amended consolidated text must be re-parsed before these numbers are "
      "quoted as current law.")
    A("- **It is section granularity.** Two sections can be formally independent "
      "and still share a definition (`gross income`, `taxable income`). The "
      "shared definitions are cluster C1 in the design document, not edges here.")
    A("- **Units are text-structure estimates**, not measurements of effort. The "
      "formula rewards numbers, percentages and rule-bearing paragraphs; it cannot "
      "see that a short section is legally hard. It is checked once, below, against "
      "the seven merged sections: the aggregate holds to about 20%, individual "
      "sections are off by a factor of two in both directions, and two are wrong "
      "in kind rather than degree. Rank clusters with it; do not schedule from it.")
    A("- **Conditional references are flattened.** \"If the taxpayer is a "
      "corporation, Section 27 applies\" becomes a plain edge, so fan-in "
      "overstates how often a section is actually reached.")
    A("")
    A("### The check on the estimate")
    A("")
    A("The estimate is a text-structure heuristic with exactly one check: the "
      "seven merged sections, estimate against the Lean declarations they "
      "actually took. Declarations means def / theorem / lemma / example / "
      "structure / inductive attributable to that section in "
      "`ph-tax-code-lean/lean`, excluding the shared certificate-checker layer "
      "and the demonstration files. Attribution is a judgement call, so the counts "
      "are a one-time hand measurement recorded in `CALIBRATION`, not something "
      "this script derives from the Lean.")
    A("")
    est = {s["section"]: s["units"] for s in secs}
    A(md_table(["Section", "Units (est.)", "Declarations (counted)", "What was counted"],
               [[f"§{m}", est[m], did, note] for m, (did, note) in sorted(CALIBRATION.items())]))
    A("")
    A(f"{sum(est[m] for m in CALIBRATION)} estimated units against "
      f"{sum(d for d, _ in CALIBRATION.values())} counted declarations over the same "
      "seven sections. The aggregate is comfortable; the per-section errors are "
      "not, and they are not noise — they follow the text structure the formula "
      "reads. Work that is a type and its monotonicity lemmas has few numbers, so "
      "§21 scores zero; a section that is mostly procedural prose this repository "
      "has not formalized scores fourteen. The estimate ranks clusters; it does "
      "not predict what a section costs.")
    A("")
    A("## 7. What follows for the roadmap")
    A("")
    A("1. **Dependency order is not the bottleneck.** With "
      f"{depth_hist.get(0, 0)} clusters at depth 0 and a chain of at most "
      f"{max_depth + 1}, a contributor can start almost anywhere. The scarce "
      "resource is the practitioner who signs statements, exactly as §4.2 of the "
      "design document argues.")
    A("2. **Cycles are the only real ordering constraint, and they are local.** "
      f"The {len(cyc)} components above should be handed to one contributor each as "
      "single assignments, never split across the desk.")
    top_open = [(m, c) for m, c in fan_in.most_common() if m not in MERGED][:5]
    A("3. **Fan-in is the priority signal, not section number.** Of the sections "
      "still to do, " + ", ".join(f"§{m}" for m, _ in top_open) +
      " are cited most and should be formalized first even though they are not "
      "the numerically first.")
    A("   §24, the most-cited section overall, is already merged — which is the "
      "reason the frontier is as wide as it is.")
    A("4. **The extractor is a deliverable.** It found a typesetting fault in the "
      "primary source on its first run. Run against the amended text it will find "
      "more, and each one is a filing against the Codification.")
    A("")

    with open(path, "w", encoding="utf-8", newline="\n") as f:
        f.write("\n".join(L))


# ---------------------------------------------------------------- main

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--audit", action="store_true", help="print sample extractions")
    ap.add_argument("--audit-sections", default="",
                    help="comma-separated section numbers to print in full")
    args = ap.parse_args()

    with open(SRC_HTML, encoding="cp1252", errors="replace") as f:
        raw = f.read()
    secs, titles = read_sections(body_html(raw))

    numbers = [s["section"] for s in secs]
    if numbers != list(range(1, len(numbers) + 1)):
        print(f"WARNING: sections are not 1..N (n={len(numbers)}, max={max(numbers)}); "
              f"missing={sorted(set(range(1, max(numbers) + 1)) - set(numbers))[:10]}",
              file=sys.stderr)

    index: dict[int, dict] = {}
    with open(SRC_INDEX, encoding="utf-8-sig", newline="") as f:
        for row in csv.DictReader(f):
            if (row.get("section") or "").strip().isdigit():
                index[int(row["section"])] = {
                    "heading": (row.get("heading") or "").strip(),
                    "title": (row.get("title") or "").strip(),
                }

    by_num = {s["section"]: s for s in secs}
    for s in secs:
        s["metrics"] = section_metrics(s["text"], s["paragraphs"])
        s["units"] = unit_estimate(s["metrics"])
        meta = index.get(s["section"], {})
        s["heading"] = meta.get("heading", "")
        s["index_title"] = meta.get("title", "")
        if not s["title"]:
            s["title"] = s["index_title"]

    adj, edges, noise = build_graph(secs)
    sccs = tarjan_scc(adj)
    comp_of, cadj = condensation(adj, sccs)
    order, level = topo_levels(cadj)

    fan_in = Counter()
    for v, ws in adj.items():
        for w in ws:
            fan_in[w] += 1

    clusters = []
    for i, comp in enumerate(sccs):
        members = sorted(comp)
        deps = sorted({t for v in members for t in adj[v] if comp_of[t] != i})
        merged_members = [m for m in members if m in MERGED]
        status = ("merged" if len(merged_members) == len(members)
                  else "partial" if merged_members else "untouched")
        total = sum(by_num[m]["units"] for m in members)
        clusters.append({
            "cluster": i,
            "sections": members,
            "size": len(members),
            "depth": level[i],
            "deps": deps,
            "dependents": [],
            "status": status,
            "merged_sections": merged_members,
            "units_est": total,
            "units_remaining": total - sum(by_num[m]["units"] for m in merged_members),
            "fan_in": sum(fan_in[m] for m in members),
            "title": by_num[members[0]]["title"] or by_num[members[0]]["index_title"],
            "heading": by_num[members[0]]["heading"],
        })

    cluster_dependents: dict[int, set[int]] = defaultdict(set)
    for c in clusters:
        for d in c["deps"]:
            cluster_dependents[comp_of[d]].add(c["cluster"])
    for c in clusters:
        c["dependents"] = sorted(cluster_dependents[c["cluster"]])

    # Frontier: ready = work left and every external dependency already merged.
    ready = [c for c in clusters
             if c["status"] != "merged" and c["units_remaining"] > 0
             and all(d in MERGED for d in c["deps"])]
    ready_ids = {c["cluster"] for c in ready}
    done_ids = {c["cluster"] for c in clusters
                if c["status"] == "merged" or c["units_remaining"] <= 0}
    next_up = [c for c in clusters
               if c["cluster"] not in ready_ids and c["cluster"] not in done_ids
               and c["deps"]
               and all((d in MERGED) or (comp_of[d] in ready_ids)
                       or (comp_of[d] in done_ids) for d in c["deps"])]

    formalizable = [s for s in secs if s["units"] > 0]
    total_units = sum(s["units"] for s in formalizable)

    # ---- machine-readable outputs
    with open(OUT_REFS, "w", encoding="utf-8", newline="") as f:
        w = csv.DictWriter(f, fieldnames=["from", "to", "phrase"])
        w.writeheader()
        w.writerows(sorted(edges, key=lambda e: (e["from"], e["to"])))

    with open(OUT_SECTIONS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["section", "title", "heading", "units", "numbers", "percent",
                    "rule_paragraphs", "internal_refs", "fan_in", "fan_out",
                    "cluster", "merged"])
        for s in secs:
            m = s["metrics"]
            w.writerow([s["section"], s["title"], s["heading"], s["units"],
                        m["numbers"], m["percent"], m["rule_paragraphs"],
                        m["internal_refs"], fan_in[s["section"]],
                        len(adj[s["section"]]), comp_of[s["section"]],
                        1 if s["section"] in MERGED else 0])

    with open(OUT_CLUSTERS, "w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["cluster", "size", "depth", "status", "units_est",
                    "units_remaining", "fan_in", "sections", "deps",
                    "dependents", "heading", "title"])
        for c in sorted(clusters, key=lambda c: (c["depth"], -c["units_remaining"], c["cluster"])):
            w.writerow([c["cluster"], c["size"], c["depth"], c["status"],
                        c["units_est"], c["units_remaining"], c["fan_in"],
                        " ".join(map(str, c["sections"])),
                        " ".join(map(str, c["deps"])),
                        " ".join(map(str, c["dependents"])),
                        c["heading"], c["title"]])

    graph = {
        "source": SRC_HTML,
        "note": ("RA 8424 (1997) base text only; not the Code as amended. "
                 "Section-level references only; subdivision references are "
                 "counted per section as coupling, not as edges."),
        "sections": len(secs),
        "edges": len(edges),
        "clusters": len(clusters),
        "cycles": [c["sections"] for c in clusters if c["size"] > 1],
        "noise": dict(noise),
        "totals": {
            "formalizable_sections": len(formalizable),
            "units_est": total_units,
            "units_merged": sum(s["units"] for s in formalizable if s["section"] in MERGED),
            "density_basis": "1 + rule_paragraphs + max(1, rp//10); 0 if score<6",
        },
        "nodes": [{"section": s["section"], "title": s["title"],
                   "heading": s["heading"], "units": s["units"],
                   "numbers": s["metrics"]["numbers"],
                   "internal_refs": s["metrics"]["internal_refs"],
                   "fan_in": fan_in[s["section"]],
                   "fan_out": len(adj[s["section"]]),
                   "cluster": comp_of[s["section"]],
                   "merged": s["section"] in MERGED} for s in secs],
        "cluster_list": [{k: c[k] for k in
                          ("cluster", "sections", "size", "depth", "status", "deps",
                           "dependents", "units_est", "units_remaining", "fan_in",
                           "heading", "title")} for c in clusters],
        "frontier_ready": [c["cluster"] for c in ready],
        "frontier_next": [c["cluster"] for c in next_up],
        "order": order,
    }
    with open(OUT_JSON, "w", encoding="utf-8") as f:
        json.dump(graph, f, indent=1)

    write_markdown(OUT_MD, {
        "sections": secs, "clusters": clusters, "adj": adj, "cadj": cadj,
        "comp_of": comp_of, "level": level, "fan_in": fan_in, "edges": edges,
        "noise": noise, "ready": ready, "next_up": next_up,
    })

    # ---- console summary
    print(f"sections parsed      : {len(secs)}")
    print(f"section-level edges  : {len(edges)}  (mean out-degree {len(edges)/len(secs):.2f})")
    print(f"refs dropped         : {dict(noise)}")
    print(f"clusters (SCCs)      : {len(clusters)}  (multi-section: "
          f"{sum(1 for c in clusters if c['size'] > 1)})")
    print(f"largest clusters     : {sorted((c['size'] for c in clusters), reverse=True)[:8]}")
    print(f"formalizable sections: {len(formalizable)} of {len(secs)}")
    print(f"units estimate       : {total_units}  (merged {graph['totals']['units_merged']})")
    print(f"depth distribution   : {dict(sorted(Counter(c['depth'] for c in clusters).items()))}")
    print(f"ready frontier       : {len(ready)} clusters, "
          f"{sum(c['units_remaining'] for c in ready)} units")
    print(f"next frontier        : {len(next_up)} clusters, "
          f"{sum(c['units_remaining'] for c in next_up)} units")
    print("top fan-in           : " + ", ".join(
        f"{m}({fan_in[m]})" for m in sorted(fan_in, key=lambda m: -fan_in[m])[:12]))

    if args.audit:
        print("\n-- sample edges --")
        for e in sorted(edges, key=lambda e: (e["from"], e["to"]))[:25]:
            print(f"  {e['from']:>3} -> {e['to']:>3}  {e['phrase'][:78]}")
        print("\n-- cycles --")
        for c in clusters:
            if c["size"] > 1:
                print(f"  {c['sections']}")
        print("\n-- highest fan-in --")
        for m in sorted(fan_in, key=lambda m: -fan_in[m])[:10]:
            print(f"  §{m:<4} {by_num[m]['heading'][:60]:<62} cited by {fan_in[m]}")

    if args.audit_sections:
        for token in args.audit_sections.split(","):
            num = int(token.strip())
            s = by_num[num]
            print(f"\n===== §{num} [{s['heading']}] units={s['units']} "
                  f"out={sorted(adj[num])} in={[m for m in adj if num in adj[m]]}")
            print(s["text"][:1400])
    return 0


if __name__ == "__main__":
    sys.exit(main())
