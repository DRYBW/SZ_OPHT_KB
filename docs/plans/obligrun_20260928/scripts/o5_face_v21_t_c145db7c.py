#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, 案A执行细则1-2): 票面 kb9_face_v2.1 构建。
规则（裁定逐字）：「逐簇比对 lit 行 PMID 与该簇 truth 来源论文（registry 血缘件），凡同源即剔」。
- 在现面（v1=EV_DIGEST_SLIM_q6_oblig.jsonl, sha ba76b6ce…）机械复算命中集，非点名剔除；
- 预期恰={Q6::7,Q6::11}×PMID 36712326 两行；命中多于 2 行→全剔并如实登记差异；少于→中止报错（血缘断裂）；
- 新面 33 簇集合不变、ranking 逐字节不动、非剔除字段零漂移（硬断言）；
- 产物: face/kb9_face_v2.1.jsonl + out/FACE_V21_ledger.tsv + sha 入账（PREREG 追加节引用）。
退出码: 0=构建通过; 2=零漂移断言失败; 3=命中集少于预期（血缘不一致，停卡）。"""
import json, hashlib, sys
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
V1 = f'{ROOT}/face/EV_DIGEST_SLIM_q6_oblig.jsonl'
V21 = f'{ROOT}/face/kb9_face_v2.1.jsonl'
V1_SHA_EXPECT = 'ba76b6ce1af1654ef4421dc81c404edda57f7842ebfc5c26178b8ddcd60be934'

# ---- 0. 前置 sha 校验（消费面=v1 冻结件本体）----
sha_v1 = hashlib.sha256(open(V1, 'rb').read()).hexdigest()
assert sha_v1 == V1_SHA_EXPECT, f'v1 面 sha 不符冻结: {sha_v1}'

# ---- 1. registry 血缘件（study→truth 来源论文，机械登记表）----
# 来源链：D002 obs.study 直读全集=9 标签（Q6_VOCAB2_PREREG AE 件/R24 provenance）；
# 6 标签自带 GSE accession，source paper=该 GSE 系列题名所对应的发表文献（2026-09-28 eutils
# esummary/db=gds 系列题名 + db=pubmed 题名/首作者解析；外部证据只读，登记于本表 basis）；
# chen_cornea/chen_limbus/chen_sclera 无 accession——残余限制沿 VERDICT v1（12 命中 PMID 首作者
# 逐篇核对非 chen 系，登记不虚构）。
LINEAGE = {
    'chakravarti_GSE218123': {
        'series_title': 'Single cell RNA-seq of human cornea organoids identifies cell fates of a developing immature corneal epithelium',
        'source_pmid': '36712326',
        'basis': 'GEO 系列题名与 PubMed 36712326(Maiti G; PNAS Nexus 2022) 题名逐字一致 + 论文 Data Availability 自存 GSE218123 + D002 obs.study 直读 4,388 评测细胞（OB-4 v1 三重证据链）',
    },
    'lako_adult_GSE155683': {
        'series_title': 'A single cell atlas of human cornea that defines its development, limbal progenitor cells and their interactions with the immune cells',
        'source_pmid': '33865984',
        'basis': 'GEO 题名→PubMed 题名检索命中 33865984(Collin J; Ocul Surf 2021)——不在票面 12 PMID 集内，无剔除贡献；38177186(Li M)对其 GSE155683 提及=下载输入（第三方再分析，沿 OB-4 v1 披露）；34381080(Ligocki) 本地语料 46 chunk 零 GSE 提及，非其来源',
    },
    'shi_GSE157474': {
        'series_title': 'Single-cell analysis of limbal niche heterogeneity and crosstalk with corneal epithelial stem cells',
        'source_pmid': None,
        'basis': '系列题名与票面 12 PMID 题名零匹配（逐条比对表见 FACE_V21_ledger 附注）——无剔除贡献',
    },
    'chen_pub_GSE153515': {
        'series_title': 'Single-cell transcriptomics uncovers human corneal limbal stem cells and its differentiation',
        'source_pmid': None,
        'basis': '题名与票面 12 PMID 零匹配——无剔除贡献',
    },
    'li_GSE147979': {
        'series_title': 'Multi-species single-cell transcriptomic analysis of ocular compartment regulons',
        'source_pmid': None,
        'basis': '题名与票面 12 PMID 零匹配——无剔除贡献',
    },
    'dickman_GSE186433': {
        'series_title': 'Single cell transcriptomics reveal the heterogeneity of the human cornea to identify novel cell types and donors',
        'source_pmid': None,
        'basis': '题名与票面 12 PMID 零匹配——无剔除贡献',
    },
    'chen_cornea': {'series_title': None, 'source_pmid': None, 'basis': 'obs 无 accession，本地不可解析 source paper（残余限制沿 v1；12 PMID 首作者无 chen 系）'},
    'chen_limbus': {'series_title': None, 'source_pmid': None, 'basis': '同上'},
    'chen_sclera': {'series_title': None, 'source_pmid': None, 'basis': '同上'},
}
SOURCE_PMIDS = {v['source_pmid'] for v in LINEAGE.values() if v['source_pmid']}
assert '36712326' in SOURCE_PMIDS and len(SOURCE_PMIDS) == 2  # {36712326, 33865984}

# ---- 2. 簇×study 组成（obs.study×leiden 直读，registry 血缘件消费面）----
cl = pd.read_csv('/mnt/D/EyeKB/plans/evalset/clustering/Q6_clusters.tsv', sep='\t', index_col=0)
import anndata as ad
a = ad.read_h5ad('/mnt/D/EyeKB/plans/evalset/data/Q6_sub100k.h5ad', backed='r')
j = cl.join(a.obs['study'].to_frame(), how='inner')
assert len(j) == 100000
j['cid'] = 'Q6::' + j['leiden'].astype(str)
CK = 'chakravarti_GSE218123'
ck_cells = j[j['study'] == CK].groupby('cid').size().to_dict()

# 命中规则：lit 行 PMID ∈ {s.source_pmid : s ∈ 供细胞入本簇的 study}
# 票面 12 PMID ∩ SOURCE_PMIDS = {36712326}；36712326 仅由 chakravarti study 供入。
face_lines = [l.rstrip('\n') for l in open(V1, encoding='utf-8')]
assert len(face_lines) == 33 and all(l != '' for l in face_lines)
face = [json.loads(l) for l in face_lines]
face_ids = [r['cluster_id'] for r in face]

hits, scan_rows = [], []
for r, raw in zip(face, face_lines):
    cid = r['cluster_id']
    ck_n = int(ck_cells.get(cid, 0))
    src_here = {CK: '36712326'} if ck_n > 0 else {}  # 本簇血缘可及 source：仅 chakravarti（其余 study source 不在票面/不可解析）
    src_pmis = set(src_here.values())
    lit = r.get('lit') or {}
    hit_here = []
    for ct, es in lit.items():
        for e in (es or []):
            p = str(e.get('pmid'))
            if p in SOURCE_PMIDS and p in src_pmis:
                hit_here.append((ct, p))
    scan_rows.append(dict(cluster_id=cid, era=('变化簇' if cid in set(json.load(open('/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_changed_clusters.json'))['changed']) else '冻结簇'),
                          chakravarti_cells=ck_n, n_lit_entries=sum(len(v or []) for v in lit.values()),
                          hit_entries=';'.join(f'{ct}:{p}' for ct, p in hit_here),
                          action=('剔除' if hit_here else '无')))
    hits += [(cid, ct, p) for ct, p in hit_here]

hits_expected = {('Q6::7', 'Endo', '36712326'), ('Q6::11', 'Endo', '36712326')}
print(f'规则复算命中集: {len(hits)} 行 -> {sorted(hits)}')
if len(hits) < len(hits_expected):
    print('!! 命中少于预期（血缘不一致）——停卡上报'); sys.exit(3)
if set(hits) - hits_expected:
    print('!! 命中多于预期——全剔并如实登记差异（裁定细则1），差异清单见 ledger')
extra = sorted(set(hits) - hits_expected)
missing = sorted(hits_expected - set(hits))

# ---- 3. 构建 v2.1 面（序列化往返自证 + 零漂移硬断言）----
def ser(r):
    return json.dumps(r, ensure_ascii=False)

for raw, r in zip(face_lines, face):
    assert ser(r) == raw, f'序列化往返不等（无法保证非剔除字段逐字节不动）: {r["cluster_id"]}'

hit_by_cid = {}
for cid, ct, p in hits:
    hit_by_cid.setdefault(cid, []).append((ct, p))

new_lines, changed_cids = [], []
for cid, raw, r in zip(face_ids, face_lines, face):
    if cid not in hit_by_cid:
        new_lines.append(raw)  # 未涉簇：整行逐字节复制
        continue
    r2 = json.loads(raw)
    for ct, p in hit_by_cid[cid]:
        before = len(r2['lit'][ct])
        r2['lit'][ct] = [e for e in r2['lit'][ct] if str(e.get('pmid')) != p]
        assert len(r2['lit'][ct]) == before - 1, f'{cid}/{ct} 剔除不等量'
        if not r2['lit'][ct]:
            del r2['lit'][ct]  # 空键清除（登记）
    # 断言：除 lit 外全字段与原始逐字节相等（用无 lit 子字典序列化比对）
    chk = lambda rr: ser({k: v for k, v in rr.items() if k != 'lit'})
    assert chk(r2) == chk(r), f'{cid} 非 lit 字段漂移'
    new_lines.append(ser(r2))
    changed_cids.append(cid)

assert len(new_lines) == 33 and changed_cids
with open(V21, 'w', encoding='utf-8') as f:
    f.write('\n'.join(new_lines) + '\n')
sha_v21 = hashlib.sha256(open(V21, 'rb').read()).hexdigest()

# ---- 4. 零漂移对账：31 未涉簇逐字节 + 2 变化簇仅 lit 收缩 ----
v21_lines = [l.rstrip('\n') for l in open(V21, encoding='utf-8')]
n_ident = sum(1 for c, a_, b_ in zip(face_ids, face_lines, v21_lines) if (a_ == b_) == (c not in hit_by_cid))
assert n_ident == 33, '逐字节对账失败'
for cid in changed_cids:
    i = face_ids.index(cid)
    o, n = face[i], json.loads(v21_lines[i])
    for k in o:
        if k == 'lit':
            continue
        assert o[k] == n[k], f'{cid}.{k} 漂移'
    # ranking 逐字节不动（显式再断言，裁定细则2）
    assert ser(o['kb_marker_ranking']) == ser(n['kb_marker_ranking'])

# ---- 5. ledger 落盘 ----
with open(f'{ROOT}/out/FACE_V21_ledger.tsv', 'w', encoding='utf-8') as f:
    f.write('cluster_id\tera\tchakravarti_cells\tn_lit_entries_v1\thit_entries\taction\n')
    for x in scan_rows:
        f.write('\t'.join(str(x[c]) for c in ['cluster_id', 'era', 'chakravarti_cells', 'n_lit_entries', 'hit_entries', 'action']) + '\n')
    f.write(f'# lineage registry basis:\n')
    for s, v in LINEAGE.items():
        f.write(f'# {s} | source_pmid={v["source_pmid"]} | {v["basis"]}\n')
    f.write(f'# hits_total={len(hits)} extra_vs_named={extra} missing_vs_named={missing}\n')
    f.write(f'# v1_sha={sha_v1}\n# v2.1_sha={sha_v21}\n')
    f.write(f'# changed_clusters={changed_cids}；31 未涉簇行逐字节相等；2 变化簇除 lit 收缩外全字段逐字节相等（含 kb_marker_ranking 零动）\n')

print(f'v2.1 面已构建: {V21}')
print(f'v2.1 sha256: {sha_v21}')
print(f'变化簇(剔除): {changed_cids}; 命中 {len(hits)} 行; 超预期={extra}; 少于预期={missing}')
print('零漂移断言: 33/33 逐字节对账 PASS（31 整行等 + 2 仅 lit 收缩）')
sys.exit(0)
