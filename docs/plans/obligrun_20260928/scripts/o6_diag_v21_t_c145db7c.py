#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, 案A细则3): OB-2 对票面 v2.1 机械重算。
计算体与 o2_diag_t_c145db7c.py 同源（k5 build_markers/k9_query 逐字抽取复用）；
FACE=kb9_face_v2.1.jsonl；输出新增 delta_vs_v1 列（含剔除后 31 未涉簇零变化对照）；
硬断言：post_shield top3 == v2.1 面 kb_marker_ranking 33/33（不一致=作废停卡，非零退出）。
退出码 0=PASS；2=硬断言失败；4=v1/v2.1 对照出现非预期漂移。"""
import json, sys, os, collections

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
KB9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
V21 = f'{ROOT}/face/kb9_face_v2.1.jsonl'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
os.environ.pop('EYEKB_ACT_V6', None)
import eyekb_core as C

k5 = open(f'{KB9}/scripts/k5_face_build.py', encoding='utf-8').read()
seg = k5[k5.index('# ---- C 臂实现'):k5.index('# ---- G1')]
K9 = json.load(open(f'{KB9}/build/markers_k9_ocs_increment.json'))
SHIELD = json.load(open(f'{KB9}/out/kb9_face_effective_genesets.json'))
ON_NAMES = ['retina', 'membrane', 'retina_interneuron', 'retina_v6', 'face_v6']
RETINA_ONLY_FILES = {'markers_v4.1_clean.json', 'markers_v5_retina_interneuron.json', 'markers_v6_retina_repair.json'}
ns = {'json': json, 'C': C, 'K9': K9, 'SHIELD': SHIELD, 'ON_NAMES': ON_NAMES,
      'RETINA_ONLY_FILES': RETINA_ONLY_FILES, 'os': os, 'ROOT': KB9}
exec(seg, ns)
build_markers, k9_query = ns['build_markers'], ns['k9_query']

def full_query(genes, config):
    markers = build_markers(config)
    gl = [str(g).strip().upper() for g in genes if str(g).strip()]
    score, order = {}, {}
    for i, ct in enumerate(markers):
        n = sum(1 for g in gl if g in markers[ct])
        if n:
            score[ct] = n
            order[ct] = i
    ranked = sorted(score.items(), key=lambda kv: (-kv[1], order[kv[0]]))
    return [{'cell_type': c, 'n_shared': n} for c, n in ranked], markers

face = [json.loads(l) for l in open(V21, encoding='utf-8')]
arms = json.load(open(f'{KB9}/out/kb9_face_arms.json'))
cw = json.load(open(f'{ROOT}/ledgers/immune_fold_names.json'))
IMMUNE = set(cw['immune_fold'])
CFG_PRE = {'on': True, 'k9': True, 'r1': True}
CFG_POST = {'on': True, 'k9': True, 'shield': True, 'r1': True}

def top10_syms(r):
    return [(s or g) for g, s in zip(r['top_genes'][:10], (r.get('top_genes_sym') or [])[:10])]

rows, hard_fail, hollow_flagged = [], [], []
for r in face:
    cid = r['cluster_id']
    gl = top10_syms(r)
    pre, mpk = full_query(gl, CFG_PRE)
    post, mpk2 = full_query(gl, CFG_POST)
    assert pre[:3] == k9_query(gl, CFG_PRE) and post[:3] == k9_query(gl, CFG_POST)
    assert post[:3] == arms['armC_kb9'][cid], f'armC 对账失败 {cid}'
    face_rank = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (r.get('kb_marker_ranking') or [])]
    if post[:3] != face_rank:
        hard_fail.append((cid, post[:3], face_rank))
    pre_pos = {x['cell_type']: i + 1 for i, x in enumerate(pre)}
    post_pos = {x['cell_type']: i + 1 for i, x in enumerate(post)}
    for et in sorted(set(pre_pos) | set(post_pos), key=lambda e: (post_pos.get(e, 99), pre_pos.get(e, 99))):
        raw_set = mpk.get(et, [])
        eff_set = mpk2.get(et, raw_set)
        blocked = set(raw_set) - set(eff_set)
        u_gl = {str(g).strip().upper() for g in gl}
        raw_hits = sorted(u_gl & set(raw_set))
        shielded_hits = sorted(u_gl & blocked)
        n_raw, n_sh = len(raw_hits), len(shielded_hits)
        n_rem = n_raw - n_sh
        top3f = et in post_pos and post_pos[et] <= 3
        if et in IMMUNE:
            flag = f"n_remaining>0:{'Y' if n_rem > 0 else 'N'}|top3:{'Y' if top3f else 'N'}"
            if n_sh > 0 and n_rem == 0:
                hollow_flagged.append((cid, et, raw_hits))
        else:
            flag = ''
        rows.append(dict(cluster_id=cid, entry_id=et, raw_hit_genes=';'.join(raw_hits), n_raw=n_raw,
                         shielded_hit_genes=';'.join(shielded_hits), n_shielded=n_sh, n_remaining=n_rem,
                         rank_pre_shield=pre_pos.get(et, ''), rank_post_shield=post_pos.get(et, ''),
                         top3_flag_post=top3f, immune_support_flag=flag))

# ---- v1 对照（delta_vs_v1）----
v1 = {}
with open(f'{ROOT}/out/pre_vote_diagnostics.tsv', encoding='utf-8') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        p = line.rstrip('\n').split('\t')
        v1[(p[0], p[1])] = tuple(p[2:])
unexpected = []
for x in rows:
    key = (x['cluster_id'], x['entry_id'])
    cur = tuple(str(x[c]) for c in hdr[2:])
    if key not in v1:
        x['delta_vs_v1'] = 'v1无此行(新增)'
        unexpected.append(key)
    elif cur == v1[key]:
        x['delta_vs_v1'] = 'zero'
    else:
        x['delta_vs_v1'] = 'DIFF:' + ';'.join(f'{h}:{o}→{n}' for h, o, n in zip(hdr[2:], v1[key], cur) if o != n)
        unexpected.append(key)
# v1 有而 v2.1 无的行（应=0：诊断表输入不含 lit）
dropped = [k for k in v1 if k not in {(x['cluster_id'], x['entry_id']) for x in rows}]
n_zero = sum(1 for x in rows if x['delta_vs_v1'] == 'zero')

cols = hdr + ['delta_vs_v1']
with open(f'{ROOT}/out/pre_vote_diagnostics_v21.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for x in rows:
        f.write('\t'.join(str(x[c]) for c in cols) + '\n')

notes = []
notes.append('# OB-2 v2.1 机械重算附注（t_c145db7c run142，案A细则3）')
notes.append(f'- 输入面 kb9_face_v2.1.jsonl（sha 2c0649dc…）；行数={len(rows)}（v1={len(v1)}）。')
notes.append(f'- 硬断言 post_shield top3 == v2.1 面 kb_marker_ranking：33 簇全检，失败={len(hard_fail)} 例 {hard_fail}')
notes.append(f'- 31 未涉簇零变化对照 + 2 变化簇对照：delta=zero {n_zero}/{len(rows)} 行；非零漂移 {len(set(unexpected))} 行 {sorted(set(unexpected))[:10]}；v1 行缺失={len(dropped)} {dropped[:6]}')
notes.append('- 说明：诊断表输入=簇 top10 基因×库 marker 集（ranking 臂），lit 字段不进入诊断计算；案 A 仅动 lit（2 行删除）且 ranking 逐字节不动 → 全表预期零漂移，实测一致则「零漂移断言」成立。')
notes.append('- 指定对照簇 Q6::8 / Q6::26（v2.1 重算）：')
for cid in ('Q6::8', 'Q6::26'):
    sub = [x for x in rows if x['cluster_id'] == cid and x['immune_support_flag']]
    if not sub:
        notes.append(f'  {cid}: 屏蔽后 ranking 无免疫候选行（与 v1 一致）')
    for x in sub:
        notes.append(f"  {cid}: {x['entry_id']} n_raw={x['n_raw']} n_shielded={x['n_shielded']} n_remaining={x['n_remaining']} rank {x['rank_pre_shield']}→{x['rank_post_shield']} top3={x['top3_flag_post']} [{x['immune_support_flag']}] delta={x['delta_vs_v1']}")
notes.append('- Q6::26 型掏空回退指认（v2.1）：')
for cid, et, hits in hollow_flagged:
    notes.append(f'  {cid}: {et} 掏空（raw_hits={hits}）')
if not hollow_flagged:
    notes.append('  （v2.1 面掏空行与 v1 相同——lit 变更不影响；v1 指认清单见 out/OB2_notes.md，互引）')
open(f'{ROOT}/out/OB2_notes_v21.md', 'w', encoding='utf-8').write('\n'.join(notes) + '\n')

print(f'OB-2 v2.1 rows: {len(rows)} | hard-fail: {len(hard_fail)} | zero-delta: {n_zero} | unexpected: {len(set(unexpected))} | dropped: {len(dropped)}')
if hard_fail:
    sys.exit(2)
if unexpected or dropped:
    sys.exit(4)
print('PASS: 硬断言 33/33 + 全表零漂移（含 31 未涉簇零变化对照）')
