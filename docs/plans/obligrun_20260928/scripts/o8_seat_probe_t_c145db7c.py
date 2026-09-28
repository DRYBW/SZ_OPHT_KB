#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN-ADD (t_c145db7c run142, PREREG §4 执行序3): 三席 enable_thinking:false 参数探针。
非票面 ping（零票面内容，不产票，不计票预算，逐席登记 logs/seat_probe_<stem>.json）。
qwen 席必带该参；其余席带参=报错则降为不带并登记偏差（不算球门失败）。"""
import json, os, re, sys, time, urllib.request

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)
SEATS = {'A': 'qwen3.8-max', 'B': 'glm-5.1', 'C': 'deepseek-v3.2'}


def call(model, with_param, tmo=120):
    body = {'model': model, 'messages': [{'role': 'user', 'content': '只回复两个字：可用'}],
            'temperature': 0.2, 'max_tokens': 50}
    if with_param:
        body['enable_thinking'] = False
    req = urllib.request.Request(base_url.rstrip('/') + '/chat/completions',
                                 data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key})
    t0 = time.time()
    resp = json.load(urllib.request.urlopen(req, timeout=tmo))
    msg = resp['choices'][0]['message']
    txt = (msg.get('content') or msg.get('reasoning_content') or '').strip()
    return txt, round(time.time() - t0, 1)


results = {}
for stem, model in SEATS.items():
    rec = dict(model=model, param_enable_thinking_false=True, attempts=[])
    ok = None
    for att in range(1, 4):
        try:
            txt, dur = call(model, True)
            rec['attempts'].append(dict(att=att, with_param=True, ok=True, reply=txt[:24], dur_s=dur))
            ok = True
            break
        except Exception as e:
            rec['attempts'].append(dict(att=att, with_param=True, ok=False, err=f'{type(e).__name__}:{str(e)[:120]}'))
            time.sleep(10)
    if ok is None and not model.startswith('qwen'):
        # 偏差路径：拒收参数→降为不带并登记（PREREG §4 原文）
        for att in range(1, 3):
            try:
                txt, dur = call(model, False)
                rec['param_enable_thinking_false'] = False
                rec['deviation'] = '带参连续 3 次失败→降为不带（如实登记通道约束，非球门失败）'
                rec['attempts'].append(dict(att='fallback-no-param', with_param=False, ok=True, reply=txt[:24], dur_s=dur))
                ok = True
                break
            except Exception as e:
                rec['attempts'].append(dict(att='fallback-no-param', with_param=False, ok=False, err=f'{type(e).__name__}:{str(e)[:120]}'))
                time.sleep(10)
    rec['probe_ok'] = bool(ok)
    json.dump(rec, open(f'{ROOT}/logs/seat_probe_{stem}.json', 'w'), ensure_ascii=False, indent=1)
    print(stem, model, 'OK' if ok else 'FAIL', '| param_kept=', rec['param_enable_thinking_false'], flush=True)
    time.sleep(2)

sys.exit(0 if all(json.load(open(f'{ROOT}/logs/seat_probe_{s}.json'))['probe_ok'] for s in SEATS) else 3)
