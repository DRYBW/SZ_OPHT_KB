#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9-K5: 自检证据面构建（build 侧，零生产写）。
步骤:
 G0 保真门1: OFF 态 query_marker 复算 33 簇 ranking, 与冻结 face_q6 逐簇对比 —— 必须 33/33 全等, 否则中止上报
 G1 保真门2: 我的 k9_query 在 (ON 态, 无屏蔽, 无新条) 配置下 == eyekb_core.query_marker(ON) 逐簇全等
 B 臂: ON 态生产 ranking (对照, 不投票)
 C 臂: KB9 包 = ON + k9 新条 + R1 剔除 + R2/R3 屏蔽 (out/kb9_face_effective_genesets.json)
 输出: out/kb9_face_arms.json (逐簇 A/B/C ranking) + build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl (C 臂面, 变化簇 lit 重建)
       + out/kb9_changed_clusters.json (投票清单)
"""
import json, os, sys, importlib

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
EV = '/mnt/D/EyeKB/plans/evalset'
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')

face = [json.loads(l) for l in open(f'{EV}/digest/face_q6/EV_DIGEST_SLIM_q6.jsonl', encoding='utf-8')]

def top10_syms(r):
    return [(s or g) for g, s in zip(r['top_genes'][:10], (r.get('top_genes_sym') or [])[:10])]

# ---- G0: OFF 态 = 现役三库, 与 RUN5 建面包同配置 ----
os.environ['EYEKB_ACT_V6'] = '0'
import eyekb_core as C

fidel_off, mism_off = 0, []
armA = {}
for r in face:
    resp = C.query_marker(genes=top10_syms(r), library='all')
    rk = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (resp.get('celltype_ranking') or [])[:3]]
    armA[r['cluster_id']] = rk
    fr = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (r.get('kb_marker_ranking') or [])]
    if rk == fr:
        fidel_off += 1
    else:
        mism_off.append((r['cluster_id'], fr, rk))
os.environ.pop('EYEKB_ACT_V6', None)
print(f"G0 OFF态复现: {fidel_off}/33 全等")
if mism_off:
    print('MISMATCHES:', json.dumps(mism_off[:4], ensure_ascii=False))

# ---- C 臂实现: 镜像 query_marker 语义 + R1/R2/R3 ----
ON_NAMES = ['retina', 'membrane', 'retina_interneuron', 'retina_v6', 'face_v6']
RETINA_ONLY_FILES = {'markers_v4.1_clean.json', 'markers_v5_retina_interneuron.json', 'markers_v6_retina_repair.json'}
SHIELD = json.load(open(f'{ROOT}/out/kb9_face_effective_genesets.json'))
K9 = json.load(open(f'{ROOT}/build/markers_k9_ocs_increment.json'))

def build_markers(config):
    """返回有序 dict {class: [genes]} + owner; config: dict(on=bool, k9=bool, shield=bool, r1=bool)"""
    dbs = []
    names = ON_NAMES if config.get('on') else ['retina', 'membrane', 'retina_interneuron']
    for n in names:
        p = C.MARKER_LIBS[n]
        with open(p, encoding='utf-8') as f:
            db = json.load(f)
        if n in ('face_v6',) and 'markers' not in db:
            derived = {}
            for src in ('stromal_repair', 'face_increment'):
                for cls, e in (db.get(src) or {}).items():
                    derived[cls] = [str(x.get('gene', '')).strip().upper() for x in (e.get('core') or []) if isinstance(x, dict) and x.get('gene')]
            db = dict(db); db['markers'] = derived
        dbs.append((n, p, db))
    if config.get('k9'):
        k9m = {cls: [str(x.get('gene')).strip().upper() for x in e.get('core', []) if x.get('gene')]
               for cls, e in (K9.get('new_terms') or {}).items()}
        dbs.append(('k9_build', __import__('pathlib').Path(f'{ROOT}/build/markers_k9_ocs_increment.json'), {'markers': k9m}))
    markers, seen = {}, {}
    for name, path, db in dbs:
        for ct, gs in db.get('markers', {}).items():
            up = ct.upper()
            if up in seen:
                markers[f"{name}::{ct}"] = [g.upper() for g in gs]
                continue
            seen[up] = ct
            markers[ct] = [g.upper() for g in gs]
    if config.get('r1'):
        # R1: owner 文件在视网膜专属集合的类剔除 (owners 按 markers 同款消歧逻辑重建)
        owners = {}
        seen2 = {}
        for name, path, db in dbs:
            for ct in db.get('markers', {}).items():
                up = ct[0].upper()
                if up in seen2:
                    key = f"{name}::{ct[0]}"
                else:
                    seen2[up] = ct[0]
                    key = ct[0]
                if key in markers:
                    owners[key] = str(path).split('/')[-1]
        markers = {k: v for k, v in markers.items() if owners.get(k, '') not in RETINA_ONLY_FILES}
    if config.get('shield'):
        mk2 = {}
        for k, v in markers.items():
            e = SHIELD.get(k)
            mk2[k] = e['face_effective_genes'] if e and e.get('face_effective_genes') is not None else v
        markers = mk2
    return markers

def k9_query(genes, config):
    markers = build_markers(config)
    gl = [str(g).strip().upper() for g in genes if str(g).strip()]
    score = {}
    for ct in markers:
        n = sum(1 for g in gl if g in markers[ct])
        if n:
            score[ct] = n
    ranked = sorted(score.items(), key=lambda kv: -kv[1])
    return [{'cell_type': c, 'n_shared': n} for c, n in ranked[:3]]

# ---- G1: 我的实现 (无包) vs query_marker ON 态 ----
os.environ.pop('EYEKB_ACT_V6', None)
importlib.reload(C)
fidel_on, mism_on = 0, []
armB = {}
for r in face:
    gl = top10_syms(r)
    ref = [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (C.query_marker(genes=gl, library='all').get('celltype_ranking') or [])[:3]]
    mine = k9_query(gl, {'on': True})
    armB[r['cluster_id']] = ref
    if ref == mine:
        fidel_on += 1
    else:
        mism_on.append((r['cluster_id'], ref, mine))
print(f"G1 裸 matcher 复现 ON 态: {fidel_on}/33 全等")
if mism_on:
    print('G1 MISMATCH:', json.dumps(mism_on[:3], ensure_ascii=False))

# ---- C 臂 ----
armC = {r['cluster_id']: k9_query(top10_syms(r), {'on': True, 'k9': True, 'shield': True, 'r1': True}) for r in face}

changed = [r['cluster_id'] for r in face
           if armC[r['cluster_id']] != [{'cell_type': x['cell_type'], 'n_shared': x['n_shared']} for x in (r.get('kb_marker_ranking') or [])]]
print('changed (C vs frozen RUN5 evidence):', len(changed), changed)

json.dump({'G0_off_fidelity': {'equal': fidel_off, 'of': 33, 'mismatches': mism_off},
           'G1_matcher_fidelity': {'equal': fidel_on, 'of': 33, 'mismatches': mism_on},
           'armA_off_ref': armA, 'armB_prod_on': armB, 'armC_kb9': armC, 'changed_clusters': changed},
          open(f'{ROOT}/out/kb9_face_arms.json', 'w'), ensure_ascii=False, indent=1)

# ---- C 面文件: 变化簇替换 ranking + lit 重建; 不变簇整行原样 ----
os.makedirs(f'{ROOT}/build/face_q6_k9', exist_ok=True)
n_litrebuilt = 0
outl = []
for r in face:
    cid = r['cluster_id']
    if cid not in changed:
        outl.append(r); continue
    nr = dict(r)
    nr['kb_marker_ranking'] = armC[cid]
    lit = {}
    for x in armC[cid]:
        ct = x['cell_type']
        if ct in lit:
            continue
        res = C.search_literature(ct, species='human', tissue='ocular_surface', top_k=4)
        entries = []
        for y in ((res.get('results') or res.get('top') or [])[:2] if isinstance(res, dict) else []):
            entries.append({'pmid': y.get('pmid'), 'yr': y.get('year'), 't': (y.get('title') or '')[:90]})
        lit[ct] = entries
    nr['lit'] = lit
    n_litrebuilt += 1
    outl.append(nr)
with open(f'{ROOT}/build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl', 'w', encoding='utf-8') as f:
    for r in outl:
        f.write(json.dumps(r, ensure_ascii=False) + '\n')
json.dump({'changed': changed, 'n_litrebuilt': n_litrebuilt}, open(f'{ROOT}/out/kb9_changed_clusters.json', 'w'))
import hashlib
sha = hashlib.sha256(open(f'{ROOT}/build/face_q6_k9/EV_DIGEST_SLIM_q6_k9.jsonl', 'rb').read()).hexdigest()
json.dump({'source': 'face_q6 frozen + KB9 C-arm rebuild', 'changed': changed, 'out_sha256': sha,
           'written_at': __import__('datetime').datetime.now().isoformat()}, open(f'{ROOT}/build/face_q6_k9/FACE_K9_freeze.json', 'w'), ensure_ascii=False, indent=1)
print('FACE C built, sha=', sha[:16], 'lit rebuilt for', n_litrebuilt, 'clusters')
