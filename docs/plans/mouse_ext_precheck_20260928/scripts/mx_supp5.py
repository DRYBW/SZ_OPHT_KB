#!/usr/bin/env python3
import re, time, urllib.request

URLS = {
 'GSE133382': 'GSE133nnn/GSE133382', 'GSE137863': 'GSE137nnn/GSE137863',
 'GSE137398': 'GSE137nnn/GSE137398', 'GSE150703': 'GSE150nnn/GSE150703',
 'GSE255520': 'GSE255nnn/GSE255520', 'GSE137828': 'GSE137nnn/GSE137828',
}

def human(b):
    try:
        v = float(re.sub(r'[A-Za-z]', '', b)); u = b[-1] if b[-1].isalpha() else 'B'
    except Exception:
        return 0
    mul = {'K': 2**10, 'M': 2**20, 'G': 2**30, 'T': 2**40, 'B': 1}.get(u, 1)
    return v * mul

for acc, path in URLS.items():
    try:
        req = urllib.request.Request(f"https://ftp.ncbi.nlm.nih.gov/geo/series/{path}/suppl/",
                                     headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=45) as r:
            x = r.read().decode('utf-8', 'replace')
    except Exception as e:
        print(acc, 'ERR', str(e)[:60]); continue
    rows = re.findall(r'<a href="([^"]+)">[^<]*</a>\s*</td>\s*<td[^>]*>\s*</td>\s*<td[^>]*>([^<]*)</td>\s*<td[^>]*>([^<]*)</td>', x)
    if not rows:
        rows = re.findall(r'<a href="([^"]+)">.*?</td>\s*<td[^>]*>([\d\.]+[KMGT])</td>', x, re.S)
    tot = 0; lbl = []
    for h, a, b in [r if len(r) == 3 else (r[0], '', r[1]) for r in rows]:
        if 'vulnerability' in h or h in ('../', '/'): continue
        size = human(b); tot += size
        if re.search(r'celltype|class|annotat|label|metadata|subtype', h, re.I) and 'barcod' not in h:
            lbl.append((h, b))
    print('==', acc, '| files', len(rows), '| total %.2fGiB' % (tot / 2**30))
    for h, s in lbl[:10]:
        print('   LABEL:', h, s)
    time.sleep(0.4)
