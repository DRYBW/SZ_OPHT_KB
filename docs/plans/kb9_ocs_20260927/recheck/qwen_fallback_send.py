#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9R 降级件：qwen3.8-max（LLM_CHANNEL通道）代审设计复核。
PI 预授权（USER_DIRECTIVE_20260927_scoring_wave.md 追加一 D6a）：LLM_CHANNEL 503 时降级
qwen3.8max，enable_thinking:false，长输出必 stream=True。
用法: python3 qwen_fallback_send.py <prompt_file> <out_file>
仅当主通道 REVIEWER_LLM 连败时使用；产物头登"临时裁定者"，不冒充 REVIEWER_LLM。
"""
import json, re, sys, time, os, urllib.request

PROMPT_F, OUT_F = sys.argv[1], sys.argv[2]
MODEL = 'qwen3.8-max'

cfg = open(os.path.expanduser('~/.hermes/profiles/AGENT_ROLE/config.yaml'), encoding='utf-8').read()
m = re.search(r'name: LLM_CHANNEL.*?base_url: (\S+).*?api_key: (\S+)', cfg, re.S)
base_url, api_key = m.group(1), m.group(2)

prompt = open(PROMPT_F, encoding='utf-8').read()
SYS = ('你是独立的生物信息学与统计方法学审稿人。以最高标准独立复核，不预设任何结论。'
       '【重要】你没有任何工具、终端、文件系统或容器——你无法执行任何命令。'
       '所有待审材料已完整包含在用户消息中。直接用纯文本输出审查意见，禁止输出任何 JSON 命令格式。请用中文回答。')

def stream_call(out_fh, timeout_s=2400, max_attempts=3):
    body = {
        'model': MODEL,
        'messages': [{'role': 'system', 'content': SYS}, {'role': 'user', 'content': prompt}],
        'max_tokens': 16000,
        'stream': True,
        'enable_thinking': False,
    }
    req = urllib.request.Request(base_url.rstrip('/') + '/chat/completions',
                                 data=json.dumps(body).encode('utf-8'),
                                 headers={'Content-Type': 'application/json',
                                          'Authorization': 'Bearer ' + api_key})
    last = None
    for attempt in range(1, max_attempts + 1):
        try:
            content = ''
            with urllib.request.urlopen(req, timeout=timeout_s) as resp:
                for raw in resp:
                    line = raw.strip()
                    if not line.startswith(b'data:'):
                        continue
                    data = line[5:].strip()
                    if data == b'[DONE]':
                        out_fh.flush()
                        return content, attempt
                    try:
                        j = json.loads(data)
                    except Exception:
                        continue
                    c = (j.get('choices', [{}])[0].get('delta') or {}).get('content') or ''
                    if c:
                        content += c
                        out_fh.write(c)
                        out_fh.flush()
            # stream ended without [DONE] but with content -> accept if substantial
            if len(content) > 2000:
                return content, attempt
            raise RuntimeError('stream ended without [DONE] and content too short')
        except Exception as e:
            last = e
            print(f'FAIL attempt={attempt} {type(e).__name__}: {str(e)[:200]}', flush=True)
            time.sleep(30)
    raise RuntimeError(f'all attempts failed: {last}')

t0 = time.time()
for attempt in range(1, 4):
    try:
        with open(OUT_F, 'w', encoding='utf-8') as fh:
            content, inner = stream_call(fh)
        print(f'OK attempt={attempt} chars={len(content)} secs={time.time()-t0:.0f}', flush=True)
        sys.exit(0)
    except Exception as e:
        print(f'OUTER FAIL attempt={attempt}: {str(e)[:200]}', flush=True)
        time.sleep(60)
sys.exit(1)
