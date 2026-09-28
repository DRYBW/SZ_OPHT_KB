#!/usr/bin/env python3
"""HEAD-only size probe for candidate series RAW tarballs. Zero body downloads."""
import json, re, time, urllib.request

FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"

TARGETS = {
 'GSE81905': ['GSE81905_RAW.tar'],
 'GSE137400': ['GSE137400supp.txt'],
 'GSE133382': ['GSE133382_RAW.tar'],
 'GSE137863': ['GSE137863_RAW.tar'],
 'GSE150703': ['GSE150703_RAW.tar'],
 'GSE184933': ['GSE184933_RAW.tar'],
 'GSE255520': ['GSE255520_RAW.tar'],
 'GSE314326': ['GSE314326_RAW.tar'],
 'GSE125708': ['GSE125708_RAW.tar'],
 'GSE169097': ['GSE169097_RAW.tar'],
 'GSE319256': ['GSE319256_RAW.tar'],
 'GSE293358': ['GSE293358_RAW.tar'],
 'GSE325479': ['GSE325479_RAW.tar'],
 'GSE63472': ['GSE63472_P14Retina_merged_digital_expression.txt.gz'],
 'GSE201402': ['GSE201402_RAW.tar'],
}

def head(url, tries=3):
    for k in range(tries):
        try:
            req = urllib.request.Request(url, method='HEAD', headers={'User-Agent': 'Mozilla/5.0'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return r.headers.get('Content-Length'), r.status
        except Exception as e:
            last = str(e)[:80]; time.sleep(2)
    return 'ERR ' + last, 0

out = {}
for acc, files in TARGETS.items():
    grp = acc[:-3] + 'nnn'
    rec = {}
    for f in files:
        url = f"{FTP}/{grp}/{acc}/suppl/{f}"
        size, st = head(url)
        rec[f] = {'bytes': size, 'status': st}
        print(acc, f, rec[f], flush=True)
        time.sleep(0.35)
    out[acc] = rec
    json.dump(out, open('/tmp/mx_heads.json', 'w'), indent=1)
print('DONE_HEADS')
