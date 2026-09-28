#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX-P4: 三席盲注 runner（run_annotator_run7rg.py 逐字派生；PREREG_v2 §7.1/§7.2）。
用法: python3 kbx_p4_annotator.py <model> <stem_A|B|C>
温度 0.2 / max_tokens 3500 / CHUNK=5 / 3 重试 / 独立断点；qwen 系 enable_thinking=false。
票上限 120=3×40（§2.4），face 构建侧已断言。"""
import json, re, urllib.request, hashlib, datetime, os, sys, time

ROOT = '/mnt/D/EyeKB/plans/kbx_lacrimal_20260928'
FROZEN_INSTR = '/mnt/D/EyeKB/plans/evalset/annotation/ANNOT_INSTRUCTIONS.md'
APPEND = f'{ROOT}/face/KBX_PROMPT_APPEND.txt'
FACE = f'{ROOT}/face/EV_DIGEST_SLIM_kbx.jsonl'
MODEL, STEM = sys.argv[1], sys.argv[2]
OUT = f'{ROOT}/annotation/ANN_{STEM}_kbx.jsonl'
DONEF = f'{ROOT}/annotation/.kbx_{STEM}_done.json'
META = f'{ROOT}/annotation/ANN_{STEM}_kbx_META.json'

rows = [json.loads(l) for l in open(FACE, encoding='utf-8')]
instr = open(FROZEN_INSTR, encoding='utf-8').read()
appendix = open(APPEND, encoding='utf-8').read()
cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)

def card_lines(r):
    hits = r.get('kb_gene_hits') or {}
    hits_s = '; '.join(f"{k}->{','.join(v[:2])}" for k, v in hits.items()) if hits else '无'
    rank_s = '; '.join(f"{x['cell_type']}(n={x['n_shared']})" for x in (r.get('kb_celltype_ranking') or [])) or '无'
    return [
        f"[{r['cluster_id']}] member={r['member']} material=species:{r['material']['species']}/tissue:{r['material']['tissue']}/pool:{r['material']['pool']} n_cells={r['n_cells']} qc={r['qc']}",
        f"top_genes(按序): {', '.join(r['top_genes'])}",
        f"kb_gene_hits: {hits_s}",
        f"kb_celltype_ranking: {rank_s}",
        f"sorts(分选池构成): {r['sorts']}",
        f"donors: {r['donors']}",
    ]

def build_prompt(chunk):
    cards = '\n'.join('\n'.join(card_lines(r)) for r in chunk)
    ids = ' / '.join(r['cluster_id'] for r in chunk)
    return f"""你是单细胞注释双盲评测的判读员（槽位 {STEM}）。对以下 {len(chunk)} 个聚类逐一盲注。只依据证据卡判读，禁止臆测证据之外的来源。

## 判读规则（冻结件原文，必须遵守）
{instr}

## 本 run 成员词表与字段说明（冻结件，必须遵守）
{appendix}

## 证据卡（{len(chunk)} 簇；cluster_id 必须原样返回：{ids}）
说明：基因为 symbol；本 run 无 lit 行。

{cards}

## 输出要求
只输出 JSONL，共 {len(chunk)} 行，顺序与证据卡一致。每行字段：cluster_id / identity / level / grade / gates / flag / why。
identity 必须用 LG 词表原样词，或 coarse:<词表名或谱系上位名>，或 undetermined；不得自造同义词、不得加中文注释。
level: majority|coarse|fine-cap；grade: A|B|C（A 仅独立实验级证据，本证据面下不给）；gates 三键(identity_evidence/resolution/technical) 取 pass|fail|unresolved|na；flag: none|out_of_baseline_coverage|conflicts_with_literature|technical_suspect|candidate_biology；why ≤40字。
证据不足给 undetermined/coarse，合法，禁止硬注。不要输出任何解释文字。
"""

def call(p, mx=3500, tmo=300):
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': p}], 'temperature': 0.2, 'max_tokens': mx}
    if MODEL.startswith('qwen'):
        body['enable_thinking'] = False
    req = urllib.request.Request(base_url.rstrip('/') + '/chat/completions', data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key})
    resp = json.load(urllib.request.urlopen(req, timeout=tmo))
    msg = resp['choices'][0]['message']
    txt = msg.get('content') or ''
    if not txt.strip():
        txt = msg.get('reasoning_content') or ''
    return txt, resp.get('usage', {})

def parse(txt):
    out = {}
    for l in txt.splitlines():
        l = l.strip().strip('`')
        if l.startswith('{'):
            try:
                r = json.loads(l)
                if 'cluster_id' in r:
                    out[r['cluster_id']] = r
            except Exception:
                pass
    return out

done = json.load(open(DONEF)) if os.path.exists(DONEF) else {}
usage_total = {'prompt_tokens': 0, 'completion_tokens': 0}
CHUNK = 5
for i in range(0, len(rows), CHUNK):
    chunk = rows[i:i+CHUNK]
    ids = [r['cluster_id'] for r in chunk]
    if all(c in done for c in ids):
        continue
    got = {}
    for att in range(1, 4):
        try:
            txt, u = call(build_prompt(chunk))
            usage_total['prompt_tokens'] += u.get('prompt_tokens', 0)
            usage_total['completion_tokens'] += u.get('completion_tokens', 0)
            g = {k: v for k, v in parse(txt).items() if k in set(ids)}
            if len(g) == len(ids):
                got = g
                break
            print(f'batch {i//CHUNK+1} att{att}: got {len(g)}/{len(ids)}', flush=True)
        except Exception as e:
            print(f'batch {i//CHUNK+1} att{att} ERR {type(e).__name__} {str(e)[:60]}', flush=True)
            time.sleep(15)
    if not got:
        print(f'batch {i//CHUNK+1} FAILED — saving progress, rerun resumes', flush=True)
        break
    done.update(got)
    json.dump(done, open(DONEF, 'w'), ensure_ascii=False)
    print(f'batch {i//CHUNK+1}/{(len(rows)+CHUNK-1)//CHUNK} ok ({len(done)}/{len(rows)})', flush=True)

json.dump(done, open(DONEF, 'w'), ensure_ascii=False)
order = [r['cluster_id'] for r in rows]
lines = [json.dumps(done[c], ensure_ascii=False) for c in order if c in done]
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
json.dump({'model': MODEL, 'stem': STEM, 'card': 'EV_DIGEST_SLIM_kbx.jsonl',
           'face_sha256': hashlib.sha256(open(FACE, 'rb').read()).hexdigest(),
           'instructions': 'ANNOT_INSTRUCTIONS.md',
           'instructions_sha256': hashlib.sha256(open(FROZEN_INSTR, 'rb').read()).hexdigest(),
           'append_sha256': hashlib.sha256(open(APPEND, 'rb').read()).hexdigest(),
           'prereg_sha256': hashlib.sha256(open(f'{ROOT}/KBX_PREREG_v2.md', 'rb').read()).hexdigest(),
           'time': datetime.datetime.now().isoformat(), 'n_rows': len(lines),
           'missing': [c for c in order if c not in done], 'usage': usage_total},
          open(META, 'w'), ensure_ascii=False, indent=1)
print(f'WROTE {OUT} rows={len(lines)} missing={len(order)-len(lines)}', flush=True)
