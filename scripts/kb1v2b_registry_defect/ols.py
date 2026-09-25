import json, urllib.request, sys

def get(url):
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0", "Accept": "application/json"})
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)

ids = ["UBERON_0001768", "UBERON_0001769", "UBERON_0001776", "UBERON_0001775", "UBERON_0005969",
       "UBERON_0001774", "UBERON_0000975", "UBERON_0011892"]
for q in ids:
    url = f"https://www.ebi.ac.uk/ols4/api/ontologies/uberon/terms?iri=http://purl.obolibrary.org/obo/{q}"
    try:
        d = get(url)
        t = d.get("_embedded", {}).get("terms", [])
        if t:
            lab = t[0].get("label")
            desc = (t[0].get("description") or [""])[0]
            iri = t[0].get("iri")
            print(f"{q} -> {lab} | iri={iri} | {desc[:300]}")
        else:
            print(f"{q} -> NO_TERM")
    except Exception as e:
        print(f"{q} -> ERR {e}")
