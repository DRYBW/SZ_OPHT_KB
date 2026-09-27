#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K4: 通用共享基因屏蔽表（PREREG §1.3 R1/R2/R3 定案版——对称规则）。
truth 折叠域: 冻结件 work_t_d1ca11b0/KB_Q6_crosswalk.tsv + KB9 扩展（逐行注 provenance）。
规则: 类 c 折叠到 truth 类集 F(c)；基因 g∈core(c) 若属于任一 truth 类 T'∉F(c) 的 top60 → g 对 c 在眼表证据装配的 n_shared 贡献记 0。
输出 out/kb9_shared_gene_shield.tsv (逐类逐基因 blocked/kept) + out/kb9_face_effective_genesets.json
"""
import json, pandas as pd

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
ensg = json.load(open('/home/ubuntu/rp_project/m3/s2/ensg_symbol_map.json'))

# truth top60 (KB 无关口径)
mk = pd.read_csv(f'{EV}/work_t_d1ca11b0/author_class_markers_data.tsv', sep='\t')
TRUTH = {}
for _, r in mk.iterrows():
    syms = {ensg.get(str(x), str(x)) for x in str(r['top60_markers']).split(',')}
    TRUTH[r['truth_super']] = {s for s in syms if s}

# ---- 类集合装配: 复刻 _load_marker_dbs ON 态 (retina/membrane/v5/retina_v6/face_v6) + KB9 build ----
import sys
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
import eyekb_core as C
dbs = C._load_marker_dbs('all')
CLS = {}
owner = {}
# 复刻消歧 (与 query_marker 同): 同名后到者 "lib::class"
seen = {}
CLS2, owner2 = {}, {}
for name, path, db in dbs:
    for ct, gs in db.get('markers', {}).items():
        up = ct.upper()
        if up in seen:
            alt = f"{name}::{ct}"
            CLS2[alt] = [g.upper() for g in gs]; owner2[alt] = str(path)
            continue
        seen[up] = ct
        CLS2[ct] = [g.upper() for g in gs]; owner2[ct] = str(path)
CLS, owner = CLS2, owner2

# KB9 新条 (build, 未注册)
K9 = json.load(open(f'{ROOT}/build/markers_k9_ocs_increment.json'))
for src in ('new_terms',):
    for cls, e in (K9.get(src) or {}).items():
        CLS[cls] = [x['gene'].upper() for x in e.get('core', []) if x.get('gene')]
        owner[cls] = f"{ROOT}/build/markers_k9_ocs_increment.json"

RETINA_ONLY_FILES = {'markers_v4.1_clean.json', 'markers_v5_retina_interneuron.json', 'markers_v6_retina_repair.json'}

# ---- 折叠映射: 冻结 crosswalk + KB9 扩展 ----
cw = pd.read_csv(f'{EV}/work_t_d1ca11b0/KB_Q6_crosswalk.tsv', sep='\t')
FOLD, FOLDPROV = {}, {}
for _, r in cw.iterrows():
    if pd.notna(r['q6_vocab_class']) and str(r['q6_vocab_class']).strip():
        FOLD[r['kb_name']] = set(str(r['q6_vocab_class']).split('|'))
        FOLDPROV[r['kb_name']] = f'frozen_crosswalk:{r["provenance"]}'
    else:
        FOLD[r['kb_name']] = set()
        FOLDPROV[r['kb_name']] = f'frozen_crosswalk:{r["provenance"]}'
EXT = {
    'Endo': ({'Endothelium'}, 'KB9_ext:KB 缩写=endothelial cell=super_map 叶'),
    'Endo_Patho': ({'Endothelium'}, 'KB9_ext:血管内皮病理态'),
    'Microglia': ({'Immune Cells'}, 'KB9_ext:小胶质=免疫叶'),
    'Mac_Tissue': ({'Immune Cells'}, 'KB9_ext:组织巨噬'),
    'Corneal Endothelium': ({'Corneal Endothelium'}, 'KB9_ext:名=truth 名'),
    'Granulocyte': ({'Immune Cells'}, 'KB9_ext'), 'cDC1': ({'Immune Cells'}, 'KB9_ext'), 'cDC2': ({'Immune Cells'}, 'KB9_ext'),
    'face_v6::Keratocytes': ({'Fibroblasts'}, 'KB9_ext:keratocyte 叶∈Fibroblasts'),
    'face_v6::Fibroblast': ({'Fibroblasts'}, 'KB9_ext'),
    'face_v6::Pericyte': ({'Pericytes'}, 'KB9_ext'),
    'face_v6::SMC': ({'Smooth Muscle Cells'}, 'KB9_ext'),
    'face_v6::Myofibroblast': ({'Fibroblasts', 'Smooth Muscle Cells'}, 'KB9_ext:ambiguous 照原链'),
    'Conj_epithelium_basal': ({'Epithelium'}, 'KB9_ext'),
    'Conj_epithelium_superficial': ({'Epithelium'}, 'KB9_ext'),
    'Melanocyte': ({'Melanocytes'}, 'KB9_new:CL:0000148'),
    'Schwann': ({'Schwann Cells'}, 'KB9_new:CL:0002573'),
    'Conj_epithelium_suprabasal': ({'Epithelium'}, 'KB9_new:CL:1000432 借父条+layer'),
    'Limbus_Sclera_fibroblast_C1': ({'Fibroblasts'}, 'KB9_new:CL:0000057'),
    'Proliferating': (set(), 'KB9_ext:状态类不折叠(不参与屏蔽)'),
    'Mast': ({'Immune Cells'}, 'x'),
}
for k, (fs, pv) in EXT.items():
    if k in CLS and not FOLD.get(k):
        FOLD[k] = fs; FOLDPROV[k] = pv

rows = []
eff = {}
for cls, gs in CLS.items():
    ffile = owner[cls].split('/')[-1]
    if ffile in RETINA_ONLY_FILES:
        rows.append([cls, '*', 'R1_drop_retina_specific', '', '', ''])
        continue
    fold = FOLD.get(cls)
    if fold is None:
        fold = set()
        FOLDPROV[cls] = 'UNMAPPED:不参与屏蔽(如实登记)'
    kept, blocked = [], []
    for g in gs:
        offenders = sorted([t for t in TRUTH if t not in fold and g in TRUTH[t]])
        if fold and offenders:
            blocked.append((g, offenders))
        else:
            kept.append(g)
    eff[cls] = {'truth_fold': sorted(fold) if fold else 'UNMAPPED',
                'fold_provenance': FOLDPROV.get(cls, ''),
                'face_effective_genes': kept,
                'blocked': [{'gene': g, 'in_top60_of': o} for g, o in blocked]}
    for g, o in blocked:
        rows.append([cls, g, 'R2R3_shield_block', '|'.join(sorted(fold)) or 'UNMAPPED', ','.join(o), ''])
    for g in kept:
        rows.append([cls, g, 'kept', '|'.join(sorted(fold)) or 'UNMAPPED', '', ''])

pd.DataFrame(rows, columns=['class', 'gene', 'action', 'truth_fold', 'blocked_in_truths', 'note']).to_csv(f'{ROOT}/out/kb9_shared_gene_shield.tsv', sep='\t', index=False)
json.dump(eff, open(f'{ROOT}/out/kb9_face_effective_genesets.json', 'w'), ensure_ascii=False, indent=1)
for cls in sorted(eff):
    e = eff[cls]
    if e['blocked']:
        print(f"{cls:32s} fold={e['truth_fold']} kept={e['face_effective_genes']} BLOCKED={[(b['gene'], b['in_top60_of']) for b in e['blocked']]}")
print('---- new terms ----')
for cls in ['Melanocyte', 'Schwann', 'Conj_epithelium_suprabasal', 'Limbus_Sclera_fibroblast_C1']:
    if cls in eff:
        e = eff[cls]
        print(cls, 'kept:', e['face_effective_genes'], '| blocked:', [(b['gene'], b['in_top60_of']) for b in e['blocked']])
