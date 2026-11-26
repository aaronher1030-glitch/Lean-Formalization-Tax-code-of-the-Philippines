import json, sys, time, urllib.request, urllib.parse
D="""10.1007/s10506-012-9131-x 10.1145/3594536.3595163 10.1145/200836.200880 10.1093/jla/laae003 10.1007/978-3-030-79876-5_37 10.2139/ssrn.4583531 10.5040/9781509937097.ch-003 10.1007/s10506-022-09328-5 10.1080/17579961.2024.2313801 10.1145/1629575.1629596 10.5744/ftr.2017.0002 10.2139/ssrn.2987065 10.25172/smulr.75.3.4 10.1145/1538788.1538814 10.1111/jels.12413 10.1145/3372885.3373824 10.1016/j.cosrev.2010.09.009 10.1145/3473582 10.1145/3446804.3446850 10.1787/3afe6ba5-en 10.1007/978-3-031-57267-8_16 10.1098/rsta.2023.0159 10.1145/263699.263712 10.1145/5689.5920 10.1016/j.clsr.2026.106377 10.26826/law-in-context.v37i1.134 10.52202/068431-2344""".split()
for d in D:
    try:
        req=urllib.request.Request("https://api.crossref.org/works/"+urllib.parse.quote(d),headers={"User-Agent":"ref-pinner/1.0"})
        m=json.load(urllib.request.urlopen(req,timeout=30))["message"]
        au="; ".join(f"{a.get('family','')}, {a.get('given','')}" for a in m.get("author",[])[:7])
        yr=(m.get("issued",{}).get("date-parts") or [[None]])[0][0]
        print(f"{d} | {yr} | {au} | {(m.get('title') or [''])[0]} | {(m.get('container-title') or [''])[0]} | v{m.get('volume','')} i{m.get('issue','')} p{m.get('page','')}")
    except Exception as e:
        print("ERR",d,e)
    time.sleep(1.2)
