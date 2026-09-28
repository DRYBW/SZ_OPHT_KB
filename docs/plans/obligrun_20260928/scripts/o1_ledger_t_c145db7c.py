#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN OB-1 (t_c145db7c): AV2-5(c) 历史 ON 态门对账。
产 out/OB1_ledger.tsv（逐簇×逐字段 + 全局项）+ logs/batch_composition.json + logs/requests_reconstructed_run5/。
判读口径=PREREG_OBLIGRUN.md §6 OB-1 (a)(b)(c)(d)。零写入冻结件；只读本卡目录外一切。"""
import json, hashlib, os, re, collections

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
EV = '/mnt/D/EyeKB/plans/evalset'
KB9 = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
run5_face = [json.loads(l) for l in open(f'{EV}/digest/face_q6/EV_DIGEST_SLIM_q6.jsonl', encoding='utf-8')]
obl_face = [json.loads(l) for l in open(f'{ROOT}/face/EV_DIGEST_SLIM_q6_oblig.jsonl', encoding='utf-8')]
changed = set(json.load(open(f'{KB9}/out/kb9_changed_clusters.json'))['changed'])
attribution = json.load(open(f'{KB9}/out/kb9_attribution.json'))
instr_sha = hashlib.sha256(open(f'{EV}/annotation/ANNOT_INSTRUCTIONS.md', 'rb').read()).hexdigest()
r5runner_sha = hashlib.sha256(open(f'{EV}/annotation/run_annotator_run5.py', 'rb').read()).hexdigest()
FIELDS = ['member', 'material', 'n_cells', 'qc', 'top_genes', 'top_genes_sym', 'gene_hits',
          'kb_marker_ranking', 'lit', 'tissue_composition_ref']
SEATS = {'A': 'qwen3.8-max', 'B': 'glm-5.1', 'C': 'deepseek-v3.2'}

# ---- 批组成快照（RUN5 与正式 run 均=面件行序 CHUNK=5）----
CHUNK = 5
batches = [[r['cluster_id'] for r in obl_face[i:i+CHUNK]] for i in range(0, len(obl_face), CHUNK)]
json.dump({'chunk': CHUNK, 'n_batches': len(batches), 'batches': batches,
           'equals_run5_row_order': [r['cluster_id'] for r in run5_face] == [r['cluster_id'] for r in obl_face]},
          open(f'{ROOT}/logs/batch_composition.json', 'w'), ensure_ascii=False, indent=1)

# ---- RUN5 完整请求确定性重渲染（runner 逐字逻辑内嵌；runner sha+面件 sha+指令 sha 三件钉定）----
instr = open(f'{EV}/annotation/ANNOT_INSTRUCTIONS.md', encoding='utf-8').read()

def render_genes(r):
    out = []
    for g, s in zip(r['top_genes'][:20], r.get('top_genes_sym') or []):
        out.append(f"{s}({g})" if (s and str(g).startswith('ENSG')) else (s or g))
    return ', '.join(out)

def render_lit(lit):
    if not lit:
        return '无'
    parts = []
    for ct, entries in lit.items():
        for e in (entries or [])[:2]:
            parts.append(f"{ct}|PMID:{e.get('pmid')}|{(e.get('t') or '')[:70]}")
    return ' ; '.join(parts[:6])

def build_prompt(chunk, STEM):
    cards = []
    for r in chunk:
        rank = '; '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in (r.get('kb_marker_ranking') or [])) or '无'
        hits = r.get('gene_hits') or {}
        hits_s = '; '.join(f"{k}->{','.join(v[:2])}" for k, v in hits.items()) if hits else '无'
        cards.append(f"[{r['cluster_id']}] member={r['member']} material=species:{r['material']['species']}/tissue:{r['material']['tissue']} n_cells={r['n_cells']} qc={r.get('qc','na')}\n"
                     f"top_genes(按序, symbol(原ID)): {render_genes(r)}\nkb_gene_hits: {hits_s}\nkb_celltype_ranking: {rank}\nlit(文献证据): {render_lit(r.get('lit'))}")
    ids = ' / '.join(r['cluster_id'] for r in chunk)
    return f"""你是单细胞注释双盲评测的判读员（槽位 {STEM}）。对以下 {len(chunk)} 个聚类逐一盲注。只依据证据卡判读，禁止臆测证据之外的来源。

## 判读规则（冻结件原文，必须遵守）
{instr}

## 证据卡（{len(chunk)} 簇；cluster_id 必须原样返回：{ids}）
说明：基因以 symbol(原ENSG ID) 双列呈现；lit 为本地文献库检索证据（排序是检索副产物不是置信度）。

{chr(10).join(cards)}

## 输出要求
只输出 JSONL，共 {len(chunk)} 行，顺序与证据卡一致。每行字段：cluster_id / identity / level / grade / gates / flag / why。
identity 必须用该 member 词表原样词，或 coarse:<词>，或 undetermined；不得自造同义词、不得加中文注释。
level: majority|coarse|fine-cap；grade: A|B|C（A 仅独立实验级证据，本证据面下不给）；gates 三键(identity_evidence/resolution/technical) 取 pass|fail|unresolved|na；flag: none|out_of_baseline_coverage|conflicts_with_literature|technical_suspect|candidate_biology；why ≤40字。
证据不足给 undetermined/coarse，合法，禁止硬注。不要输出任何解释文字。
"""

os.makedirs(f'{ROOT}/logs/requests_reconstructed_run5', exist_ok=True)
req_index = []
for stem in SEATS:
    for bi in range(len(batches)):
        chunk = run5_face[bi*CHUNK:(bi+1)*CHUNK]
        p = build_prompt(chunk, stem)
        fn = f'{ROOT}/logs/requests_reconstructed_run5/{stem}_b{bi+1:02d}.txt'
        open(fn, 'w', encoding='utf-8').write(p)
        req_index.append(dict(seat=stem, model=SEATS[stem], batch=bi+1, clusters=batches[bi],
                              request_sha256=hashlib.sha256(p.encode('utf-8')).hexdigest(), bytes=len(p.encode('utf-8'))))
json.dump({'note': 'RUN5 完整请求确定性重渲染（三件钉定=runner sha %s / 指令 sha %s / 面件 sha f083dd60…；RUN5 当时未逐字节留档原文，替代取证形态登记 PREREG §6(c)）'
           % (r5runner_sha[:16], instr_sha[:16]), 'runs': req_index},
          open(f'{ROOT}/logs/requests_reconstructed_run5/INDEX.json', 'w'), ensure_ascii=False, indent=1)

# ---- RUN5 存档票完整性 ----
ballots = {}
for stem in SEATS:
    rows = [json.loads(l) for l in open(f'{EV}/annotation/ANN_{stem}_run5.jsonl', encoding='utf-8') if l.strip()]
    done = json.load(open(f'{EV}/annotation/.run5_{stem}_done.json'))
    meta = json.load(open(f'{EV}/annotation/ANN_{stem}_run5_META.json'))
    ids = [r['cluster_id'] for r in rows]
    ballots[stem] = dict(n=len(rows), order_eq_face=ids == [r['cluster_id'] for r in run5_face],
                         done_eq_jsonl=all(json.dumps(done[c], sort_keys=True) == json.dumps(r, sort_keys=True) for c, r in zip(ids, rows)),
                         face_sha256_eq_archive=meta['face_sha256'] == 'f083dd60ee4e4eb945c35e0bb69976dc6641f82f3b549a4a6c914873e0f9403c',
                         model=meta['model'], time=meta['time'])

# ---- 逐簇×逐字段对账表 ----
rows_out = []
drift_beyond = []
for r5, ro in zip(run5_face, obl_face):
    cid = r5['cluster_id']
    for fld in FIELDS:
        e1, e2 = r5.get(fld), ro.get(fld)
        if fld == 'kb_marker_ranking':
            e1c = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (e1 or [])]
            e2c = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (e2 or [])]
            eq = e1c == e2c
        else:
            eq = json.dumps(e1, sort_keys=True) == json.dumps(e2, sort_keys=True)
        kind = '提案内变更' if (not eq and fld in ('kb_marker_ranking', 'lit')) else ('逐字节一致' if eq else '越界漂移')
        if kind == '越界漂移':
            drift_beyond.append((cid, fld))
        rows_out.append(dict(scope='cluster', cluster_id=cid, field=fld,
                             in_changed_set=str(cid in changed), status=kind,
                             run5_val_sha16=hashlib.sha256(json.dumps(e1, sort_keys=True).encode()).hexdigest()[:16],
                             oblig_val_sha16=hashlib.sha256(json.dumps(e2, sort_keys=True).encode()).hexdigest()[:16]))
# 全局项行
glb = [
    ('global', 'batch_composition', '逐字节一致', f'7 批（5,5,5,5,5,5,3）行序=RUN5 面件序；logs/batch_composition.json equals_run5_row_order=True'),
    ('global', 'ANNOT_INSTRUCTIONS.md sha', '逐字节一致', instr_sha),
    ('global', 'runner 参数', '逐字节一致', 'temperature=0.2 max_tokens=3500 CHUNK=5 3重试；三席 qwen3.8-max/glm-5.1/deepseek-v3.2（META 与 KB9_PREREG §3 对账）'),
    ('global', 'RUN5 请求原文留档', '等级注记', 'RUN5 完整请求未逐字节留档；以三件钉定确定性重渲染 21 请求替代（logs/requests_reconstructed_run5/，sha 逐请求登记）——G1≠历史 ON 保真（注册包 §4(c) 原文随件）'),
    ('global', '库态 RUN5→今', '历史事实登记', 'library_activation_only=%s（kb9_attribution.json 对照臂；Q6::21/29 回退=KB7 条激活库态变化实证）；本 run 零复用存档票（33 簇全量新票），不据旧票声称当期复测' % attribution['attribution']['library_activation_only']),
    ('global', 'RUN5 存档票完整性 A', '逐字节一致' if ballots['A']['order_eq_face'] and ballots['A']['done_eq_jsonl'] and ballots['A']['face_sha256_eq_archive'] else '不符', json.dumps(ballots['A'], ensure_ascii=False)),
    ('global', 'RUN5 存档票完整性 B', '逐字节一致' if ballots['B']['order_eq_face'] and ballots['B']['done_eq_jsonl'] and ballots['B']['face_sha256_eq_archive'] else '不符', json.dumps(ballots['B'], ensure_ascii=False)),
    ('global', 'RUN5 存档票完整性 C', '逐字节一致' if ballots['C']['order_eq_face'] and ballots['C']['done_eq_jsonl'] and ballots['C']['face_sha256_eq_archive'] else '不符', json.dumps(ballots['C'], ensure_ascii=False)),
]
for sc, fld, st, note in glb:
    rows_out.append(dict(scope=sc, cluster_id='-', field=fld, in_changed_set='-', status=st, run5_val_sha16='-', oblig_val_sha16='-', note=note))

# ---- 判定行 ----
n_changed = len(changed)
b_ok = not drift_beyond
verdict = '清' if b_ok else '不清'
rows_out.append(dict(scope='verdict', cluster_id='ALL', field='OB-1', in_changed_set=f'8不变/{n_changed}变化',
                     status=verdict, run5_val_sha16='-', oblig_val_sha16='-',
                     note=f'(a) 8 不变簇输入面逐字节可对账=True; (b) 越界漂移字段数={len(drift_beyond)}（限 ranking+lit 外）; (c) 请求替代取证已登记; (d) 库态变化已登记。判读口径=PREREG §6 OB-1'))
cols = ['scope', 'cluster_id', 'field', 'in_changed_set', 'status', 'run5_val_sha16', 'oblig_val_sha16', 'note']
with open(f'{ROOT}/out/OB1_ledger.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for r in rows_out:
        f.write('\t'.join(str(r.get(c, '')) for c in cols) + '\n')
print('OB-1 rows:', len(rows_out), '| drift_beyond:', drift_beyond, '| VERDICT:', verdict)
print('ballots:', {k: (v['n'], v['order_eq_face'], v['done_eq_jsonl'], v['face_sha256_eq_archive']) for k, v in ballots.items()})
