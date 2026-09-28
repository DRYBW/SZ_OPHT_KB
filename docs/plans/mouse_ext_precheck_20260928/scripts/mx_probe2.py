#!/usr/bin/env python3
import json, re, time, urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"

def get(url, timeout=40, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (metadata probe)'})
            with urllib.request.urlopen(req, timeout=timeout) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            if k == tries - 1:
                return 'EXC ' + str(e)[:120]
            time.sleep(3)

out = {}
# full GSM titles for 184933 and 63472, plus 325479 taxon
for acc in ['GSE63472', 'GSE184933', 'GSE325479']:
    time.sleep(0.5)
    d = get(f"{EUTILS}/esearch.fcgi?db=gds&term={acc}%5BACCESSION%5D&retmode=json")
    try:
        uid = json.loads(d)['esearchresult']['idlist'][0]
    except Exception:
        out[acc] = 'esearch fail'; continue
    time.sleep(0.5)
    xml = get(f"{EUTILS}/esummary.fcgi?db=gds&id={uid}&retmode=xml")
    tax = re.search(r'<Item Name="taxon" Type="String">(.*?)</Item>', xml)
    gsms = re.findall(r'<Item Name="Accession" Type="String">(GSM\d+)</Item>\s*<Item Name="Title" Type="String">(.*?)</Item>', xml)
    grp = acc[:-3] + 'nnn'
    time.sleep(0.5)
    listing = get(f"{FTP}/{grp}/{acc}/suppl/")
    files = re.findall(r'<a href="([^"]+)">[^<]*</a>\s*</td>\s*<td align="right">([^<]*)</td>', listing)
    rows = [(h, s) for h, s in files if h and not h.startswith(('?', '/')) and 'vulnerability' not in h]
    out[acc] = {'taxon': tax.group(1) if tax else None,
                'n_gsm_shown': len(gsms),
                'titles': [t[:110] for _, t in gsms],
                'supp': rows[:60]}
    print(acc, out[acc]['taxon'], len(gsms), 'suppfiles', len(rows), flush=True)
json.dump(out, open('/tmp/mx_probe2.json', 'w'), ensure_ascii=False, indent=1)
print('DONE2')
