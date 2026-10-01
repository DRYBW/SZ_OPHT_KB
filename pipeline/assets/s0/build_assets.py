#!/usr/bin/env python
# S0PROBE build_assets.py — 物种 symbol universe + ortholog 对表缓存
# 只读源: /mnt/D/OcularKB/data/ncbi_orthologs (compara104, gene_info), 输出 assets.pkl
# 写盘仅限本 plans 目录。
import gzip, pickle, sys, os

IN = '/mnt/D/OcularKB/data/ncbi_orthologs'
LOCAL = '/mnt/D/EyeKB/plans/s0_probe_20260930/inputs'
OUT = '/mnt/D/EyeKB/plans/s0_probe_20260930/assets'
os.makedirs(OUT, exist_ok=True)

def parse_gene_info(path):
    """return symbol_set(main+syn), sym2ensg, main_sym_set(官方大小写本体, 用于 cs 判别)"""
    syms, s2e, main = set(), {}, set()
    with gzip.open(path, 'rt', encoding='utf-8', errors='ignore') as f:
        header = f.readline()
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) < 7: continue
            tax, gid, sym, lt, syn, xrefs = p[0], p[1], p[2], p[3], p[4], p[5]
            if sym == '-' or not sym: continue
            syms.add(sym); main.add(sym)
            for x in syn.split('|'):
                if x and x != '-': syms.add(x)
            for x in xrefs.split('|'):
                if x.startswith('Ensembl:'):
                    e = x[8:]
                    if e and sym not in s2e: s2e[sym] = e
    return syms, s2e, main

print('== human gene_info ==')
hs_sym, hs_s2e, hs_main = parse_gene_info(f'{IN}/gene_info/Homo_sapiens.gene_info.gz')
hensg2sym = {v: k for k, v in hs_s2e.items()}
print('human symbols:', len(hs_sym), 'ensg2sym:', len(hensg2sym))

print('== mouse gene_info ==')
ms_sym, ms_s2e, ms_main = parse_gene_info(f'{LOCAL}/Mus_musculus.gene_info.gz')
mensg2sym = {v: k for k, v in ms_s2e.items()}
print('mouse symbols:', len(ms_sym), 'ensmusg2sym:', len(mensg2sym))

print('== rat gene_info (optional) ==')
rs_sym, rs_s2e = set(), {}
rs_main = set()
rat_path = f'{LOCAL}/Rattus_norvegicus.gene_info.gz'
if os.path.exists(rat_path):
    try:
        rs_sym, rs_s2e, rs_main = parse_gene_info(rat_path)
    except Exception as e:
        print('rat parse fail:', e)
print('rat symbols:', len(rs_sym))

print('== compara104 human<->mouse pairs ==')
pairs_h2m, pairs_m2h = {}, {}
n_hi = 0
with gzip.open(f'{IN}/homo_sapiens_compara104.tsv.gz', 'rt') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    i_gs, i_sp, i_ht, i_hgs, i_hsp, i_hc = (hdr.index(x) for x in
        ('gene_stable_id','species','homology_type','homology_gene_stable_id','homology_species','is_high_confidence'))
    o2o_cnt, all_cnt = 0, 0
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) <= i_hc: continue
        if p[i_sp] != 'homo_sapiens' or p[i_hsp] != 'mus_musculus': continue
        g, hg = p[i_gs], p[i_hgs]
        if not (g.startswith('ENSG') and hg.startswith('ENSMUSG')): continue
        all_cnt += 1
        if p[i_hc] == '1':
            n_hi += 1
            pairs_h2m.setdefault(g, set()).add(hg)
            pairs_m2h.setdefault(hg, set()).add(g)
print('mouse-ortholog rows:', all_cnt, 'high-conf pairs (unique directions):', n_hi,
      'h-side:', len(pairs_h2m), 'm-side:', len(pairs_m2h))

# 正式 ortholog: one2one 优先；many 保留全集用于 symbol 桥（B5 教训: 面板映射用并集但记录歧义）
def bridge_maps(pairs, src2sym, dst2sym):
    """src gene-id -> set(dst symbols)"""
    out = {}
    for s, dsts in pairs.items():
        ss = set()
        for d in dsts:
            sym = dst2sym.get(d)
            if sym: ss.add(sym)
        if ss: out[s] = ss
    return out

# human ENSG -> mouse symbols (native case)
h2m_sym = bridge_maps(pairs_h2m, None, mensg2sym)
m2h_sym = bridge_maps(pairs_m2h, None, hensg2sym)
# ensid -> ensid dicts (for id-level mapping)
h2m_id = dict(pairs_h2m); m2h_id = dict(pairs_m2h)

one2one_h2m = {g: next(iter(s)) for g, s in pairs_h2m.items() if len(s) == 1}
one2one_m2h = {m: next(iter(s)) for m, s in pairs_m2h.items() if len(s) == 1}

assets = dict(
    human_symbols=hs_sym, mouse_symbols=ms_sym, rat_symbols=rs_sym,
    human_main=hs_main, mouse_main=ms_main, rat_main=rs_main,
    hensg2sym=hensg2sym, mensg2sym=mensg2sym,
    ensg2ensmusg=h2m_id, ensmusg2ensg=m2h_id,
    h2m_symbols=h2m_sym, m2h_symbols=m2h_sym,
    one2one_h2m=one2one_h2m, one2one_m2h=one2one_m2h,
    meta=dict(compara='homo_sapiens_compara104 is_high_confidence=1',
              built=str(__import__('datetime').datetime.now())),
)
with open(f'{OUT}/species_assets.pkl', 'wb') as f:
    pickle.dump(assets, f, protocol=4)
print('wrote', f'{OUT}/species_assets.pkl')
