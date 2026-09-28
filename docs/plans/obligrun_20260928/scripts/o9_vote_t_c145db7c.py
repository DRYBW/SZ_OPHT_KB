#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, PREREG §4-5 + ADD1 A4): 正式三席票 run（票面 v2.1）。
k6_annotator.py 同参派生：FACE=face/kb9_face_v2.1.jsonl 全 33 簇；prompt/温度0.2/max_tokens3500/
CHUNK=5/3重试 与 RUN5/KB9 逐字同；enable_thinking:false 按探针件逐席继承（qwen 必带）。
硬票预算：全局计数器 logs/vote_budget_counter.tsv——每张可入面档的票计 1（含重试批返回票），
将超 150 立即停止一切后续请求并置 VOTE_BUDGET_EXCEEDED 标记（退出码 5→block 上报）。
429/配额=如实报错，禁自行换通道。用法: python3 o9_vote_t_c145db7c.py <model> <stem>"""
import json, re, urllib.request, hashlib, datetime, os, sys, time

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
EV = '/mnt/D/EyeKB/plans/evalset'
FACE = f'{ROOT}/face/kb9_face_v2.1.jsonl'
MODEL, STEM = sys.argv[1], sys.argv[2]
OUT = f'{ROOT}/out/ANN_{STEM}_oblig.jsonl'
DONEF = f'{ROOT}/out/.oblig_{STEM}_done.json'
META = f'{ROOT}/out/ANN_{STEM}_oblig_META.json'
RAW = f'{ROOT}/logs/vote_raw/{STEM}'
COUNTER = f'{ROOT}/logs/vote_budget_counter.tsv'
BUDGET = 150
os.makedirs(RAW, exist_ok=True)

rows = [json.loads(l) for l in open(FACE, encoding='utf-8')]
assert len(rows) == 33
# 行序=RUN5/v1 面行序（批组成不变断言）
v1_ids = [json.loads(l)['cluster_id'] for l in open(f'{ROOT}/face/EV_DIGEST_SLIM_q6_oblig.jsonl', encoding='utf-8')]
assert [r['cluster_id'] for r in rows] == v1_ids, '行序漂移——停'
instr = open(f'{EV}/annotation/ANNOT_INSTRUCTIONS.md', encoding='utf-8').read()
cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)

# 探针继承（ADD1 A4；qwen 席必带）
probe = json.load(open(f'{ROOT}/logs/seat_probe_{STEM}.json'))
KEEP_THINK_FALSE = bool(probe['param_enable_thinking_false']) or MODEL.startswith('qwen')
if MODEL.startswith('qwen') and not probe['param_enable_thinking_false']:
    raise SystemExit(f'qwen 席探针未确认带参——按 PREREG §4 qwen 必带，停')


def budget_sum():
    if not os.path.exists(COUNTER):
        return 0
    tot = 0
    with open(COUNTER, encoding='utf-8') as f:
        for line in f:
            p = line.rstrip('\n').split('\t')
            if len(p) >= 5:
                try:
                    tot += int(p[4])
                except ValueError:
                    pass
    return tot


def add_budget(n):
    with open(COUNTER, 'a', encoding='utf-8') as f:
        f.write(f'{datetime.datetime.now().isoformat()}\t{STEM}\t{MODEL}\tballots\t{n}\n')
        f.flush()


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


def build_prompt(chunk):
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


def call(p, mx=3500, tmo=300):
    body = {'model': MODEL, 'messages': [{'role': 'user', 'content': p}], 'temperature': 0.2, 'max_tokens': mx}
    if KEEP_THINK_FALSE:
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
blocked = False
for i in range(0, len(rows), CHUNK):
    chunk = rows[i:i + CHUNK]
    ids = [r['cluster_id'] for r in chunk]
    if all(c in done for c in ids):
        continue
    if os.path.exists(f'{ROOT}/logs/VOTE_BUDGET_EXCEEDED'):
        blocked = True
        break
    if budget_sum() + len(ids) > BUDGET:
        open(f'{ROOT}/logs/VOTE_BUDGET_EXCEEDED', 'w').write(f'{STEM} pre-request guard @ budget={budget_sum()}\n')
        blocked = True
        break
    got = {}
    for att in range(1, 4):
        try:
            txt, u = call(build_prompt(chunk))
            usage_total['prompt_tokens'] += u.get('prompt_tokens', 0)
            usage_total['completion_tokens'] += u.get('completion_tokens', 0)
            allb = parse(txt)
            # 预算口径：每张可入面档的票计 1（含重试批返回票）——按响应内可解析票计数
            add_budget(len([k for k in allb if k in set(ids) or str(k).startswith('Q6::')]))
            open(f'{RAW}/b{i//CHUNK+1}_att{att}.txt', 'w', encoding='utf-8').write(txt)
            g = {k: v for k, v in allb.items() if k in set(ids)}
            if len(g) == len(ids):
                got = g
                break
            print(f'batch {i//CHUNK+1} att{att}: got {len(g)}/{len(ids)} | budget={budget_sum()}', flush=True)
        except Exception as e:
            print(f'batch {i//CHUNK+1} att{att} ERR {type(e).__name__} {str(e)[:60]}', flush=True)
            time.sleep(15)
        if budget_sum() + 5 > BUDGET:
            open(f'{ROOT}/logs/VOTE_BUDGET_EXCEEDED', 'w').write(f'{STEM} post-response guard @ budget={budget_sum()}\n')
            blocked = True
            break
    if blocked:
        break
    if not got:
        print(f'batch {i//CHUNK+1} FAILED — saving progress, rerun resumes', flush=True)
        break
    done.update(got)
    json.dump(done, open(DONEF, 'w'), ensure_ascii=False)
    print(f'batch {i//CHUNK+1}/{(len(rows)+CHUNK-1)//CHUNK} ok ({len(done)}/{len(rows)}) | budget={budget_sum()}', flush=True)

order = [r['cluster_id'] for r in rows]
lines = [json.dumps(done[c], ensure_ascii=False) for c in order if c in done]
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
json.dump({'model': MODEL, 'stem': STEM, 'face': 'kb9_face_v2.1.jsonl',
           'face_sha256': hashlib.sha256(open(FACE, 'rb').read()).hexdigest(),
           'protocol': 'PREREG_OBLIGRUN.md + ADD1（票规 v2 C2b 声明见原预注册 §1）',
           'enable_thinking_false': KEEP_THINK_FALSE,
           'time': datetime.datetime.now().isoformat(), 'n_rows': len(lines),
           'missing': [c for c in order if c not in done], 'usage': usage_total,
           'budget_consumed_total': budget_sum(), 'budget_blocked': blocked},
          open(META, 'w'), ensure_ascii=False, indent=1)
print(f'WROTE {OUT} rows={len(lines)} missing={len(order)-len(lines)} blocked={blocked}', flush=True)
sys.exit(5 if blocked else (0 if len(lines) == 33 else 4))
