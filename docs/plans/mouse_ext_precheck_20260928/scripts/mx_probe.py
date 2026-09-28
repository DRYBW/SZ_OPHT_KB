#!/usr/bin/env python3
"""MOUSEEXT batch metadata probe: GSM titles, supp listing (names+sizes), pubmed. Zero file-body downloads."""
import json, re, time, urllib.request

EUTILS = "https://eutils.ncbi.nlm.nih.gov/entrez/eutils"
FTP = "https://ftp.ncbi.nlm.nih.gov/geo/series"

CAND = ['GSE63472','GSE147573','GSE201402','GSE150703','GSE184933','GSE255520',
        'GSE314326','GSE125708','GSE169097','GSE319256','GSE293358','GSE137400','GSE81905','GSE325479']

def get(url, timeout=45):
    req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0 (research metadata probe)'})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return r.read().decode('utf-8', 'replace')

def probe(acc, out):
    rec = {'acc': acc}
    d = json.loads(get(f"{EUTILS}/esearch.fcgi?db=gds&term={acc}%5BACCESSION%5D&retmode=json"))['esearchresult']['idlist']
    time.sleep(0.4)
    if not d:
        rec['error'] = 'no uid'; out[acc] = rec; return
    xml = get(f"{EUTILS}/esummary.fcgi?db=gds&id={d[0]}&retmode=xml")
    t = re.search(r'<Item Name="title" Type="String">(.*?)</Item>', xml, re.S)
    rec['title'] = re.sub(r'\s+', ' ', t.group(1))[:200] if t else None
    n = re.search(r'<Item Name="n_samples"[^>]*>(\d+)', xml)
    rec['n_gsm'] = int(n.group(1)) if n else None
    gsms = re.findall(r'<Item Name="Accession" Type="String">(GSM\d+)</Item>\s*<Item Name="Title" Type="String">(.*?)</Item>', xml)
    rec['gsm_titles_sample'] = [g[1][:90] for g in gsms[:25]]
    time.sleep(0.4)
    try:
        lx = get(f"{EUTILS}/elink.fcgi?dbfrom=gds&db=pubmed&id={d[0]}&retmode=xml")
        rec['pmids'] = re.findall(r'<Id>(\d{7,9})</Id>', lx)[:3]
    except Exception:
        rec['pmids'] = ['ERR']
    grp = acc[:-3] + 'nnn'
    time.sleep(0.4)
    try:
        listing = get(f"{FTP}/{grp}/{acc}/suppl/")
        files = re.findall(r'<a href="([^"]+)">[^<]*</a>\s*</td>\s*<td align="right">([^<]*)</td>', listing)
        if not files:
            files = re.findall(r'<a href="([^"]+)">[^<]*</a>.*?(\d[\d,\.]*[KMGT]?)', listing, re.S)
        rows = []
        for href, size in files:
            if not href or href.startswith(('?', '/')) or 'vulnerability' in href:
                continue
            rows.append((href, size))
        rec['supp'] = rows[:40]
    except Exception as e:
        rec['supp'] = 'ERR ' + str(e)[:90]
    out[acc] = rec
    supp_n = len(rec.get('supp', [])) if isinstance(rec.get('supp'), list) else rec.get('supp')
    print(acc, '|', (rec.get('title') or '')[:60], '| gsm', rec.get('n_gsm'), '| supp', supp_n, '| pmid', rec.get('pmids'), flush=True)

out = {}
for acc in CAND:
    try:
        probe(acc, out)
    except Exception as e:
        out[acc] = {'acc': acc, 'error': str(e)[:120]}
        print(acc, 'ERR', str(e)[:100], flush=True)
    json.dump(out, open('/tmp/mouseext_probe.json', 'w'), ensure_ascii=False, indent=1)
print('DONE')
