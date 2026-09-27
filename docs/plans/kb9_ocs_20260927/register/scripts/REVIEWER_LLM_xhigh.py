#!/usr/bin/env python3
"""Direct-connection variant of stream_llm.py: bypasses the local proxy and adds reasoning_effort.

Usage:
    python3 stream_llm_direct.py <model> <prompt_file> <out_file> [max_tokens] [base_url]

WHEN TO USE: stream_llm.py is proxy-hardcoded (127.0.0.1:PORT). When the proxy's
outbound path is dead (diagnosis: `curl -x 127.0.0.1:PORT https://www.google.com`
returns 000 while `curl --noproxy '*' https://LLM_CHANNEL/v1/models` returns
401 = reachable), all proxied calls fail with HTTP 502 that is NOT an endpoint
problem. Switch to this script. Key is read at runtime from config.yaml
(LLM_CHANNEL+贵 provider), never hardcoded.

Adds 'reasoning_effort': 'high' to the payload (REVIEWER_LLM final-review default,
2026-09-08 user directive; gpt-5.6-sol callers usually want medium — pass model
accordingly).

Proven: REVIEWER_LLM plan review, 13,359 chars in 3677s, attempt=1 via direct
connection (2026-09-13) after 7 consecutive proxy-path 502s on the same prompt.
"""
import json, re, sys, time, http.client, ssl
import yaml

KEY_SOURCE = '/home/ubuntu/.hermes/profiles/AGENT_ROLE/config.yaml'
DEFAULT_BASE = 'https://LLM_CHANNEL'
UA = 'curl/8.7.1'

def get_key():
    cfg = open(KEY_SOURCE).read()
    m = re.search(r'custom_providers:\s*\n((?:- .*\n|\s+.*\n)*)', cfg)
    providers = yaml.safe_load('custom_providers:\n' + m.group(1))['custom_providers']
    p = [x for x in providers if 'LLM_CHANNEL' in str(x.get('name', '')) and '贵' in str(x.get('name', ''))][0]
    return p.get('api_key') or p.get('key')

def stream_call(key, model, prompt, out_fh, base_url, max_tokens, timeout_s=2400):
    # Direct TLS to the endpoint host; request path must NOT carry the scheme.
    host = base_url.split('//')[1]
    conn = http.client.HTTPSConnection(host, 443, timeout=timeout_s,
                                       context=ssl.create_default_context())
    body = json.dumps({
        'model': model,
        'messages': [{'role': 'user', 'content': prompt}],
        'max_tokens': max_tokens,
        'stream': True,
        'reasoning_effort': 'xhigh',
    }).encode()
    conn.request('POST', '/v1/chat/completions', body=body, headers={
        'User-Agent': UA,
        'Authorization': f'Bearer {key}',
        'Content-Type': 'application/json',
    })
    resp = conn.getresponse()
    if resp.status != 200:
        raise RuntimeError(f'HTTP {resp.status}: {resp.read(2000)[:300]}')
    buf, content, term = b'', '', False
    for chunk in iter(lambda: resp.read(4096), b''):
        buf += chunk
        while b'\n' in buf:
            line, buf = buf.split(b'\n', 1)
            line = line.strip()
            if not line.startswith(b'data:'):
                continue
            data = line[5:].strip()
            if data == b'[DONE]':
                term = True
                break
            try:
                j = json.loads(data)
            except Exception:
                continue
            choices = j.get('choices') or []   # choices can be empty — never index blind
            if not choices:
                continue
            piece = choices[0].get('delta', {}).get('content')
            if piece:
                content += piece
                out_fh.write(piece)
                out_fh.flush()
        if term:
            break
    if not term:
        raise RuntimeError('stream ended without [DONE]')
    return content

def main():
    if len(sys.argv) < 4:
        print(__doc__)
        return 2
    model, prompt_file, out_file = sys.argv[1], sys.argv[2], sys.argv[3]
    max_tokens = int(sys.argv[4]) if len(sys.argv) > 4 else 8000
    base_url = sys.argv[5] if len(sys.argv) > 5 else DEFAULT_BASE
    prompt = open(prompt_file).read()
    key = get_key()
    t0 = time.time()
    for attempt in range(1, 4):
        try:
            with open(out_file, 'w') as fh:
                content = stream_call(key, model, prompt, fh, base_url, max_tokens)
            print(f'OK attempt={attempt} chars={len(content)} secs={time.time()-t0:.0f}', flush=True)
            return 0
        except Exception as e:
            tail = ''
            try:
                tail = open(out_file).read()[-200:]
            except Exception:
                pass
            print(f'FAIL attempt={attempt} {type(e).__name__}: {str(e)[:200]} partial_tail={tail!r}', flush=True)
            time.sleep(10)
    return 1

if __name__ == '__main__':
    sys.exit(main())
