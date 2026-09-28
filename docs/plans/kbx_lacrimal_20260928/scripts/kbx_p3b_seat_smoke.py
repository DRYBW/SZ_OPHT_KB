#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KBX 三席冒烟探针（§7.1：起跑前各 1 次；记录 logs/seat_smoke.txt）。
只发一条极小 prompt，不计票不占配额语义（票=正式批次）。"""
import json, os, re, sys, time, urllib.request

cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)
SEATS = {'A': 'qwen3.8-max', 'B': 'glm-5.1', 'C': 'deepseek-v3.2'}
out = []
for stem, model in SEATS.items():
    body = {'model': model, 'messages': [{'role': 'user', 'content': '只回复两个字：可用'}],
            'temperature': 0.2, 'max_tokens': 50}
    if model.startswith('qwen'):
        body['enable_thinking'] = False
    req = urllib.request.Request(base_url.rstrip('/') + '/chat/completions',
                                 data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json', 'Authorization': 'Bearer ' + api_key})
    for att in range(3):
        try:
            t0 = time.time()
            resp = json.load(urllib.request.urlopen(req, timeout=120))
            txt = (resp['choices'][0]['message'].get('content') or resp['choices'][0]['message'].get('reasoning_content') or '').strip()
            out.append(f'{stem} {model} OK {time.time()-t0:.1f}s reply={txt[:20]!r}')
            break
        except Exception as e:
            if att == 2:
                out.append(f'{stem} {model} FAIL {type(e).__name__} {str(e)[:60]}')
            else:
                time.sleep(10)
    time.sleep(2)
msg = '\n'.join(out)
print(msg)
open('/mnt/D/EyeKB/plans/kbx_lacrimal_20260928/logs/seat_smoke.txt', 'w').write(msg + '\n')
sys.exit(0 if all(' OK ' in l for l in out) else 3)
