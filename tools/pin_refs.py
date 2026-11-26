import json, sys, urllib.request, urllib.parse

DOIS = [
    "10.1145/3473582",
    "10.1145/3446804.3446850",
    "10.1080/17579961.2024.2313801",
    "10.1145/5689.5920",
    "10.1787/3afe6ba5-en",
    "10.1007/s10506-022-09328-5",
    "10.1145/3594536.3595163",
    "10.1098/rsta.2023.0159",
    "10.1111/jels.12413",
    "10.1093/jla/laae003",
    "10.1016/j.cosrev.2010.09.009",
    "10.1145/263699.263712",
    "10.1145/1629575.1629596",
    "10.1145/1538788.1538814",
    "10.1007/978-3-030-79876-5_37",
    "10.1145/3372885.3373824",
    "10.1145/200836.200880",
    "10.1007/s10506-012-9131-x",
    "10.26826/law-in-context.v37i1.134",
    "10.1007/978-3-031-57267-8_16",
]

QUERIES = [
    "A Logic for Statutes Lawsky Florida Tax Review",
    "Formalizing the Code Lawsky Tax Law Review",
    "Coding the Code: Catala and Computationally Accessible Tax Law",
    "Code-driven law freezing the future and scaling the past Hildebrandt",
    "Technological due process Citron",
    "Accountable algorithms Kroll Huey Barocas",
    "From Rules as Code to Mindset Strategies Burdon",
    "dataset for statutory reasoning in tax law entailment and question answering",
    "LegalBench collaboratively built benchmark legal reasoning large language models",
    "Autoformalization with large language models Wu Jiang",
    "Robodebt automated debt recovery administrative law Carney",
]


def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "ref-pinner/1.0 (mailto:none@example.org)"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)["message"]


def fmt(m):
    authors = "; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author", [])[:8])
    yr = (m.get("issued", {}).get("date-parts") or [[None]])[0][0]
    return (f"{m.get('DOI')} | {yr} | {authors} | {(m.get('title') or [''])[0]} | "
            f"{(m.get('container-title') or [''])[0]} | v{m.get('volume','')} i{m.get('issue','')} p{m.get('page','')}")


mode = sys.argv[1] if len(sys.argv) > 1 else "dois"
if mode == "dois":
    for d in DOIS:
        try:
            print("OK  " + fmt(get("https://api.crossref.org/works/" + urllib.parse.quote(d))))
        except Exception as e:
            print("ERR " + d + " " + str(e))
else:
    for q in QUERIES:
        try:
            u = "https://api.crossref.org/works?rows=2&query.bibliographic=" + urllib.parse.quote(q)
            req = urllib.request.Request(u, headers={"User-Agent": "ref-pinner/1.0"})
            with urllib.request.urlopen(req, timeout=30) as r:
                items = json.load(r)["message"]["items"]
            print("Q   " + q)
            for it in items:
                print("    " + fmt(it))
        except Exception as e:
            print("ERR " + q + " " + str(e))
