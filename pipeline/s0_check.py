#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""S0 sample pre-check layer (species x tissue automatic decision + hard-gate abstention) — WIRE-P1 wired version.

Origin and lineage
    Logic ported verbatim from plans/s0_probe_20260930/scripts/s0_probe.py (S0PROBE smoke
    prototype, t_7d4e404f, 2026-09-30). Three evidence channels = A gene-ID composition /
    B symbol conventions + marker cross-hits (case-insensitive + official orthologs) /
    C baselines composition scoring; all six hard gates default ON.
    Porting discipline: zero numeric-semantics changes — for the same pb.csv input, the output
    of this module and of the prototype script must be field-by-field identical (the G2 gate
    reconciles via verdict_table.csv).

Environment differences vs the prototype (paths only, no algorithm differences)
    - Assets: in-repo pipeline/assets/s0/species_assets.pkl (pre-baked, zero network at runtime).
    - Dictionaries: in-repo kb/markers, kb/baselines, kb/priors/composition
      (the only difference of markers_k9_ocs_increment.json from the production disk = the
      registration_provenance metadata field; panel content is class-by-class identical,
      sha cross-check records in plans/wire_p1_20260930/logs/).

Hard constraints (architecture-review ruling astra_review/ROUTER_V0_ASTRa_R1.md + REV-1 decision, T6 firewall hardwired)
    - This module is a review-side surface: reading any natural-language text under this repo's
      kb/known_issues/ or pipeline/pitfalls/ is forbidden. No pitfall-page read path may appear
      in this module; grep of this file + the module's runtime inputs/outputs = zero pitfall
      wording (G4 machine check).
    - Failed gate -> abstain=True recorded in the readings. The wiring side (run_pipeline.py)
      Phase-1 = shadow: abstain does not block the run, it only writes s0_gate_report.json +
      REPORT_ABSTAIN.md (human-readable record); the blocking hard gate = Phase 3 (switched via
      EYEKB_S0_ENFORCE=1, off by default this batch). The overall rollback switch
      EYEKB_S0_GATE=0 is consumed by run_pipeline; this module contains no switch logic itself
      (scoring engine decoupled from rollback semantics).

Usage (standalone smoke, same CLI shape as the prototype):
    python pipeline/s0_check.py <pb.csv> [--name X] [--out outdir] [--thr-json t.json]
"""
from __future__ import annotations

import json
import os
import pickle
import re
import sys
from pathlib import Path

import numpy as np
import pandas as pd

HERE = Path(__file__).resolve().parent
REPO_ROOT = HERE.parent
ASSETS = str(HERE / "assets" / "s0" / "species_assets.pkl")
KBM = str(REPO_ROOT / "kb" / "markers")
KBB = str(REPO_ROOT / "kb" / "baselines")
KBP = str(REPO_ROOT / "kb" / "priors" / "composition")

# ---------- Thresholds (verbatim values from the prototype; all "pending calibration", override via --thr-json for sensitivity sweeps) ----------
THR = {
    'id_decisive_frac': 0.80,     # ENSG (or ENSMUSG) share >= this value decides species (ID-path conclusive)
    'id_mixed_frac': 0.05,        # both ENS prefixes >= this value at once -> conflict
    'sp_margin': 0.15,            # symbol path: human-mouse score-difference lower bound
    'sp_floor': 0.20,             # symbol path: minimum score on either side
    'tissue_gap': 0.10,           # tissue top1-top2 relative score-gap lower bound
    'tissue_domain_floor': 0.0,   # all contrast scores negative -> out-of-domain tissue
    'tissue_sim_floor': 0.25,     # composition-cosine similarity max < this value -> out-of-domain tissue (pending calibration)
    'min_genes_detected': 1000,   # genes-detected lower bound (depth gate)
    'min_total_counts': 5000,     # pseudobulk total-count lower bound
    'fetal_ratio': 1.0,           # fetal contrast score >= adult-retina contrast score x this ratio -> suspected fetal
}

RE_H = re.compile(r'^ENSG\d{11}$')
RE_M = re.compile(r'^ENSMUSG\d{11}$')
RE_R = re.compile(r'^ENSRNOG\d{11}$')
RE_E = re.compile(r'^ENS[A-Z]+G\d+$')

# Panel name -> in-repo tissue dictionary name (run_pipeline.known_tissues()); names not in the table are handled by stripping the species prefix
TISSUE_TO_DICT = {
    'human_pdr_membrane': 'fibrovascular_membrane',
}


# ---------- Marker panels: kb-sourced + prototype hand-picked completion (kb_origin flag distinguishes) ----------
def load_markers():
    mk = {}
    kb = {}
    d = json.load(open(f'{KBM}/markers_v4.1_clean.json'))
    for c, gs in d['markers'].items():
        mk[c] = list(gs); kb[c] = True
    d = json.load(open(f'{KBM}/markers_membrane_v1.json'))
    for c, gs in d['markers'].items():
        mk[c] = list(gs); kb[c] = True
    try:
        d = json.load(open(f'{KBM}/markers_k9_ocs_increment.json'))
        for c, v in (d.get('markers') or {}).items():
            gs = v if isinstance(v, list) else v.get('markers', [])
            if gs: mk[c] = list(gs); kb[c] = True
    except Exception:
        pass
    # hand-picked canonicals (panel classes the kb lacks; prototype use only, annotated in the report)
    picked = {
        'Oligodendrocyte': ['MBP', 'MOG', 'MOBP', 'PLP1', 'MAL', 'CNP'],
        'OPC': ['PDGFRA', 'CSPG4', 'CXCR4', 'DCX?', 'SOX10', 'TCN2'],
        'Adipocyte': ['ADIPOQ', 'PLIN1', 'LEP', 'CFD', 'FABP4'],
        'Mast_cell': ['TPSAB1', 'CPA3', 'MS4A2', 'HDC'],
        'Dendritic': ['FLT3', 'CD1C', 'ZBTB46', 'CST3', 'CLEC10A'],
        'T_cell': ['CD3D', 'CD3E', 'IL7R', 'TRAC', 'CD2'],
        'Epithelium_generic': ['EPCAM', 'KRT8', 'KRT18', 'KRT19', 'CDH1'],
        'PCE_pigmented': ['TYR', 'TYRP1', 'DCT', 'PMEL', 'MLANA'],
        'NPCE': ['AQP1', 'CLIC6', 'OTX2', 'PRPH', 'SPP1'],
        'Immune_generic': ['PTPRC', 'CD14', 'LYZ', 'CSF1R', 'ITGAM'],
        'PR_contam': ['RHO', 'GNAT1', 'NR2E3'],
        'Erythroid': ['HBB', 'HBA1', 'HBA2', 'HBD', 'ALAS2'],
        'PRPC_fetal': ['CRX', 'RCVRN', 'NRL', 'PROM1', 'VSX2'],
        'NRPC_fetal': ['LIN28A', 'IGF2', 'HMGA2', 'HES5', 'SOX2', 'NES', 'TOP2A'],
        'Neuron_generic': ['SNAP25', 'STMN2', 'TUBB3', 'RBFOX3'],
    }
    for c, gs in picked.items():
        if c not in mk:
            mk[c] = [g for g in gs if not g.endswith('?')]; kb[c] = False
    return mk, kb


def load_tissue_panels():
    """(tissue_name, species_scope, weights dict class->pct, stage) from baselines+priors"""
    panels = []
    alias = {
        'Astrocyte': 'Astro', 'Microglia': 'Micro', 'Endothelium': 'Endo',
        'Endothelial_cell': 'Endo', 'Fibroblasts': 'Fibroblast',
        'Immune Cell': 'Immune_generic', 'Immune Cells': 'Immune_generic',
        'Melanocyte': 'PCE_pigmented', 'Melanocytes': 'PCE_pigmented',
        'Pigmented_cell': 'PCE_pigmented', 'Ciliary_Muscle': 'SMC',
        'Smooth Muscle Cells': 'SMC', 'Mural_cell': 'Pericyte',
        'Schwann Cell': 'Schwann', 'Schwann_cell': 'Schwann',
        'T_cell': 'T_cell', 'B_cell': 'B', 'NK_cell': 'NK',
        'Macrophage': 'Mac_Tissue', 'PR-associated': 'PR_contam',
        'neuron-like': 'Neuron_generic', 'myeloid': 'Immune_generic',
        'erythroid': 'Erythroid', 'Oligodendrocyte': 'Oligodendrocyte',
        'Oligodendrocyte_precursor_cell': 'OPC', 'Adipocyte': 'Adipocyte',
        'Mast_cell': 'Mast_cell', 'Dendritic_cell': 'Dendritic',
        'Epithelium': 'Epithelium_generic', 'Corneal Endothelium': 'Corneal Endothelium',
        'Keratocytes': 'Keratocytes', 'Fibroblast': 'Fibroblast',
        'PRPC': 'PRPC_fetal', 'NRPC': 'NRPC_fetal',
        'Pericyte': 'Pericyte', 'Pericytes': 'Pericyte',
        'MG': 'MG', 'Micro': 'Micro',
        # PDR-membrane prior compartment names -> marker classes
        'endothelial': 'Endo', 'glial_candidate': 'MG', 'lymphoid_T': 'T_cell',
        'lymphoid_plasma': 'Plasma', 'myeloid': 'Mac_Tissue',
        'proliferating': 'Proliferating', 'stromal_myofibro': 'Myofibroblast',
        'stromal_pericyte': 'Pericyte',
    }
    def add(name, comp, stage='adult'):
        w = {}
        for c, pct in comp.items():
            if not isinstance(pct, (int, float)): continue
            key = alias.get(c, c)
            w[key] = w.get(key, 0) + pct
        panels.append(dict(name=name, weights=w, stage=stage))
    for f, nm, stg in [('retina.json', 'human_retina', 'adult'),
                       ('RPE.json', 'human_RPE', 'adult'),
                       ('ciliary_body.json', 'human_ciliary_body', 'adult'),
                       ('trabecular_meshwork.json', 'human_trabecular_meshwork', 'adult'),
                       ('optic_nerve.json', 'human_optic_nerve', 'adult'),
                       ('ocular_surface.json', 'human_ocular_surface', 'adult'),
                       ('retina__fetal_developing.json', 'human_retina_fetal', 'fetal')]:
        d = json.load(open(f'{KBB}/{f}'))
        comp = d.get('pooled_adult_only_main') or d.get('pooled_all_cells')
        if comp is None and nm == 'human_retina_fetal':
            comp = (d.get('portal_majorclass_reference') or {}).get('pct')
        if comp: add(nm, comp, stg)
    d = json.load(open(f'{KBP}/human_pdr_membrane.json'))
    comp = (d.get('_computed') or {}).get('comp_pdr')
    if comp:
        add('human_pdr_membrane', {k: (v[1] if isinstance(v, list) else v) for k, v in comp.items()})
    return panels


# ---------- Evidence A: ID composition ----------
def id_evidence(gene_ids):
    n = len(gene_ids)
    if n == 0:
        return dict(path='empty', frac_h=0, frac_m=0, frac_r=0, frac_ens_other=0,
                    frac_symbol=0, call='none')
    hh = mm = rr = eo = sym = 0
    for g in gene_ids:
        if RE_H.match(g): hh += 1
        elif RE_M.match(g): mm += 1
        elif RE_R.match(g): rr += 1
        elif RE_E.match(g): eo += 1
        else: sym += 1
    f = dict(frac_h=hh / n, frac_m=mm / n, frac_r=rr / n, frac_ens_other=eo / n,
             frac_symbol=sym / n)
    if f['frac_h'] >= THR['id_decisive_frac'] and f['frac_m'] < THR['id_mixed_frac']:
        call = 'human'
    elif f['frac_m'] >= THR['id_decisive_frac'] and f['frac_h'] < THR['id_mixed_frac']:
        call = 'mouse'
    elif f['frac_h'] >= THR['id_mixed_frac'] and f['frac_m'] >= THR['id_mixed_frac']:
        call = 'mixed_conflict'
    elif f['frac_r'] >= THR['id_decisive_frac']:
        call = 'rat_out_of_domain'
    elif f['frac_ens_other'] >= 0.5:
        call = 'nonhumanmouse_ens_out_of_domain' if f['frac_h'] < 0.5 else 'human'
    else:
        call = 'none'   # symbol data; the ID path carries no decision power
    f['call'] = call
    f['path'] = 'id'
    return f


# ---------- Evidence B: symbol conventions + marker cross-hits (case-insensitive + official orthologs) ----------
def symbol_evidence(symbols, assets, human_panel):
    S = [s for s in symbols if s and s not in ('NA', '-', '--')]
    if not S:
        return dict(path='none', score_h=0, score_m=0, call='none')
    Su = {s.upper() for s in S}
    hs = assets.get('human_main', assets['human_symbols'])
    ms = assets.get('mouse_main', assets['mouse_symbols'])
    Hu_upper = {x.upper() for x in hs}
    Mu_upper = {x.upper() for x in ms}
    # universe hits: case-sensitive (the convention signal itself) + case-insensitive (B5 floor sanity)
    cs_h = sum(1 for s in S if s in hs) / len(S)
    cs_m = sum(1 for s in S if s in ms) / len(S)
    ci_h = sum(1 for s in Su if s in Hu_upper) / len(Su)
    ci_m = sum(1 for s in Su if s in Mu_upper) / len(Su)
    # human-panel cross-hits: the human panel (original symbols) and the mouse panel (ortholog-mapped native case) each get cs/ci hit rates
    P_h = set(human_panel)
    global _PM_CACHE
    try:
        P_m = _PM_CACHE
    except NameError:
        P_m = set()
        rev = {}
        for e, syms in assets['h2m_symbols'].items():
            h = assets['hensg2sym'].get(e, '').upper()
            if h:
                rev.setdefault(h, set()).update(syms)
        _PM_CACHE = {g: rev.get(g.upper(), set()) for g in P_h}
    P_m = {m for g in P_h for m in _PM_CACHE.get(g, set())}
    cs_h_panel = len({s for s in S if s in P_h}) / max(1, len(P_h))
    cs_m_panel = len({s for s in S if s in P_m}) / max(1, len(P_m))
    ci_h_panel = len({s.upper() for s in S} & {s.upper() for s in P_h}) / max(1, len(P_h))
    ci_m_panel = len({s.upper() for s in S} & {s.upper() for s in P_m}) / max(1, len(P_m))
    # MT convention: human MT-CO1 vs mouse mt-Co1
    mt_h = sum(1 for s in S if s.startswith('MT-'))
    mt_m = sum(1 for s in S if s.lower().startswith('mt-') and not s.startswith('MT-'))
    mt_sig = 0.5 if mt_h > mt_m else (-0.5 if mt_m > mt_h else 0)
    # composite: half universe-cs delta + half panel-cs delta, plus the MT-convention term
    score_h = 0.5 * cs_h + 0.5 * cs_h_panel + (mt_sig if mt_sig > 0 else 0)
    score_m = 0.5 * cs_m + 0.5 * cs_m_panel + (-mt_sig if mt_sig < 0 else 0)
    return dict(path='symbol', score_h=round(score_h, 4), score_m=round(score_m, 4),
                cs_h_univ=round(cs_h, 4), cs_m_univ=round(cs_m, 4),
                ci_h_univ=round(ci_h, 4), ci_m_univ=round(ci_m, 4),
                cs_h_panel=round(cs_h_panel, 4), cs_m_panel=round(cs_m_panel, 4),
                ci_h_panel=round(ci_h_panel, 4), ci_m_panel=round(ci_m_panel, 4),
                mt_h=mt_h, mt_m=mt_m,
                call=('human' if score_h - score_m >= THR['sp_margin'] and score_h >= THR['sp_floor'] else
                      'mouse' if score_m - score_h >= THR['sp_margin'] and score_m >= THR['sp_floor'] else
                      'ambiguous'))


# ---------- Mapping into human-symbol space (shared by scoring) ----------
def to_human_symbol(df, assets):
    m2h = {}
    for hs, msyms in assets['h2m_symbols'].items():
        h = assets['hensg2sym'].get(hs)
        if h:
            for m in msyms:
                m2h.setdefault(m.upper(), h)
    out = []
    h2m_id = assets['ensg2ensmusg']
    sym_col = df['symbol'].values if 'symbol' in df else ['NA'] * len(df)
    id_col = df['gene_id'].values
    for i in range(len(df)):
        g, s = str(id_col[i]), str(sym_col[i])
        if RE_H.match(g):
            out.append(assets['hensg2sym'].get(g, 'NA'))
        elif RE_M.match(g):
            out.append(assets['mensg2sym'].get(g, 'NA'))
        elif s and s not in ('NA', '-'):
            out.append(s)
        elif g and not RE_E.match(g):
            out.append(g)   # the gene_id column itself holds symbols (dr-sc shape)
        else:
            out.append('NA')
    res = []
    for x in out:
        if x in assets['human_symbols']:
            res.append(x)
        elif x.upper() in m2h and x not in assets['human_symbols']:
            res.append(m2h[x.upper()])
        elif x.upper() in m2h:
            res.append(m2h[x.upper()])
        else:
            res.append(x)  # as-is (may fail to match and then be dropped during scoring)
    return np.array(res)


# ---------- Evidence C: tissue scoring (contrast-based composition enrichment, full ranking, no hard curation) ----------
def tissue_scores(df_hsym, counts, panels, mk):
    # pseudobulk -> CPM log2
    tot = counts.sum()
    if tot <= 0:
        return None
    agg = pd.Series(counts, index=df_hsym).groupby(level=0).sum()
    agg = agg[agg.index != 'NA']
    cpm = np.log2(1 + agg / agg.sum() * 1e6) if agg.sum() else agg
    det = set(cpm[cpm > 0].index)
    classes = sorted({c for p in panels for c in p['weights']})
    cs = {}
    for c in classes:
        gs = [g for g in mk.get(c, []) if g in cpm.index]
        cs[c] = float(np.mean(cpm[gs])) if gs else 0.0
    W = np.array([[p['weights'].get(c, 0.0) / 100.0 for c in classes] for p in panels])
    s = np.array([cs[c] for c in classes])
    raw = W @ s
    contrast = (W - W.mean(axis=0)) @ s
    # ---- the sim metric is computed only over the adult panel set (the fetal panel shares
    #      CRX/VSX2 etc. expression with adult bulk through the PRPC/NRPC classes -> inflated
    #      composition cosine; handled separately by the fetal gate instead; known prototype
    #      limitation, disclosed in the report)
    adult_idx = [i for i, p in enumerate(panels) if p.get('stage') != 'fetal']
    adult_cls = sorted({c for i in adult_idx for c in panels[i]['weights']})
    Wa = np.array([[panels[i]['weights'].get(c, 0.0) / 100.0 for c in adult_cls] for i in adult_idx])
    sa = np.array([cs[c] for c in adult_cls])
    spa = np.maximum(sa - sa.min(), 0)
    qa = spa / spa.sum() if spa.sum() > 0 else spa
    def _corr(u_, v_):
        u2 = u_ - u_.mean(); v2 = v_ - v_.mean()
        d = np.linalg.norm(u2) * np.linalg.norm(v2)
        return float(np.dot(u2, v2) / d) if d > 0 else 0.0
    sim_a = np.array([_corr(qa, w) for w in Wa])
    order_c_adult = np.array(adult_idx)[np.argsort(-contrast[adult_idx])]
    order_s_adult = np.array(adult_idx)[np.argsort(-sim_a)]
    order = np.argsort(-contrast)
    ranking = []
    for rank, i in enumerate(order):
        e = dict(tissue=panels[i]['name'], raw=round(float(raw[i]), 4),
                 contrast=round(float(contrast[i]), 4))
        if i in adult_idx:
            e['sim'] = round(float(sim_a[adult_idx.index(i)]), 4)
        ranking.append(e)
    if len(order_c_adult) >= 2:
        c1, c2 = contrast[order_c_adult[0]], contrast[order_c_adult[1]]
        gap = (c1 - c2) / (abs(c1) + 1e-9)
    else:
        gap = 1.0
    agree = panels[order_c_adult[0]]['name'] == panels[order_s_adult[0]]['name']
    top1a = panels[order_c_adult[0]]['name']
    return dict(ranking=ranking, top1=top1a, gap=round(float(gap), 4),
                sim_top1=panels[order_s_adult[0]]['name'],
                sim_top1_val=round(float(sim_a.max()), 4),
                metrics_agree=bool(agree),
                n_detected_genes=int(len(det)),
                best_raw=float(raw.max()))


# ---------- Main scoring ----------
def probe(pb_csv, name, assets, mk, panels, human_panel):
    rec = dict(name=name, file=str(pb_csv))
    thr_snapshot = dict(THR)
    rec['thresholds'] = thr_snapshot
    df = pd.read_csv(pb_csv, keep_default_na=False)
    return probe_df(df, rec, assets, mk, panels, human_panel)


def probe_df(df, rec, assets, mk, panels, human_panel):
    """DataFrame core of probe(): shared by probe() (reads a csv) and gate_from_input() (in-memory pseudobulk)."""
    rec.setdefault("thresholds", dict(THR))
    counts = pd.to_numeric(df.get('counts'), errors='coerce').fillna(0).values
    # abundance-semantics probe: all integers and max>=100 -> raw counts; otherwise treated as log/normalized abundance (total-count gate skipped)
    is_counts = bool(len(counts)) and float(np.nanmax(counts)) >= 100 and np.allclose(counts, np.round(counts))
    rec['input_kind'] = 'raw_counts' if is_counts else ('empty' if len(counts) == 0 else 'normalized_abundance')
    rec['evidence_A_id'] = id_evidence(df['gene_id'].astype(str).values)
    ids_str = df['gene_id'].astype(str).values
    id_as_sym = [g for g in ids_str if not RE_E.match(g)]
    syms_in = (df['symbol'].astype(str).values if 'symbol' in df else [])
    rec['evidence_B_symbol'] = symbol_evidence(list(syms_in) + id_as_sym, assets, human_panel)
    gates = []
    # depth gate
    if len(df) == 0 or (df['counts'].sum() if 'counts' in df else 0) == 0:
        gates.append('empty_or_zero_counts')
    detected = int((counts > 0).sum())
    if detected < THR['min_genes_detected']:
        gates.append(f'low_depth_detected={detected}')
    if is_counts and counts.sum() < THR['min_total_counts']:
        gates.append(f'low_total_counts={int(counts.sum())}')
    # species composite: A takes priority, B cross-validates
    a, b = rec['evidence_A_id']['call'], rec['evidence_B_symbol']['call']
    species_call, sp_conf = None, 0.0
    if a in ('human', 'mouse'):
        species_call = a
        if b in ('human', 'mouse') and b != a:
            gates.append(f'species_conflict_id={a}_symbol={b}')
        sp_conf = 0.9 if b in (a, 'none') else 0.4
    elif a == 'mixed_conflict':
        gates.append('species_mixed_id_prefixes')
        species_call = 'conflicted'
    elif a in ('rat_out_of_domain', 'nonhumanmouse_ens_out_of_domain'):
        gates.append('species_out_of_domain')
        species_call = 'out_of_domain'
    else:  # ID path carries no decision power -> symbol path
        if b in ('human', 'mouse'):
            species_call = b
            sp_conf = max(0.3, abs(rec['evidence_B_symbol']['score_h'] - rec['evidence_B_symbol']['score_m']))
        else:
            species_call = 'undetermined'
            gates.append('species_unresolvable')
    # tissue scoring runs only when the species is usable (human/mouse both mappable; out-of-domain species skipped = hard-gate "stop")
    rec['evidence_C_tissue'] = None
    if species_call in ('human', 'mouse'):
        hs = to_human_symbol(df, assets)
        rec['evidence_C_tissue'] = tissue_scores(hs, counts, panels, mk)
        if rec['evidence_C_tissue']:
            C = rec['evidence_C_tissue']
            if C['best_raw'] <= THR['tissue_domain_floor'] and C['ranking'][0]['contrast'] <= 0:
                gates.append('tissue_out_of_domain_no_positive_signal')
            if C['sim_top1_val'] < THR['tissue_sim_floor']:
                gates.append(f"tissue_out_of_domain_low_sim={C['sim_top1_val']}")
            if not C['metrics_agree']:
                gates.append(f"tissue_metrics_disagree contrast={C['top1']} sim={C['sim_top1']}")
            if C['top1'] != 'human_retina_fetal':
                if C['gap'] < THR['tissue_gap']:
                    gates.append(f"tissue_low_gap={C['gap']}")
            # fetal gate: the fetal panel's contrast score overtakes the adult-retina panel -> suspected fetal material, stop and report to the human
            rmap = {r['tissue']: r['contrast'] for r in C['ranking']}
            fet, ad = rmap.get('human_retina_fetal', -9), rmap.get('human_retina', -9)
            if fet > 0 and fet >= ad * THR['fetal_ratio']:
                gates.append('suspected_fetal_stage')
    abstain = len(gates) > 0
    conf = 0.0 if abstain else round(min(1.0, sp_conf * 0.5 + (rec['evidence_C_tissue']['gap'] if rec['evidence_C_tissue'] else 0) * 1.0), 3)
    rec['final'] = dict(species_call=species_call,
                        tissue_ranking=(rec['evidence_C_tissue']['ranking'] if rec['evidence_C_tissue'] else None),
                        tissue_top1=(rec['evidence_C_tissue']['top1'] if rec['evidence_C_tissue'] else None),
                        confidence=conf, abstain=abstain, gate_reasons=gates)
    return rec


# ---------- Wiring facade (consumed by run_pipeline.py) ----------
_CTOR = {}


def _ctx():
    """Lazy singleton for assets/panels (process-level; the scoring engine is forbidden to read pitfalls text, see module header)."""
    if not _CTOR:
        _CTOR['assets'] = pickle.load(open(ASSETS, 'rb'))
        _CTOR['mk'], _CTOR['kbflag'] = load_markers()
        _CTOR['panels'] = load_tissue_panels()
        _CTOR['human_panel'] = sorted({g for c in ['Rod', 'Cone', 'BC', 'AC', 'HC', 'RGC', 'MG', 'Astro', 'RPE']
                                       for g in _CTOR['mk'][c]})
    return _CTOR


def pseudobulk_from_anndata(adata, sample=None):
    """AnnData (raw counts or normalized values, semantics probed downstream) -> pseudobulk DataFrame
    (columns gene_id[, symbol], counts — same shape as s0_probe inputs/pb/*.csv).
    Backed mode sums in chunks and never loads the whole matrix (memory iron rule #1)."""
    import scipy.sparse as sp
    n_genes = adata.shape[1]
    tot = np.zeros(n_genes, dtype=np.float64)
    if adata.isbacked:
        CH = 5000
        X = adata.X
        for s in range(0, adata.shape[0], CH):
            blk = X[s:s + CH]
            blk = blk.tocsr() if sp.issparse(blk) else blk
            tot += np.asarray(blk.sum(axis=0)).ravel()
    else:
        X = adata.X
        if sp.issparse(X):
            for s in range(0, adata.shape[0], 20000):
                tot += np.asarray(X[s:s + 20000].sum(axis=0)).ravel()
        else:
            tot = np.asarray(X).sum(axis=0)
    var = adata.var
    sym_col = None
    for c in ('gene_symbols', 'symbol', 'gene_name', 'symbols'):
        if c in var.columns and var[c].notna().any():
            sym_col = c
            break
    df = pd.DataFrame({'gene_id': np.asarray(var_names_of(adata)).astype(str),
                       'counts': tot})
    if sym_col:
        df['symbol'] = var[sym_col].astype(str).values
    return df


def var_names_of(adata):
    return adata.var_names


def map_tissue_to_dict(panel_top1):
    """S0 panel name -> dictionary tissue name; returns (dict_name, in_dict_or_alias_note)."""
    if panel_top1 in TISSUE_TO_DICT:
        return TISSUE_TO_DICT[panel_top1], 'alias-map'
    for pref in ('human_', 'mouse_'):
        if panel_top1.startswith(pref):
            stem = panel_top1[len(pref):]
            return stem, 'strip-prefix'
    return panel_top1, 'as-is'


def gate_from_input(input_path, sample_col='', name=None):
    """Wiring gate: read input (stage_a loader, h5ad via backed) -> pseudobulk -> probe.
    Returns (rec, tmp_df); writes no files and applies no override — consumed by run_pipeline."""
    from stage_a_processing import load_input  # same-directory module
    p = Path(input_path)
    name = name or p.name
    if p.is_file() and p.suffix == '.h5ad':
        import anndata as ad
        a = ad.read_h5ad(p, backed='r')  # memory iron rule: backed read
        pb = pseudobulk_from_anndata(a)
        del a
    else:
        import tempfile
        logf = Path(tempfile.gettempdir()) / f"s0_{os.getpid()}.log"
        a = load_input(p, logf, sample_col=sample_col)
        pb = pseudobulk_from_anndata(a)
        del a
    c = _ctx()
    rec = probe_df(pb, dict(name=name, file=str(p)), c['assets'], c['mk'],
                   c['panels'], c['human_panel'])
    return rec


def main():
    import argparse
    ap = argparse.ArgumentParser(description="S0 sample pre-check layer, standalone smoke (same CLI shape as the prototype)")
    ap.add_argument('pb')
    ap.add_argument('--name', default=None)
    ap.add_argument('--out', default=None,
                    help="omit = do not write JSON, only print the final line")
    ap.add_argument('--thr-json', default=None)
    a = ap.parse_args()
    if a.thr_json:
        THR.update(json.load(open(a.thr_json)))
    c = _ctx()
    rec = probe(a.pb, a.name or os.path.basename(a.pb), c['assets'], c['mk'],
                c['panels'], c['human_panel'])
    if a.out:
        os.makedirs(a.out, exist_ok=True)
        jout = os.path.join(a.out, (a.name or os.path.basename(a.pb).replace('.csv', '')) + '.json')
        json.dump(rec, open(jout, 'w'), ensure_ascii=False, indent=1)
    else:
        jout = None
    print(json.dumps({k: rec[k] for k in ('evidence_A_id',)}, ensure_ascii=False))
    print('final:', json.dumps({k: rec['final'][k] for k in ('species_call', 'tissue_top1', 'confidence', 'abstain', 'gate_reasons')}, ensure_ascii=False))
    if jout:
        print('->', jout)


if __name__ == '__main__':
    main()
