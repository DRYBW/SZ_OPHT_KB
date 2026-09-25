import json, sys, os

for f in sys.argv[1:]:
    if not os.path.exists(f) or os.path.getsize(f) == 0:
        print(f, "MISSING/EMPTY"); continue
    try:
        d = json.load(open(f))
    except Exception as e:
        print(f, "PARSE ERR", e, open(f).read()[:200]); continue
    res = d.get("result", d)
    print("#####", f)
    for k, v in res.items():
        if k == "uids":
            continue
        if isinstance(v, dict):
            print("  title:", v.get("title"))
            print("  accession:", v.get("accession"), "| n_samples:", v.get("n_samples"),
                  "| taxon:", v.get("taxon"), "| type:", v.get("gdsType"), "| PDAT:", v.get("PDAT"))
            print("  summary:", (v.get("summary") or "")[:700].replace("\n", " "))
            print("  ftplink:", v.get("FTPLink"))
        else:
            print("  ", k, "=", str(v)[:200])
