#!/usr/bin/env python3
import re, time, urllib.request

FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"
# acc -> group dir (GEO groups are 3-digit blocks truncated)
GRP = {
 'GSE133382': 'GSE133nnn', 'GSE137863': 'GSE137nnn', 'GSE137398': 'GSE137nnn',
 'GSE137828': 'GSE137nnn', 'GSE150703': 'GSE150nnn', 'GSE255520': 'GSE255nnn',
 'GSE81904': 'GSE81nnn', 'GSE81905': 'GSE81nnn',
}

def get(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            last = str(e)[:70]; time.sleep(2)
    return 'EXC ' + last

for acc, grp in GRP.items():
    txt = get(f"{FTP}/{grp}/{acc}/suppl/filelist.txt")
    time.sleep(0.4)
    if txt.startswith('EXC'):
        print(acc, txt[:80], flush=True); continue
    tot = 0; labelish = []
    for l in txt.splitlines():
        parts = l.split('\t')
        if parts[0] in ('Archive', 'File') and len(parts) > 3:
            try: tot += int(parts[3])
            except Exception: pass
            if re.search(r'celltype|cell.?class|class|annotat|label|metadata', parts[1], re.I) and 'barcode' not in parts[1]:
                labelish.append(parts[1])
    print(acc, '| total_bytes', tot, f'({tot/2**30:.2f}GiB) | label files:', sorted(set(labelish))[:8], flush=True)
