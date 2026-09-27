#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""BTEST B 臂自由查询 runner（判据件 BTEST_PREREG_v1.0.md §3/§4 冻结协议）。
用法: python3 btest_runner.py <model> <stem_A|B|C> <run1|run2|smoke>
- 卷面 = FACEV21 冻结 45 簇（逐字节同一张卷），B 卡 = header 行 + top_genes 行（§4.1），
  撤下 kb_gene_hits/kb_celltype_ranking/lit/pred_hint/旗行/规则行——证据一律会话内五工具自取。
- 每簇独立会话（1 簇 × ≤8 轮工具 + 强制收尾）；提醒≤2（零工具出票）；格式错误重试≤3；
  簇级重跑≤3 次；PROTOCOL_FAIL 残留 → missing≠0 中止上报（禁跨 run 顶票）。
- 工具 = 进程内直调 mcp_server/server.py 五工具包装函数（同一实现与服务端 calllog 留痕）；
  env EYEKB_MCP_TRACE_TAG=btest_d9；ACT_V6/SOFTFLAGS 不设=默认 ON。参数护栏与截断见 §4.2。
- 成本逐簇落 logs/cost_r{N}_{stem}.jsonl；票落 annotation/ANN_{stem}_btest_r{N}.jsonl；
  断点 DONEF 每簇更新；run1/run2 全量独立。冒烟 smoke 用合成簇 SMOKE::1，不产票。"""
import json, re, os, sys, time, math, urllib.request, datetime, hashlib

ROOT = '/mnt/D/EyeKB/plans/btest_20260927'
EVAL = '/mnt/D/EyeKB/plans/evalset'
F21 = '/mnt/D/EyeKB/plans/face_v21_20260926'
MCP_DIR = '/mnt/D/EyeKB/mcp_server'
FROZEN_INSTR = f'{EVAL}/annotation/ANNOT_INSTRUCTIONS.md'

MODEL, STEM, RUNARG = sys.argv[1], sys.argv[2], sys.argv[3]
assert STEM in ('A', 'B', 'C'), 'stem must be A|B|C'
assert RUNARG in ('run1', 'run2', 'smoke'), 'run arg must be run1|run2|smoke'

cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)

os.environ['EYEKB_MCP_TRACE_TAG'] = 'btest_d9'  # 先于 server import（calllog 会话快照）
sys.path.insert(0, MCP_DIR)
import server  # noqa: E402  进程内直调，calllog 服务端留痕

PREREG_SHA = hashlib.sha256(open(f'{ROOT}/BTEST_PREREG_v1.0.md', 'rb').read()).hexdigest()

# ---------- 五工具：API schema + 护栏执行（§4.2） ----------
TOOLS_SCHEMA = [
    {"type": "function", "function": {
        "name": "query_marker",
        "description": "查本地权威 marker 库（默认 library=all，含 retina/v5/眼表/v6 修复面板）。genes=基因 symbol 列表→反查命中哪些细胞类型及类排名(n_shared)；cell_type=类名→该类 marker 清单。注释第一步：先查本地。返回的排序是检索副产物不是置信度；soft_flags.notes 仅复核线索。",
        "parameters": {"type": "object", "properties": {
            "genes": {"type": "array", "items": {"type": "string"}, "description": "基因 symbol 列表，≤40 个"},
            "cell_type": {"type": "string", "description": "细胞类型名，如 Rod / Muller glia / corneal endothelium；可空"}},
            "required": []}}},
    {"type": "function", "function": {
        "name": "search_literature",
        "description": "检索本地眼科文献库（RAG v2.0，全部带 PMID 可溯源），返回文献片段+期刊年份+marker 共现+相关度。cell_type 建议给出；species=human|mouse|空(不过滤)；tissue 如 retina/cornea/RPE；query 可写显式检索句。top_k≤10。",
        "parameters": {"type": "object", "properties": {
            "cell_type": {"type": "string"}, "species": {"type": "string"},
            "tissue": {"type": "string"}, "query": {"type": "string"},
            "top_k": {"type": "integer"}}, "required": []}}},
    {"type": "function", "function": {
        "name": "get_kb_page",
        "description": "读文献索引页原文。scope=index→总目录；scope=topic,name=主题(如 vascular)；scope=tissue,name=组织(如 cornea/RPE)。白名单路径。",
        "parameters": {"type": "object", "properties": {
            "scope": {"type": "string", "enum": ["index", "topic", "tissue"]},
            "name": {"type": "string"}}, "required": ["scope"]}}},
    {"type": "function", "function": {
        "name": "get_tissue_composition",
        "description": "组织细胞组成基线（供者级参考分布，每条带 PMID/数据集出处）。注释前对照『该组织应有什么、大致多少』；按实际取样材料查询；species=human|mouse；tissue=retina/...；development_stage 留空=成人主档，禁成人桶代答胎儿问题。",
        "parameters": {"type": "object", "properties": {
            "species": {"type": "string"}, "tissue": {"type": "string"},
            "disease": {"type": "string"}, "development_stage": {"type": "string"}},
            "required": ["species", "tissue"]}}},
    {"type": "function", "function": {
        "name": "get_disease_prior",
        "description": "疾病先验条目（预期细胞×状态矩阵+非预期旗+污染旗+marker 签名+出处）。仅在疾病材料对照阶段调用；先验≠真理，与数据打架要列打架清单不许硬凑。",
        "parameters": {"type": "object", "properties": {
            "disease": {"type": "string"}, "tissue": {"type": "string"}},
            "required": ["disease"]}}},
]


def _s(v, n):
    return (str(v) if v is not None else '')[:n]


def exec_tool(name, args):
    """护栏执行（§4.2）：未知工具名/参数越界 → 不执行，回注 error 文本，计入调用数不计取证数；
    结果 JSON 截断 ≤8000 字符。返回 (content_str, executed_bool)。"""
    a = args if isinstance(args, dict) else {}
    try:
        if name == 'query_marker':
            genes = a.get('genes') or []
            if not isinstance(genes, list):
                return (json.dumps({'error': 'args_violation:genes_must_be_list'}), False)
            if len(genes) > 40 or any(not isinstance(g, str) or len(g) > 20 for g in genes):
                return (json.dumps({'error': 'args_violation:genes_bound(≤40×≤20char)'}), False)
            if len(str(a.get('cell_type') or '')) > 80:
                return (json.dumps({'error': 'args_violation:cell_type_bound'}), False)
            r = server.query_marker(genes=[g for g in genes if g] or None,
                                    cell_type=_s(a.get('cell_type'), 80), library='all')
        elif name == 'search_literature':
            tk = a.get('top_k')
            if tk is not None and (not isinstance(tk, int) or not (1 <= tk <= 10)):
                return (json.dumps({'error': 'args_violation:top_k∈[1,10]'}), False)
            if len(str(a.get('query') or '')) > 200 or str(a.get('db') or '') != '':
                return (json.dumps({'error': 'args_violation:query_len/db_locked'}), False)
            r = server.search_literature(cell_type=_s(a.get('cell_type'), 80), top_k=tk if tk else 5,
                                         species=_s(a.get('species'), 20), tissue=_s(a.get('tissue'), 40),
                                         query=_s(a.get('query'), 200), db='')
        elif name == 'get_kb_page':
            if str(a.get('scope')) not in ('index', 'topic', 'tissue') or len(str(a.get('name') or '')) > 80:
                return (json.dumps({'error': 'args_violation:scope/name'}), False)
            r = server.get_kb_page(scope=a['scope'], name=_s(a.get('name'), 80))
        elif name == 'get_tissue_composition':
            if not a.get('species') or not a.get('tissue'):
                return (json.dumps({'error': 'args_violation:species&tissue_required'}), False)
            if any(len(str(a.get(k) or '')) > n for k, n in (('species', 20), ('tissue', 40), ('disease', 100), ('development_stage', 20))):
                return (json.dumps({'error': 'args_violation:str_len'}), False)
            r = server.get_tissue_composition(species=_s(a.get('species'), 20), tissue=_s(a.get('tissue'), 40),
                                              disease=_s(a.get('disease'), 100),
                                              development_stage=_s(a.get('development_stage'), 20))
        elif name == 'get_disease_prior':
            if not a.get('disease') or len(str(a.get('disease'))) > 100 or len(str(a.get('tissue') or '')) > 60:
                return (json.dumps({'error': 'args_violation:disease/tissue'}), False)
            r = server.get_disease_prior(disease=_s(a.get('disease'), 100), tissue=_s(a.get('tissue'), 60))
        else:
            return (json.dumps({'error': f'unknown_tool:{name}'}), False)
    except Exception as e:
        return (json.dumps({'error': f'{type(e).__name__}:{str(e)[:200]}'}), False)
    try:
        txt = json.dumps(r, ensure_ascii=False, default=str)
    except Exception:
        txt = str(r)
    if len(txt) > 8000:
        txt = txt[:8000] + '...[TRUNCATED]'
    return txt, True


# ---------- 卡片与提示词（§4.1 冻结文本） ----------
instr = open(FROZEN_INSTR, encoding='utf-8').read()


def render_genes(r):
    out = []
    for g, s in zip(r['top_genes'][:20], r.get('top_genes_sym') or []):
        out.append(f"{s}({g})" if (s and str(g).startswith('ENSG')) else (s or g))
    return ', '.join(out)


def b_card_lines(r):
    return [f"[{r['cluster_id']}] member={r['member']} material=species:{r['material']['species']}/tissue:{r['material']['tissue']} n_cells={r['n_cells']} qc={r.get('qc','na')}",
            f"top_genes(按序): {render_genes(r)}"]


EXPL = ('取证方式说明（绑定）：本卡不提供任何预烘焙证据；判读所需 marker/文献/组成/疾病先验'
        '一律由你在本会话内调用工具自行取证。冻结件中"输入=EV_DIGEST.jsonl"在本模式读作'
        '"输入=数据卡+工具按需证据"；词表/等级/三门/输出字段以冻结件原文为准。')
REMINDER = ('你尚未调用任何工具取证即给出判读，不符合本模式规程。请先调用至少一个取证工具'
            '（如 query_marker），然后再输出同一格式的 JSON 判定。')
FORCE_FINAL = ('立即基于已获取的证据输出最终单行 JSON 判定（字段 cluster_id/identity/level/grade/'
               'gates/flag/why），不得再调用工具，不得输出任何解释文字。')


def build_b_prompt(row):
    card = '\n'.join(b_card_lines(row))
    ids = row['cluster_id']
    return f"""你是单细胞注释双盲评测的判读员（槽位 {STEM}，自由取证模式）。对以下 1 个聚类逐一盲注。只依据数据卡与你用工具取到的证据判读，禁止臆测证据之外的来源。

## 判读规则（冻结件原文，必须遵守）
{instr}
{EXPL}

## 数据卡（cluster_id 必须原样返回：{ids}）
{card}

## 取证工具（可多轮调用；输出判读前至少调用 1 次）
可用工具：query_marker / search_literature / get_kb_page / get_tissue_composition / get_disease_prior（参数与语义见工具 schema）。
建议：先 query_marker（基因反查类排名，或按候选类取核心 marker）；需要时 get_tissue_composition 对照组成；文献佐证用 search_literature（带 PMID）。
纪律：工具返回只作证据与引用；排序=检索副产物不是置信度；soft_flags 仅复核线索；两谱系核心 marker 共存按冻结件 resolution 口径处理；证据不足给 coarse:<名> 或 undetermined 合法，禁止硬注。

## 输出要求
证据足够时只输出一行 JSON（不要其他文字）：cluster_id / identity / level / grade / gates / flag / why。
identity 必须用该 member 词表原样词，或 coarse:<词>，或 undetermined；不得自造同义词、不得加中文注释。
level: majority|coarse|fine-cap；grade: A|B|C（A 仅独立实验级证据，通常给不到）；gates 三键(identity_evidence/resolution/technical) 取 pass|fail|unresolved|na；flag: none|out_of_baseline_coverage|conflicts_with_literature|technical_suspect|candidate_biology；why ≤40字。
技术可信度门：数据卡无 QC 数值时 technical 填 na。"""


def ballot_valid(d, cid):
    if not isinstance(d, dict):
        return False
    if str(d.get('cluster_id')) != cid:
        return False
    ident = d.get('identity')
    grade = str(d.get('grade', '')).strip()
    return bool(ident) and isinstance(ident, str) and grade in ('A', 'B', 'C')


def parse_ballot(txt, cid):
    for l in (txt or '').splitlines():
        l = l.strip().strip('`')
        if l.startswith('{'):
            try:
                r = json.loads(l)
                if ballot_valid(r, cid):
                    return r
            except Exception:
                pass
    return None


# ---------- API 调用（§3 同参：T=0.2 max_tokens=3500 qwen 关思考） ----------
def call_api(messages, with_tools=True, tmo=300):
    body = {'model': MODEL, 'messages': messages, 'temperature': 0.2, 'max_tokens': 3500}
    if MODEL.startswith('qwen'):
        body['enable_thinking'] = False
    if with_tools:
        body['tools'] = TOOLS_SCHEMA
    req = urllib.request.Request(base_url.rstrip('/') + '/chat/completions',
                                 data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key})
    resp = json.load(urllib.request.urlopen(req, timeout=tmo))
    msg = resp['choices'][0]['message']
    usage = resp.get('usage', {})
    return msg, usage


# ---------- 冒烟（合成簇，不产票不留卷） ----------
if RUNARG == 'smoke':
    smoke_row = {'cluster_id': 'SMOKE::1', 'member': 'Q1',
                 'material': {'species': 'human', 'tissue': 'retina'},
                 'n_cells': 10, 'qc': 'na',
                 'top_genes': ['RHO', 'OPN1SW'], 'top_genes_sym': ['RHO', 'OPN1SW']}
    messages = [{'role': 'user', 'content': build_b_prompt(smoke_row)}]
    executed_any = False
    final_content = ''
    for turn in range(4):
        msg, usage = call_api(messages)
        tc = msg.get('tool_calls')
        if tc:
            messages.append({'role': 'assistant', 'content': msg.get('content') or '',
                             'tool_calls': tc})
            for c in tc:
                fn = c['function']['name']
                try:
                    a = json.loads(c['function'].get('arguments') or '{}', strict=False)
                except Exception:
                    a = {}
                content, executed = exec_tool(fn, a)
                executed_any = executed_any or executed
                messages.append({'role': 'tool', 'tool_call_id': c.get('id', fn),
                                 'name': fn, 'content': content})
            continue
        final_content = msg.get('content') or ''
        if not executed_any:
            messages.append({'role': 'user', 'content': REMINDER})
            continue
        break
    line = (f"{datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')} seat={STEM} model={MODEL} "
            f"tool_executed={'OK' if executed_any else 'NO_TOOL'} ballot_seen={'yes' if final_content.strip() else 'no'}")
    print(line)
    sys.exit(0 if executed_any else 1)

# ---------- 正式会话回路（§4.3） ----------
FACE = f'{F21}/face/EV_DIGEST_SLIM_facev21.jsonl'
rows = [json.loads(l) for l in open(FACE)]
assert len(rows) == 45, '卷面行数 != 45'
for r in rows:
    assert 'target_role' not in json.dumps(build_b_prompt(r)), '防泄漏断言失败：target_role 进入提示词'

BDIR = f'{ROOT}/annotation/ballots/{RUNARG}_{STEM}'
TDIR = f'{ROOT}/annotation/toolcalls/{RUNARG}_{STEM}'
os.makedirs(BDIR, exist_ok=True)
os.makedirs(TDIR, exist_ok=True)
DONEF = f'{ROOT}/annotation/.btest_{RUNARG}_{STEM}_done.json'
COSTF = f'{ROOT}/logs/cost_{RUNARG}_{STEM}.jsonl'
done = json.load(open(DONEF)) if os.path.exists(DONEF) else {}

MAX_TURNS = 8
MAX_REMINDERS = 2
MAX_FMT_RETRY = 3
MAX_ATTEMPTS = 3


def run_cluster(row):
    """一个簇的独立会话 → (ballot|None, record)."""
    cid = row['cluster_id']
    rec = {'cid': cid, 'api_calls': 0, 'tool_calls': 0, 'tools': {}, 'turns': 0,
           'reminders': 0, 'forced_final': False, 'prompt_tokens': 0, 'completion_tokens': 0,
           'start_ts': datetime.datetime.now().astimezone().isoformat(), 'pid': os.getpid()}
    calls = []
    t0 = time.time()
    for attempt in range(1, MAX_ATTEMPTS + 1):
        rec['attempts'] = attempt
        messages = [{'role': 'user', 'content': build_b_prompt(row)}]
        n_tool = 0
        n_exec = 0
        fmt_retry = 0
        reminders = 0
        ballot = None
        forced = False
        turn = 0
        while turn < MAX_TURNS:
            turn += 1
            try:
                msg, usage = None, None
                for api_att in range(1, 4):
                    try:
                        msg, usage = call_api(messages)
                        break
                    except Exception as e:
                        rec.setdefault('api_errors', []).append(f'{type(e).__name__}:{str(e)[:80]}')
                        if api_att < 3:
                            time.sleep(15)
                if msg is None:
                    break  # 网络三连败 → 该 attempt 失败
                rec['api_calls'] += 1
                rec['prompt_tokens'] += usage.get('prompt_tokens', 0)
                rec['completion_tokens'] += usage.get('completion_tokens', 0)
            except Exception as e:
                rec.setdefault('api_errors', []).append(f'{type(e).__name__}:{str(e)[:80]}')
                break
            tc = msg.get('tool_calls') or []
            if tc:
                messages.append({'role': 'assistant', 'content': msg.get('content') or '',
                                 'tool_calls': tc})
                for c in tc:
                    fn = c['function']['name']
                    try:
                        a = json.loads(c['function'].get('arguments') or '{}', strict=False)
                    except Exception:
                        a = {}
                    content, executed = exec_tool(fn, a)
                    n_tool += 1
                    if executed:
                        n_exec += 1
                    rec['tool_calls'] += 1
                    rec['tools'][fn] = rec['tools'].get(fn, 0) + 1
                    calls.append({'ts': datetime.datetime.now().astimezone().isoformat(),
                                  'tool': fn, 'args': a, 'executed': executed,
                                  'result_chars': len(content)})
                    messages.append({'role': 'tool', 'tool_call_id': c.get('id', fn),
                                     'name': fn, 'content': content})
                continue
            # 无 tool_calls → 尝试收票
            b = parse_ballot(msg.get('content'), cid)
            if b is not None:
                if n_exec == 0 and reminders < MAX_REMINDERS:
                    reminders += 1
                    rec['reminders'] = reminders
                    messages.append({'role': 'assistant', 'content': msg.get('content') or ''})
                    messages.append({'role': 'user', 'content': REMINDER})
                    continue
                ballot = b
                break
            # 格式错误/无票
            if fmt_retry < MAX_FMT_RETRY:
                fmt_retry += 1
                messages.append({'role': 'assistant', 'content': (msg.get('content') or '')[:500]})
                messages.append({'role': 'user', 'content': '格式错误：只输出一行合法 JSON（字段同输出要求），不要其他文字。'})
                continue
            break
        if ballot is None and n_exec > 0:
            # 轮次耗尽仍未收票 → 强制收尾一次（无工具）
            forced = True
            try:
                messages_forced = messages + [{'role': 'user', 'content': FORCE_FINAL}]
                msg2, usage2 = call_api(messages_forced, with_tools=False)
                rec['api_calls'] += 1
                rec['prompt_tokens'] += usage2.get('prompt_tokens', 0)
                rec['completion_tokens'] += usage2.get('completion_tokens', 0)
                ballot = parse_ballot(msg2.get('content'), cid)
            except Exception as e:
                rec.setdefault('api_errors', []).append(f'forced:{type(e).__name__}:{str(e)[:80]}')
        if ballot is not None and n_exec >= 1:
            rec.update({'turns': turn, 'forced_final': forced, 'outcome': 'OK',
                        'n_exec_tools': n_exec,
                        'wall_s': round(time.time() - t0, 1),
                        'end_ts': datetime.datetime.now().astimezone().isoformat()})
            return ballot, rec, calls
        # attempt 失败 → 记录后重跑（新会话）
        rec.setdefault('attempt_notes', []).append(
            f'attempt{attempt}: n_tool={n_tool} n_exec={n_exec} ballot={"yes" if ballot else "no"} turns={turn} fmt_retry={fmt_retry}')
    rec.update({'turns': turn, 'forced_final': forced, 'outcome': 'PROTOCOL_FAIL',
                'wall_s': round(time.time() - t0, 1),
                'end_ts': datetime.datetime.now().astimezone().isoformat()})
    return None, rec, calls


order = [r['cluster_id'] for r in rows]
failed = []
for i, row in enumerate(rows):
    cid = row['cluster_id']
    if cid in done:
        continue
    ballot, rec, calls = run_cluster(row)
    with open(COSTF, 'a') as f:
        f.write(json.dumps(rec, ensure_ascii=False) + '\n')
    json.dump(calls, open(f'{TDIR}/{cid.replace("::", "_")}.json', 'w'), ensure_ascii=False, indent=1)
    if ballot is None:
        failed.append(cid)
        print(f'[{RUNARG}/{STEM}] {i+1}/45 {cid} PROTOCOL_FAIL — stop', flush=True)
        break
    done[cid] = ballot
    json.dump(ballot, open(f'{BDIR}/{cid.replace("::", "_")}.json', 'w'), ensure_ascii=False)
    json.dump(done, open(DONEF, 'w'), ensure_ascii=False)
    print(f'[{RUNARG}/{STEM}] {i+1}/45 {cid} OK tools={rec["tool_calls"]} api={rec["api_calls"]} {rec["wall_s"]}s', flush=True)

lines = [json.dumps(done[c], ensure_ascii=False) for c in order if c in done]
OUT = f'{ROOT}/annotation/ANN_{STEM}_btest_{RUNARG}.jsonl'
open(OUT, 'w', encoding='utf-8').write('\n'.join(lines) + '\n')
meta = {'model': MODEL, 'stem': STEM, 'run': RUNARG, 'mode': 'btest_freequery',
        'face': FACE, 'face_sha256': hashlib.sha256(open(FACE, 'rb').read()).hexdigest(),
        'prereg_sha256': PREREG_SHA,
        'instructions_sha256': hashlib.sha256(open(FROZEN_INSTR, 'rb').read()).hexdigest(),
        'server_py_sha256': hashlib.sha256(open(f'{MCP_DIR}/server.py', 'rb').read()).hexdigest(),
        'runner_pid': os.getpid(), 'time': datetime.datetime.now().isoformat(),
        'n_rows': len(lines), 'missing': [c for c in order if c not in done],
        'failed': failed}
json.dump(meta, open(f'{ROOT}/annotation/ANN_{STEM}_btest_{RUNARG}_META.json', 'w'), ensure_ascii=False, indent=1)
print(f'WROTE {OUT} rows={len(lines)} missing={len(meta["missing"])}', flush=True)
if meta['missing']:
    sys.exit(2)
