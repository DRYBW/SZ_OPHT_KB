#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P1c: 外部文献面板重建（REVIEWER_LLM 预审回函 §1.2 可粘贴文本的操作化；冻结前重跑，S3 授权）。
分层检索（逐基因）：
  Q_A = '"GENE" AND "lacrimal gland" AND ("marker" OR "cell type" OR "single-cell" OR "scRNA" OR "transcriptom" OR "immunohistochem*" OR "in situ")'
  Q_B = '"GENE" AND "lacrimal gland"'
主证据 Tier1：来自 Q_A∪Q_B 命中，同一条记录 title+abstract 含 ①基因精确 token ②泪腺语境（lacrim…gland/lacrimation；
  **排除 lacrimal sac|dacryocyst|canalicul|meibom 语境**）③细胞类型/marker/组学定位语义 token。
Tier2（敏感性档，不入主面板）：无 Tier1 时——>=2 个不同 PMID、每个 title 含泪腺语境（同上排除）、
  基因 token 在 title/abstract 可见、>=1 条含 marker 语义。
疾病蛋白组/泪液唾液蛋白组语境（无细胞类型定位）= 附录档 TIER-APPX（不打分）。
每群最低有效 Tier1 基因数 MIN_T1=3，不足=panel_unavailable（不得由 1-2 基因构成 0.7 锚定）。
原始返回逐查询留 ledgers/eurpmc2/。
"""
import json, os, re, time, urllib.request, urllib.parse, csv

BASE = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
LEDGER = f'{BASE}/ledgers/eurpmc2'
os.makedirs(LEDGER, exist_ok=True)

PANEL_CAND = {
  'ACINAR':   ['LACRT','MUC7','LPO','PIP','PRB1','PRB2','PRB3','STATH','HTN1','PRSS1','CTRB1','CTRB2',
               'PNLIP','PLA2G1B','CA6','BPIFA2','ZG16B','AQP5','PRR4','CST1','CST4','SCGB1D1','SCGB2A2',
               'SCGB3A1','DCD','SLPI','ZGP2','PRR5','ZG16'],
  'DUCT':     ['KRT19','KRT7','KRT8','KRT18','CFTR','SOX9','SPP1','CEACAM6','PIGR','AQP1','ELF3','BPIFB1',
               'PRR27','MSMB','PSCA','KRT13','ANXA8','ANXA1','LTF','TGM2','AQP5','SCGB1A1','KRT23'],
  'MYOEPITH': ['ACTA2','CNN1','MYH11','TAGLN','KRT5','KRT14','KRT15','TP63','MYL9','LMOD1','PRLR','CNGB1',
               'CALD1','ACTG2','TPM2','S100A2','KRT6A','KRT17'],
  'IMMUNE':   ['PTPRC','CD3D','CD3E','CD68','MS4A1','MZB1','NKG7','CD74','IL7R','CCL5','CSF1R','CD79A','CD79B',
               'LYZ','LTF','ITGAM','FCGR3A','IGHM','JCHAIN','TNC'],
  'ENDO':     ['PECAM1','CLDN5','VWF','CDH5','KDR','ESAM','RAMP2','FLT1','RGS5','CAV1','PLVAP','TIE1'],
  'NEUROGLIA':['PLP1','S100B','SOX10','MAG','ST8SIA3','NGFR','GFAP','S100A4','GAP43','PRPH','SNCG','PHOX2B','TUBB3','ELAVL4'],
  'STROMA':   ['DCN','LUM','COL1A1','COL1A2','FBN1','PDGFRB','MMP2','POSTN','PTGDS','TWIST2','FN1','THY1','LDLRAD4'],
}
EXCLUDED_PLATFORM = {'LYZ': '泪液超富集/板法 ambient 先验（预登记平台排除规则，不依赖本 run 结果；REVIEWER_LLM Q8#13 独立性披露）',
                     'LTF': '泪液超富集/板法 ambient 先验（同上）'}
CTX_ON  = re.compile(r'lacrim|lacrimation|tear[- ]?duct\b', re.I)
NEG     = re.compile(r'lacrimal sac|dacryocyst|canalicul|meibom|lacrimal canals?\b|nasolacrimal|lacrimal drainage', re.I)
MARKSEM = re.compile(r'marker|cell[- ]type|single[- ]cell|sc[- ]?rna|scRNA|transcriptom|immunohistochem|in situ|expression profil|cell type', re.I)

def eurpmc(query, tag):
    fp = f'{LEDGER}/{tag}.json'
    if os.path.exists(fp):
        return json.load(open(fp))
    url = ('https://www.ebi.ac.uk/europepmc/webservices/rest/search?query='
           + urllib.parse.quote(query) + '&format=json&pageSize=8&resultType=core')
    req = urllib.request.Request(url, headers={'User-Agent': 'KBX-panel/2.0'})
    for att in range(3):
        try:
            with urllib.request.urlopen(req, timeout=90) as r:
                data = json.loads(r.read().decode('utf-8'))
            data['_query'] = query
            tmp = fp + '.tmp'; json.dump(data, open(tmp, 'w')); os.replace(tmp, fp)
            return data
        except Exception as e:
            time.sleep(3 * (att + 1))
    raise RuntimeError(f'eurpmc failed {tag}')

def tok(text, gene):
    return re.search(r'(?<![A-Za-z0-9])' + re.escape(gene) + r'(?![A-Za-z0-9])', text or '', re.I) is not None

def evaluate(gene, hits_a, hits_b):
    """-> (tier, pmids, note)"""
    pool = []
    seen = set()
    for h in (hits_a + hits_b):
        pmid = h.get('pmid')
        if not pmid or pmid in seen:
            continue
        seen.add(pmid)
        pool.append(h)
    t1_pmids = []
    for h in pool:
        body = (h.get('title') or '') + ' \u00a7 ' + (h.get('abstractText') or '')
        if tok(body, gene) and CTX_ON.search(body) and not NEG.search(body) and MARKSEM.search(body):
            t1_pmids.append(h['pmid'])
    if t1_pmids:
        return 'TIER1', t1_pmids[:3], 'gene+CTX+marker-semantics in title/abstract, neg-context excluded'
    # Tier2：>=2 个不同 PMID、title 含 CTX 无 NEG、基因 token 可见、>=1 含 MARKSEM
    t2 = []
    for h in pool:
        title = h.get('title') or ''
        body = title + ' \u00a7 ' + (h.get('abstractText') or '')
        if CTX_ON.search(title) and not NEG.search(body) and tok(body, gene):
            t2.append(h['pmid'])
    if len(set(t2)) >= 2:
        pool_by_pmid = {h['pmid']: h for h in pool if h.get('pmid')}
        sem = any(MARKSEM.search(((pool_by_pmid[p].get('title') or '') + ' ' + (pool_by_pmid[p].get('abstractText') or '')))
                  for p in set(t2) if p in pool_by_pmid)
        if sem:
            return 'TIER2', sorted(set(t2))[:3], '>=2 lacrimal-title PMIDs, gene visible, >=1 marker-semantics'
    if t2:
        return 'TIER-APPX', sorted(set(t2))[:3], 'lacrimal context only, no marker semantics = appendix (disease/humoral protein record)'
    # 疾病蛋白组语境兜底：CTX 仅在 body、有命中无细胞定位
    for h in pool:
        body = (h.get('title') or '') + ' ' + (h.get('abstractText') or '')
        if CTX_ON.search(body) and tok(body, gene) and not NEG.search(body):
            return 'TIER-APPX', [h['pmid']], 'CTX+gene co-occurrence, no cell-type localization = appendix'
    return 'FAIL', [], 'no lacrimal-gland cell-type-context record'

rows = []
for grp, genes in PANEL_CAND.items():
    for gene in dict.fromkeys(genes):
        if gene in EXCLUDED_PLATFORM:
            rows.append(dict(group=grp, gene=gene, tier='EXCLUDED-PLATFORM', pmids='',
                             note=EXCLUDED_PLATFORM[gene], qa_hits='', qb_hits=''))
            continue
        qa = f'"{gene}" AND "lacrimal gland" AND (marker OR "cell type" OR "single-cell" OR scRNA OR transcriptom OR immunohistochemistry OR "in situ")'
        qb = f'"{gene}" AND "lacrimal gland"'
        da = eurpmc(qa, f'A_{gene}')
        time.sleep(0.3)
        db = eurpmc(qb, f'B_{gene}')
        time.sleep(0.3)
        tier, pmids, note = evaluate(gene, da.get('resultList', {}).get('result', []) or [],
                                     db.get('resultList', {}).get('result', []) or [])
        rows.append(dict(group=grp, gene=gene, tier=tier, pmids='|'.join(pmids), note=note,
                         qa_hits=da.get('hitCount'), qb_hits=db.get('hitCount')))
        print(f'{grp:9s} {gene:9s} {tier:15s} pmids={",".join(pmids)[:34]:34s} qa={da.get("hitCount")} qb={db.get("hitCount")}', flush=True)

with open(f'{BASE}/ledgers/KBX_PANEL_CANDIDATES_V2.tsv', 'w', newline='', encoding='utf-8') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t'); w.writeheader(); w.writerows(rows)

MIN_T1 = 3
print('\n=== group summary (Tier1 = main panel) ===')
main_groups = {}
for grp, genes in PANEL_CAND.items():
    t1 = [r['gene'] for r in rows if r['group'] == grp and r['tier'] == 'TIER1']
    t2 = [r['gene'] for r in rows if r['group'] == grp and r['tier'] == 'TIER2']
    ap = [r['gene'] for r in rows if r['group'] == grp and r['tier'] == 'TIER-APPX']
    avail = 'OK' if len(t1) >= MIN_T1 else 'panel_unavailable'
    main_groups[grp] = t1
    print(f'{grp}: T1={len(t1)} {t1} | T2={t2} | APPX={ap} → {avail}')
json.dump(main_groups, open(f'{BASE}/ledgers/KBX_PANEL_MAIN_groups.json', 'w'), ensure_ascii=False, indent=1)
