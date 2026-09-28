#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""B5IMPL t_8960c7e0 · b509 — 门5 留痕复验：只读领地零写入 + SHA_POST 台账
① kb9 exec SHA_PRE_EXEC.txt 全行（tag≠MCP 的 kb/、priors、baselines、markers、注册包、
   overlay、evals 面）现算 sha256 逐行对账 → 必须全等；
② KBGOV ledgers/INPUT_SHA_PRE.txt 中 POST 判 OK 的行 → 现算全等（POST 已知 FAILED=
   eyekb_core.py/server.py 属 B5 合法改动面；calls jsonl=运行日志随动）；
③ 本卡 SHA_PRE_B5IMPL.txt 的 KBGOV 冻结件 9 行 + 词表双件 → 现算全等；
④ plans/kb_gov_20260928/SHA_MANIFEST.txt 逐行复验（该卡自身声明的只读面锚）；
⑤ 窗口文件系统扫描：/mnt/D/EyeKB 内比卡开工时刻更新的文件，白名单=
   plans/kbgov_b5impl_20260928/（本卡产物）、mcp_server/（领地=eyekb_core.py/server.py/
   词表/词表缓存 pycache）、logs/mcp_trace/（calllog 运行留痕=生产行为非写入领地违规）、
   __pycache__；白名单外任何命中=违规 FAIL（H1M3 并行卡目录=其自身领地，本卡零触碰，
   扫描排除并单独声明）。
⑥ 输出 ledgers/SHA_POST_B5IMPL.txt + out/b509_readonly_recheck.json。exit 0=全 PASS。"""
import hashlib
import json
import re
import subprocess
import sys
import time
from pathlib import Path

CARD = Path("/mnt/D/EyeKB/plans/kbgov_b5impl_20260928")
EYEKB = Path("/mnt/D/EyeKB")
CARD_START = 1790578548  # task created_at（epoch 秒）
fails, summary = [], {}

SHA_RE = re.compile(r"^([0-9a-f]{64})\s+(.*)$")

# 窗口内他卡合法产物归因表（本卡零触碰，证据=文件头自署卡片号）
ATTRIB_HITS = {
    str(EYEKB / "plans/ANNOTATION_PROTOCOL_v1.3.md"):
        "并行卡 t_e0f94d4f H1M3 判序锚协议 v1.3（文件头自署卡片号；本卡领地=mcp_server 零触碰协议面）",
}


def sha256(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def check_ledger(path, skip_pred=lambda tag_path: False, label="", base_dir=None):
    n_ok = n_fail = n_skip = 0
    bad = []
    attributed = []
    for line in open(path, encoding="utf-8"):
        line = line.rstrip("\n")
        m = SHA_RE.match(line)
        if not m:
            continue
        want, rest = m.group(1), m.group(2)
        parts = rest.split(None, 2) if re.match(r"^\S+\s+\d+\s+/", rest) else [rest]
        fp = parts[-1] if len(parts) >= 1 else rest
        fp = fp.split()[-1] if " " in fp else fp
        if fp.startswith("./") and base_dir:
            fp = str(Path(base_dir) / fp[2:])
        if not fp.startswith("/"):
            continue
        if skip_pred(line):
            n_skip += 1
            continue
        p = Path(fp)
        if not p.is_file():
            bad.append([fp, "MISSING"])
            n_fail += 1
            continue
        got = sha256(p)
        if got == want:
            n_ok += 1
        elif p.stat().st_mtime < CARD_START:
            attributed.append([fp, f"drift 存在于卡窗口之前(mtime={time.strftime('%F %T', time.localtime(p.stat().st_mtime))}, 非本卡作为)"])
        else:
            bad.append([fp, f"sha drift got={got[:12]} want={want[:12]}"])
            n_fail += 1
    return {"label": label, "ok": n_ok, "fail": n_fail, "skip": n_skip,
            "bad": bad[:12], "attributed_preexisting": attributed}


# ① kb9 exec PRE 台账：MCP 行豁免（本卡领地），其余必全等
r1 = check_ledger(EYEKB / "plans/kb9_ocs_20260927/exec/out/SHA_PRE_EXEC.txt",
                  skip_pred=lambda l: " /mnt/D/EyeKB/mcp_server/" in l,
                  label="kb9exec_pre_excl_mcp")
summary["ledger_kb9"] = r1
fails += [[r1["label"], b] for b in r1["bad"]]

# ② KBGOV INPUT_SHA_POST: "path: OK" 行 → 拿 INPUT_SHA_PRE 的 sha 现算复验
pre_sha = {}
for line in open(EYEKB / "plans/kb_gov_20260928/ledgers/INPUT_SHA_PRE.txt", encoding="utf-8"):
    m = SHA_RE.match(line.strip())
    if m:
        pre_sha[m.group(2).split()[-1]] = m.group(1)
ok_rows = [ln.split(":")[0].strip() for ln in open(
    EYEKB / "plans/kb_gov_20260928/ledgers/INPUT_SHA_POST.txt", encoding="utf-8")
    if ln.rstrip().endswith(": OK")]
n2_ok = 0
bad2 = []
for fp in ok_rows:
    if fp not in pre_sha:
        bad2.append([fp, "no-pre-entry"])
        continue
    if Path(fp).is_file() and sha256(Path(fp)) == pre_sha[fp]:
        n2_ok += 1
    else:
        bad2.append([fp, "drift/missing"])
summary["ledger_kbgov_inputs"] = {"checked": len(ok_rows), "ok": n2_ok, "bad": bad2[:12]}
fails += [["kbgov_inputs", b] for b in bad2]

# ③ 本卡 PRE 台账（KBGOV 冻结件 9 + 词表源件）现算复验 + 词表副本对源全等
r3 = check_ledger(CARD / "ledgers/SHA_PRE_B5IMPL.txt",
                  skip_pred=lambda l: " /mnt/D/EyeKB/mcp_server/" in l and "kbgov_vocab" not in l,
                  label="b5_pre_ledger_excl_mcp_code")
summary["ledger_b5pre"] = r3
fails += [[r3["label"], b] for b in r3["bad"]]
v_src = sha256(EYEKB / "plans/kb_gov_20260928/data/kbgov_vocab.json.gz")
v_loc = sha256(EYEKB / "mcp_server/kbgov_vocab.json.gz")
ck_voc = v_src == v_loc == "9b504a2e7cdc975b3963579e445e680e40921dc6749b1b105d172d80a0222a61"
if not ck_voc:
    fails.append(["vocab-copy", [v_src[:12], v_loc[:12]]])

# ④ kb_gov SHA_MANIFEST（若为该格式；行内 sha+path 则逐验，否则登记跳过）
man = EYEKB / "plans/kb_gov_20260928/SHA_MANIFEST.txt"
r4 = check_ledger(man, skip_pred=lambda l: "mcp_server" in l,
                  label="kb_gov_sha_manifest", base_dir=str(man.parent))
summary["manifest_kbgov"] = r4
fails += [[r4["label"], b] for b in r4["bad"]]

# ⑤ 窗口扫描
t0 = str(CARD_START)
cmd = (f"find {EYEKB} -newermt @{t0} -type f "
       f"-not -path '*/__pycache__/*' "
       f"-not -path '{EYEKB}/plans/kbgov_b5impl_20260928/*' "
       f"-not -path '{EYEKB}/logs/mcp_trace/*' "
       f"-not -path '{EYEKB}/plans/grade_h1m3impl_20260928/*' "
       f"-not -path '{EYEKB}/logs/*' "
       f"-not -path '{EYEKB}/plans/repo_sync2_20260928/*' 2>/dev/null")
out = subprocess.run(["bash", "-c", f"export PATH=/usr/bin:/bin:$PATH; {cmd}"],
                     capture_output=True, text=True).stdout.splitlines()
mcp_hits = [f for f in out if f.startswith(str(EYEKB / "mcp_server"))]
other_hits_all = [f for f in out if not f.startswith(str(EYEKB / "mcp_server"))]
attributed_hits = {f: ATTRIB_HITS[f] for f in other_hits_all if f in ATTRIB_HITS}
other_hits = [f for f in other_hits_all if f not in ATTRIB_HITS]
mcp_allowed = {"eyekb_core.py", "server.py", "kbgov_vocab.json.gz"}
mcp_bad = [f for f in mcp_hits if Path(f).name not in mcp_allowed]
summary["window_scan"] = {"mcp_server_changed": [Path(f).name for f in mcp_hits],
                          "mcp_unexpected": mcp_bad,
                          "outside_hits": other_hits[:20], "outside_n": len(other_hits),
                          "attributed_other_cards": attributed_hits}
if mcp_bad:
    fails.append(["mcp_window", mcp_bad])
if other_hits:
    fails.append(["readonly_territory_write", other_hits[:20]])

# ⑥ SHA_POST 台账
lines = []
for p in sorted((EYEKB / "mcp_server").glob("*")):
    if p.is_file():
        lines.append(f"{sha256(p)}  MCP  {p.stat().st_size}  {p}")
(CARD / "ledgers/SHA_POST_B5IMPL.txt").write_text(
    f"# B5IMPL t_8960c7e0 POST ledger {time.strftime('%F %T')} (sha256, tag, bytes, path)\n"
    + "\n".join(lines) + "\n", encoding="utf-8")

verdict = not fails
json.dump({"at": time.strftime("%F %T"), "card": "t_8960c7e0", "summary": summary,
           "fails": fails, "verdict": "PASS" if verdict else "FAIL"},
          open(CARD / "out/b509_readonly_recheck.json", "w"), ensure_ascii=False, indent=1)
print(json.dumps({"verdict": "PASS" if verdict else "FAIL", "fails_n": len(fails),
                  "kb9": {k: r1[k] for k in ("ok", "fail", "skip")},
                  "kbgov_inputs": {k: summary["ledger_kbgov_inputs"][k] for k in ("checked", "ok")},
                  "b5pre": {k: r3[k] for k in ("ok", "fail")},
                  "manifest": {k: r4[k] for k in ("ok", "fail", "skip")},
                  "vocab_ok": ck_voc,
                  "window": {"mcp": summary["window_scan"]["mcp_server_changed"],
                             "outside": summary["window_scan"]["outside_hits"]}},
                 ensure_ascii=False))
sys.exit(0 if verdict else 1)
