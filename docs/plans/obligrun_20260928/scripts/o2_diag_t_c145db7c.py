#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN OB-2 (t_c145db7c): A07 投票前诊断表首跑（注册包 §6 列规格逐字）。
arm 语义逐字=k5_face_build.py build_markers/k9_query（源码抽取复用，非重写）。
产 out/pre_vote_diagnostics.tsv；硬断言 post_shield top3 == 票面 kb_marker_ranking（不一致=run 作废→非零退出）。
Q6::8/Q6::26 指定对照簇逐簇单列；Q6::26 型掏空回退指认行附 out/OB2_notes.md。"""
import json, sys, collections

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
KB9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
import os
os.environ.pop('EYEKB_ACT_V6', None)
import eyekb_core as C

# --- 逐字抽取 k5 的 build_markers / k9_query（含其全局依赖）---
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

# 全 ranking 版 matcher（与 k9_query 同排序语义，仅去掉 [:3] 截断——top3 切片必须逐字相等，先自证）
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

face = [json.loads(l) for l in open(f'{ROOT}/face/EV_DIGEST_SLIM_q6_oblig.jsonl', encoding='utf-8')]
arms = json.load(open(f'{KB9}/out/kb9_face_arms.json'))
cw = json.load(open(f'{ROOT}/ledgers/immune_fold_names.json'))  # 免疫折叠 entry 名单（由 truth_fold 导）
IMMUNE = set(cw['immune_fold'])

CFG_PRE = {'on': True, 'k9': True, 'r1': True}
CFG_POST = {'on': True, 'k9': True, 'shield': True, 'r1': True}

def top10_syms(r):
    return [(s or g) for g, s in zip(r['top_genes'][:10], (r.get('top_genes_sym') or [])[:10])]

rows = []
hard_fail = []
hollow_flagged = []
for r in face:
    cid = r['cluster_id']
    gl = top10_syms(r)
    pre, mpk = full_query(gl, CFG_PRE)
    post, mpk2 = full_query(gl, CFG_POST)
    # 截断自证：full[:3] == k9_query(截断版) == armC
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

cols = ['cluster_id', 'entry_id', 'raw_hit_genes', 'n_raw', 'shielded_hit_genes', 'n_shielded',
        'n_remaining', 'rank_pre_shield', 'rank_post_shield', 'top3_flag_post', 'immune_support_flag']
with open(f'{ROOT}/out/pre_vote_diagnostics.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for x in rows:
        f.write('\t'.join(str(x[c]) for c in cols) + '\n')

notes = []
notes.append('# OB-2 附注（t_c145db7c，PREREG §6 OB-2）')
notes.append(f'- 硬断言 post_shield top3 == 票面 kb_marker_ranking：33 簇全检，失败={len(hard_fail)} 例 {hard_fail}')
notes.append('- 指定对照簇 Q6::8 / Q6::26 逐簇免疫候选行：')
for cid in ('Q6::8', 'Q6::26'):
    sub = [x for x in rows if x['cluster_id'] == cid and x['immune_support_flag']]
    if not sub:
        notes.append(f'  {cid}: 屏蔽后 ranking 无免疫候选行（如实登记）')
    for x in sub:
        notes.append(f"  {cid}: {x['entry_id']} n_raw={x['n_raw']} n_shielded={x['n_shielded']} n_remaining={x['n_remaining']} "
                     f"rank {x['rank_pre_shield']}→{x['rank_post_shield']} top3={x['top3_flag_post']} [{x['immune_support_flag']}]")
notes.append('- Q6::26 型"证据被掏空"回退指认（n_shielded>0 且 n_remaining=0 的免疫头部）：')
if hollow_flagged:
    for cid, et, hits in hollow_flagged:
        notes.append(f'  {cid}: {et} 掏空（raw_hits={hits}）')
else:
    notes.append('  本票面（C 臂）下免疫类整体已被 R1 退出/未入头部——Q6::26 RUN5 原案（APC 头部掏空致 coarse）发生在旧库态；C 臂中该簇免疫候选行见上表单列。')
open(f'{ROOT}/out/OB2_notes.md', 'w', encoding='utf-8').write('\n'.join(notes) + '\n')

print('OB-2 rows:', len(rows), '| hard-assert failures:', len(hard_fail))
print('hollow-flagged:', hollow_flagged)
if hard_fail:
    sys.exit(2)
print('PASS: 票面与诊断表一致')
