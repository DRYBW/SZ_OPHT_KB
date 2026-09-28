#!/usr/bin/env python3
import re, time, urllib.request

FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"
ACC = ['GSE81905','GSE137400','GSE133382','GSE137863','GSE150703','GSE184933','GSE255520',
       'GSE314326','GSE125708','GSE169097','GSE319256','GSE293358','GSE325479','GSE147573','GSE201402']

LBL = re.compile(r'cell.?type|cellclass|cell_?class|class|cluster|annotat|label|metadata|barcode', re.I)

def get(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.read().decode('utf-8', 'replace')
        except Exception as e:
            last = str(e)[:70]; time.sleep(2)
    return 'EXC ' + last

out = {}
for acc in ACC:
    grp = acc[:-3] + 'nnn'
    txt = get(f"{FTP}/{grp}/{acc}/suppl/filelist.txt")
    time.sleep(0.4)
    if txt.startswith('EXC'):
        out[acc] = {'filelist': txt}
        print(acc, txt[:70], flush=True)
        continue
    lines = [l for l in txt.splitlines() if l.startswith('File')]
    per_gsm = {}
    for l in lines:
        parts = l.split('\t')
        fn = parts[1] if len(parts) > 1 else ''
        m = re.match(r'GSM(\d+)_', fn)
        gsm = m.group(0)[:-1] if m else 'series'
        per_gsm.setdefault(gsm, []).append((fn, parts[2] if len(parts) > 2 else ''))
    labelish = sorted(set(fn for items in per_gsm.values() for fn, _ in items if LBL.search(fn)))
    out[acc] = {'n_files': len(lines), 'labelish_files': labelish[:25],
                'series_level': [fn for fn, _ in per_gsm.get('series', [])][:12]}
    print(acc, '| files', len(lines), '| labelish:', labelish[:8], flush=True)
import json
json.dump(out, open('/tmp/mx_filelists.json', 'w'), ensure_ascii=False, indent=1)
print('DONE_FL')
