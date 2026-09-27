#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""E2 共享层：ON 态面板复刻（不 import 生产码，按 eyekb_core.py 现行文本逻辑复刻）
+ 基因级证据抽取（e2_decon_rules.json 判据）+ keep 规则 + E1 同口径打分原语。
本模块只读 kb/markers/*.json；判据先于跑数冻结于 e2_decon_rules.json (sha 34928582)。"""
import json, re

ROOT = '/mnt/D/EyeKB/plans/e2_decontam_20260926'
MD = '/mnt/D/EyeKB/kb/markers'
EV = '/mnt/D/EyeKB/plans/evalset'
R1 = '/mnt/D/EyeKB/plans/evidence_scoring_20260926'

LIBS_ON = ['retina', 'membrane', 'retina_interneuron', 'retina_v6', 'face_v6']
LIB_PATH = {
    'retina': f'{MD}/markers_v4.1_clean.json',
    'membrane': f'{MD}/markers_membrane_v1.json',
    'retina_interneuron': f'{MD}/markers_v5_retina_interneuron.json',
    'retina_v6': f'{MD}/markers_v6_retina_repair.json',
    'face_v6': f'{MD}/markers_v6_face_increment.json',
}
RET_LIBS = ('retina', 'retina_interneuron', 'retina_v6')
AXIS_HRCA = {'Q3', 'Q4', 'Q5b'}
AXIS_FACE = {'Q6'}
B_AXIS_RETINA = {'41578023'}  # HRCA 本体论文（视网膜系面板行的派生源）
LINEAGE = json.load(open(f'{R1}/e1_leak_lineage.json'))
BSRC = {m: set(v.get('source_pmids') or []) for m, v in LINEAGE['members'].items()}
CMAP = json.load(open(f'{R1}/e1_class_map.json'))
MEMBERS = list(BSRC.keys())

PM_RE = re.compile(r'PMID[:：]?\s*(\d{5,8})')

def _gene_level_recs(recs):
    """剔除 pmid_context（类级语境语义，非该基因逐条引用）后的记录文本。"""
    return [r for r in recs if isinstance(r, dict) and str(r.get('type')) != 'pmid_context']

def _pmids(recs):
    out = set()
    for r in _gene_level_recs(recs):
        for p in PM_RE.findall(json.dumps(r, ensure_ascii=False)):
            out.add(p)
    return out

def _has_pcx_ext(recs):
    return any(isinstance(r, dict) and r.get('type') == 'pmid_context'
               and int(r.get('n_hits') or 0) > 0 for r in recs)

def load_panel():
    """复刻 eyekb_core._load_marker_dbs + query_marker 行注册（首注者正名，同名成 lib::类 别名）。"""
    dbs = []
    for n in LIBS_ON:
        db = json.load(open(LIB_PATH[n], encoding='utf-8'))
        if n == 'face_v6' and 'markers' not in db:
            derived = {}
            for src in ('stromal_repair', 'face_increment'):  # 固定序；平票行序差异在验收容差内登记
                for cls, e in (db.get(src) or {}).items():
                    derived[cls] = [str(x.get('gene', '')).strip().upper()
                                    for x in (e.get('core') or [])
                                    if isinstance(x, dict) and x.get('gene')]
            db = dict(db)
            db['markers'] = derived
        dbs.append((n, db))
    rows, seen = [], {}
    for name, db in dbs:
        for ct, gs in (db.get('markers') or {}).items():
            up = ct.upper()
            key = f'{name}::{ct}' if up in seen else ct
            rows.append({'key': key, 'lib': name, 'cls': ct, 'genes': [g.upper() for g in gs]})
            seen.setdefault(up, ct)
    return rows, dbs

_P04 = None
def v41_p04_sets(dbs):
    global _P04
    if _P04 is None:
        d = dict(dbs)['retina']
        mm = set((d.get('micro_detail') or {}).get('final_markers') or [])
        rr = set((d.get('rpe_detail') or {}).get('final_markers') or [])
        warn = []
        for cls, s in (('Micro', mm), ('RPE', rr)):
            flat = set((d.get('markers') or {}).get(cls) or [])
            if flat != s:
                warn.append(f'v4.1 {cls} flat!=final_markers: flat={sorted(flat)} fin={sorted(s)}')
        _P04 = (mm, rr, warn)
    return _P04

def _p04_hit(dbs, cls, gene):
    mm, rr, _ = v41_p04_sets(dbs)
    return (cls == 'Micro' and gene in mm) or (cls == 'RPE' and gene in rr)

def gene_evidence(dbs, lib, cls, gene):
    """→ dict(S=set, axis=set, p04=bool, pcx=bool)；判据 = e2_decon_rules.json 冻结文本。"""
    d = dict(dbs)[lib]
    S = set()
    hrca = mem = face = p04 = pcx = False
    if lib == 'retina':
        if _p04_hit(dbs, cls, gene):
            hrca, p04 = True, True
    elif lib == 'membrane':
        recs = ((d.get('provenance') or {}).get(cls) or {}).get(gene) or []
        S = _pmids(recs)
        txt = json.dumps(_gene_level_recs(recs), ensure_ascii=False)
        if re.search(r'"id":\s*"GSE165784', txt) or 'membrane v1 携带' in txt:
            mem = True
        if 'HRCA' in txt:
            hrca = True
    elif lib == 'retina_interneuron':
        recs = ((d.get('provenance') or {}).get(cls) or {}).get(gene)
        if recs is not None:
            S = _pmids(recs)
            txt = json.dumps(_gene_level_recs(recs), ensure_ascii=False)
            if re.search(r'HRCA_D001|kb5v2_gate|HRCA', txt):
                hrca = True
            pcx = _has_pcx_ext(recs)
        elif _p04_hit(dbs, cls, gene):
            hrca, p04 = True, True  # v5 全量继承 v4.1（含 P0.4 数据驱动行）
    elif lib == 'retina_v6':
        blocks = {x.get('gene'): x for x in ((d.get('marker_blocks') or {}).get(cls) or [])
                  if isinstance(x, dict)}
        mg = {x.get('gene'): x for x in ((d.get('microglia_repair') or {}).get('core') or [])
              if isinstance(x, dict)}
        rec = blocks.get(gene) or (mg.get(gene) if cls == 'Micro' else None)
        if rec:
            evs = rec.get('evidence') or []
            S = _pmids(evs)
            txt = json.dumps(_gene_level_recs(evs), ensure_ascii=False)
            if 'membrane v1 携带' in txt:
                mem = True  # 携带自 membrane（派生 GSE165784=Q9 非真值）→ 撤轴
            elif (rec.get('stats_frozen') is not None
                  or re.search(r'REVCAND|KB6 v[12] 判级|kb5v3', txt)):
                hrca = True
            pcx = _has_pcx_ext(evs)
        elif _p04_hit(dbs, cls, gene):
            hrca, p04 = True, True  # 未覆盖行 = v4.1 继承
    elif lib == 'face_v6':
        rec = None
        for src in ('stromal_repair', 'face_increment'):
            for x in ((d.get(src) or {}).get(cls) or {}).get('core') or []:
                if isinstance(x, dict) and str(x.get('gene', '')).upper() == gene:
                    rec = x
        if rec:
            evs = rec.get('evidence') or []
            S = _pmids(evs)
            txt = json.dumps(_gene_level_recs(evs), ensure_ascii=False)
            if 'membrane v1 携带' in txt or re.search(r'"id":\s*"GSE165784', txt):
                mem = True
            elif re.search(r'kb6b|kb7_w2|REVCAND_KB6b', txt):
                face = True
            if re.search(r'HRCA_D001|kb5v2_gate', txt):
                hrca = True  # face 库禁现 HRCA 门；出现即入轴并集（异常将在矩阵表可见）
    axis = set()
    if not mem:
        if hrca:
            axis |= AXIS_HRCA
        if face:
            axis |= AXIS_FACE
    return {'S': S, 'axis': axis, 'p04': p04, 'pcx': pcx,
            'hrca': hrca, 'mem': mem, 'face': face}

def keep(gene_ev, lib, m, variant='S1'):
    """主规则与敏感性变体（e2_decon_rules.json keep_rule / sens_variants 直译）。"""
    S, axis = set(gene_ev['S']), gene_ev['axis']
    if variant == 'S4' and gene_ev['p04']:
        axis = axis - AXIS_HRCA
    if variant == 'S5' and gene_ev['pcx'] and not S:
        S = {'PCX_SENTINEL'}
    bsrc = BSRC.get(m, set())
    if variant == 'S2':
        return bool(S - bsrc)
    if m in axis:
        b = bsrc | (B_AXIS_RETINA if lib in RET_LIBS else set())
        return bool(S - b)
    if S:
        return bool(S - bsrc)
    return True

def canon(c):
    return c.split('::')[-1] if '::' in c else c

def load_digest_rows():
    return [json.loads(l) for l in open(f'{EV}/digest/EV_DIGEST_SLIM_v3full.jsonl')]

def top10_of(r):
    genes = r.get('top_genes') or []
    syms = r.get('top_genes_sym') or []
    return [str(s or g).strip().upper() for g, s in zip(genes, syms)][:10]

def lit_of_cluster(r):
    litm = {}
    for k, ents in (r.get('lit') or {}).items():
        c = canon(k)
        pms = set()
        for e in ents or []:
            pm = str(e.get('pmid') or '').strip()
            if pm and pm.lower() != 'none':
                pms.add(pm)
        litm[c] = litm.get(c, set()) | pms
    return litm

def merged_cluster(top, rows, keepset, m, decontam_lit=False):
    """一簇的 canon max 合并（E1 collect 同规则：严格大者替换，平票保先序）；
    keepset: row_key -> set(kept_genes) 或 None(raw)；decontam_lit: lit 剔除源 PMID。"""
    merged = {}
    for row in rows:
        gl = row['genes'] if keepset is None else sorted(keepset[row['key']])
        gs = [g for g in top if g in set(gl)]
        n = len(gs)
        if n == 0:
            continue
        c = canon(row['key'])
        if c not in merged or n > merged[c]['n']:
            merged[c] = {'n': n, 'shared_genes': gs, 'alias': [row['key']]}
        else:
            merged[c]['alias'].append(row['key'])
    for c, d in merged.items():
        pm = merged[c]
        pass  # lit 注接入下（保持行序 = 排名序）
    return merged

def attach_lit(merged, raw_lit, m, decontam):
    bsrc = BSRC.get(m, set())
    for c, pm in raw_lit.items():
        if c not in merged and pm:
            merged[c] = {'n': 0, 'shared_genes': [], 'alias': [c]}
    for c, d in merged.items():
        pm = raw_lit.get(c, set())
        d['lit_n_raw'] = len(pm)
        d['lit_pm_raw'] = sorted(pm)
        if decontam:
            pm2 = pm - bsrc
        else:
            pm2 = pm
        d['lit_n'] = len(pm2)
        d['lit_pm'] = sorted(pm2)

def sorted_rows(merged):
    return sorted(merged.items(), key=lambda kv: (-kv[1]['n'], kv[0]))
