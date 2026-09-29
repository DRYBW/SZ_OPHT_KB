#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""REPOSYNC6 t_5112f6d9 · 八门电池（判据沿 RS5 同型；领地=RS6 任务书：composition v1 两件 + comp_prior_v1 全目录 + QUEUE/WIKI 09-29 增补 + 本卡证据）。
T7 needle 运行期拼装（本脚本自净）。输出=out/t1..t8 证据件 + out/gates_summary.json。
与 RS5 的关键差异=T1 领地剔除反转：COMPV1 v1 面本轮**必须**入仓（正断言）；冻结清单复用 rs5 154 件。"""
import hashlib
import json
import os
import re
import subprocess
import sys
from collections import Counter
from pathlib import Path

_ROOT = Path(__file__).resolve().parent
while _ROOT != _ROOT.parent and not (_ROOT / ".git").exists():
    _ROOT = _ROOT.parent
STG = Path(os.environ.get("EYEKB_STG", str(_ROOT)))
CARD = STG / "docs/plans/repo_sync6_20260929"
OUT = CARD / "out"
OUT.mkdir(parents=True, exist_ok=True)
WORK = Path("/tmp/rs6_work")
ENGINE = str(Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py")  # 引擎按路径调用（不镜像入仓）
RES = {}

TEXT_EXT = {".md", ".json", ".yaml", ".txt", ".tsv", ".py", ".sh", ".log", ".jsonl",
            ".out", ".err", ".list", ".sha256", ".csv", ".yaml"}

# ---------- T1 领地锁定：只写任务书范围（M=修改面，??/A=新增面）；正断言 COMPV1 面已入仓 ----------
allowed_new = ("kb/composition/EXPECTED_COMPOSITION_v1.", "docs/plans/comp_prior_v1_20260929/",
               "docs/plans/repo_sync6_20260929/", "__ALLOW_UNUSED__")
allowed_mod = ("docs/plans/QUEUE_20260929.md", "kb/composition/SHA256SUMS.txt")
bad_struct = []
for line in subprocess.run(["git", "status", "--short", "-uall"], cwd=str(STG), capture_output=True, text=True).stdout.splitlines():
    raw = line[3:]
    p = raw.strip()
    if p.startswith('"') and p.endswith('"'):
        p = p[1:-1].encode("utf-8", "surrogateescape").decode("unicode_escape")
    st = line[:2].strip()
    if st in ("M", "MM"):
        if p not in allowed_mod:
            bad_struct.append(("MOD-OUTSIDE-SCOPE", p))
        continue
    if st == "D":
        bad_struct.append(("DELETED-TRACKED", p))
        continue
    rp = STG / p
    try:
        rpr = rp.resolve()
        if OUT == rpr or OUT in rpr.parents:
            continue  # 本卡 out/ 证据件=门运行时产物豁免
    except Exception:
        pass
    if not p.startswith(allowed_new):
        bad_struct.append(("NEW-OUTSIDE-SCOPE", p))
# 正断言：COMPV1 回收面在位
need = [STG / "kb/composition/EXPECTED_COMPOSITION_v1.json", STG / "kb/composition/EXPECTED_COMPOSITION_v1.md"]
need += [STG / "docs/plans/comp_prior_v1_20260929" / x for x in
         ["V1_VERDICT.md", "PHASE0_INVENTORY_t_37a35220.md", "MANIFEST_sha256.txt",
          "ob1_lit_candidates.tsv", "residual_attribution_xtab.tsv", "os_conditional_intervals.json",
          "retina_conditional_intervals.json", "retina_strata_units.tsv", "q6_recompute_os.tsv",
          "stratified_recompute_rows.tsv", "stratified_recompute_rows_v2.tsv", "stratified_recompute_summary.tsv"]]
need += sorted((STG / "docs/plans/comp_prior_v1_20260929/scripts").glob("*.py"))
need += sorted((STG / "docs/plans/comp_prior_v1_20260929/logs").glob("*"))
missing = [str(p.relative_to(STG)) for p in need if not p.is_file()]
n_tree = sum(1 for p in (STG / "docs/plans/comp_prior_v1_20260929").rglob("*") if p.is_file())
t1_ok = not bad_struct and not missing and n_tree >= 26
RES["T1"] = {"pass": t1_ok, "violations": bad_struct, "missing_recyclables": missing, "comp_prior_v1_files_in_repo": n_tree}
print(f"T1 领地锁定: {'PASS' if t1_ok else 'FAIL'} (violations={len(bad_struct)}, missing={len(missing)}, tree_files={n_tree})")
for x in (bad_struct + missing)[:6]:
    print("   T1-FLAG:", x)

# ---------- T2 冻结面不变：154 件 sha 前后全等（复用 rs5 清单）----------
before = {}
for line in (WORK / "sha_before.txt").read_text().splitlines():
    h, _, f = line.partition("  ")
    before[f.strip()] = h.strip()
after = {}
for f in before:
    p = STG / f
    after[f] = hashlib.sha256(p.read_bytes()).hexdigest() if p.exists() else "MISSING"
diff2 = [f for f in before if before[f] != after[f]]
t2_ok = not diff2
RES["T2"] = {"pass": t2_ok, "files_compared": len(before), "changed": diff2}
print(f"T2 冻结面: {'PASS' if t2_ok else 'FAIL'} ({len(before)} 件 evals/tests/kb/mcp_server/rag_snapshots 前后全等, changed={len(diff2)})")

# ---------- T3 v4 幂等引擎扫描 scan=0（全仓 docs 面，含新收面）----------
r = subprocess.run([sys.executable, ENGINE, "--scan"], cwd=STG, capture_output=True, text=True,
                   env=dict(os.environ, EYEKB_STG=str(STG)))
(WORK / "t3_engine_scan.tmp.txt").write_text(r.stdout + r.stderr, encoding="utf-8")
hits_m = re.search(r"== 命中文件数: (\d+) ==", r.stdout)
scan_zero = bool(hits_m) and int(hits_m.group(1)) == 0
src = (Path(os.path.expanduser("~")) / "eyekb_desensitize_v4_reposync3.py").read_text(encoding="utf-8")
ns = {"re": re, "BRAND": "as" + "tra"}
exec(re.search(r"^RULES = \[.*?^\]", src, re.S | re.M).group(0), ns)
STRICT = {
    "BRAND-1": "as" + "tra", "BRAND-2": ("bai" + "lian").lower(),
    "BRAND-3": "".join(map(chr, [0x767E, 0x70BC])), "BRAND-4": ("".join(map(chr, [0x80A5, 0x732B]))),
    "BRAND-5": "fei" + "mao", "BRAND-6": ("999555" + "999"), "BRAND-7": ("api" + "key.fun"),
    "BRAND-8": ("ubuntu-X" + "12DAi"), "BRAND-9": ("pi" + "-chief"),
    "BRAND-10": "".join(map(chr, [0x4F01, 0x4E1A, 0x5FAE, 0x4FE1])),
    "BRAND-11": (r"BMR" + r"\d{6,}"),
}
CJK = re.compile(r"[\u4e00-\u9fff]")
# 门体系自身（rs5/rs6 脚本，needle 运行期拼装=合法持有者）自净豁免（台账登记）
SELFCLEAN_EARLY = {"rs5_gates.py", "rs5_wiki_mask.py", "rs5_pathnorm.py", "rs5_pathnorm_revert.py",
                   "rs5_finalize_mask.py", "rs5_card_detokenize.py", "rs5_manifest_reanchor.py",
                   "rs5_t6_clone.py", "rs6_gates.py", "rs6_pathnorm.py", "rs6_t6_clone.py",
                   "rs6_ingest.py", "rs6_finalize_mask.py", "t7_own_tokens_rs5.py"}


def cjk_adjacent_hits(text, needle):
    out = 0
    for m in re.finditer(re.escape(needle), text, re.I):
        prev = text[m.start() - 1] if m.start() else ""
        nxt = text[m.end()] if m.end() < len(text) else ""
        if (prev.isascii() and prev.isalnum()) or (nxt.isascii() and nxt.isalnum()):
            continue
        if CJK.search(prev + nxt):
            out += 1
    return out


strict_hits = []
for d in ["docs/wiki", "docs/skills", "docs/plans", "mcp_server", "README.md"]:
    base = STG / d
    it = [base] if base.is_file() else [Path(rt) / f for rt, _ds, fs in os.walk(base) for f in fs if "__pycache__" not in rt]
    for p in it:
        if not p.is_file() or p.suffix not in TEXT_EXT:
            continue
        if "out/" in str(p.relative_to(STG)) or p.name in SELFCLEAN_EARLY:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        for k, nd in STRICT.items():
            n = len(re.findall(nd, t)) if "\\" in nd else cjk_adjacent_hits(t, nd)
            if n:
                strict_hits.append((str(p.relative_to(STG)), k, n))
t3_ok = scan_zero and not strict_hits
(OUT / "t3_v4_engine_scan.txt").write_text((WORK / "t3_engine_scan.tmp.txt").read_text(encoding="utf-8"), encoding="utf-8")
RES["T3"] = {"pass": t3_ok, "engine_scan_zero": scan_zero, "cjk_strict_hits": strict_hits[:10],
             "cjk_strict_count": len(strict_hits)}
print(f"T3 v4 幂等扫描: {'PASS' if t3_ok else 'CHECK'} (engine-hitfiles={hits_m and hits_m.group(1)}, cjk-strict={len(strict_hits)})")
for x in strict_hits[:8]:
    print("   STRICT-HIT:", x)

# ---------- T4 T7 敏感扫描永久门 HARD=0（ADVISORY 通名沿 PI 口径）----------
P_A = re.compile(chr(66) + chr(77) + chr(82) + r"\d{6,}")
P_B = re.compile(r"\b" + chr(89) + chr(65) + chr(83) + r"[-_ ]?\d")
P_C = re.compile("".join(map(chr, [0x5EB7, 0x67CF, 0x897F, 0x666E])))
P_C_adv = re.compile(r"(?i)" + "con" + "ber" + "cept")
P_D = re.compile(r"(?i)" + "DR" + r"[-_]" + "AGI" + "NG")
P_E = re.compile(r"(?i)" + "aging" + "_" + "comor" + "bid")
P_F = re.compile(r"(?i)(?:Pha" + "se" + "1|DR_" + "PHASE" + "1)")
P_G = re.compile("leak" + "_" + "adj")
P_H = re.compile(r"\bDR(1|2|3|4|5|6|7|8|9|10|11|12)\b(?![A-Za-z])")
TOK = {"CAT-A": P_A, "CAT-B": P_B, "CAT-C": P_C, "CAT-C-adv": P_C_adv, "CAT-D": P_D,
       "CAT-E": P_E, "CAT-F": P_F, "CAT-G": P_G, "CAT-H": P_H}
CTX = re.compile("样本|患者|病例|编号|取材|队列|眼底|donor|Donor|STZ|cohort|sample[ _]id")
NEG = re.compile("通名|可留|非本项目|文献")
WRITE_SURF = ["docs", "mcp_server", "README.md", "figures"]
INV_SURF = ["scripts", "tests", "evals", "clients", "rag_snapshots", "kb"]
SKIP_KEY = "docs/plans/repo_sync6_20260929/out/"
SELFCLEAN = SELFCLEAN_EARLY


def scan_file(p):
    try:
        t = p.read_text(encoding="utf-8", errors="ignore")
    except Exception:
        return []
    hits = []
    for cat, rx in TOK.items():
        for m in rx.finditer(t):
            ctx = t[max(0, m.start() - 120): m.end() + 120]
            if cat == "CAT-H":
                kind = "ADVISORY" if NEG.search(ctx) else ("HARD" if CTX.search(ctx) else "ADVISORY")
            elif cat.endswith("-adv"):
                kind = "ADVISORY"
            else:
                kind = "HARD"
            hits.append((cat, kind))
    return hits


def walk(base):
    if base.is_file():
        yield base
        return
    for root, ds, fs in os.walk(base):
        ds[:] = [x for x in ds if x != "__pycache__"]
        for f in fs:
            p = Path(root) / f
            if SKIP_KEY in str(p.relative_to(STG)):
                continue
            yield p


rows, purges, inv = [], [], []
for surf in WRITE_SURF:
    for p in walk(STG / surf):
        if p.suffix and p.suffix not in TEXT_EXT:
            continue
        if p.name in SELFCLEAN:
            continue
        for cat, kind in scan_file(p):
            rel = str(p.relative_to(STG))
            rows.append((rel, cat, kind))
            if kind == "HARD":
                purges.append(rel)
for surf in INV_SURF:
    for p in walk(STG / surf):
        if p.suffix not in TEXT_EXT:
            continue
        hc = [h for h in scan_file(p) if h[1] == "HARD"]
        if hc:
            inv.append((str(p.relative_to(STG)), len(hc)))
purges = sorted(set(purges))
cc = Counter(r[1] for r in rows if r[2] == "HARD")
(OUT / "t4_T7_scan.tsv").write_text("relpath\tcategory\tkind\n" + "\n".join("\t".join(r) for r in rows) + "\n",
                                    encoding="utf-8")
t4_ok = not purges and not inv
RES["T4"] = {"pass": t4_ok, "write_hard_files": purges, "hard_categories": dict(cc),
             "advisory": sum(1 for r in rows if r[2] == "ADVISORY"), "inventory_hard": inv}
print(f"T4 T7 token 门: {'PASS' if t4_ok else 'FAIL'} (HARD={len(purges)} files, ADVISORY={RES['T4']['advisory']}, 镜像面 HARD={len(inv)})")
for x in purges[:10]:
    print("   HARD:", x)

# ---------- T5 黄金 41（外部 systemd-run 跑；此处收证据）----------
ev = WORK / "t5_golden41_evidence.txt"
t5_pass = ev.exists() and "REPRO PASS: 41/41" in ev.read_text()
(OUT / "t5_golden41.txt").write_text(ev.read_text() if ev.exists() else "PENDING", encoding="utf-8")
RES["T5"] = {"pass": t5_pass, "note": "tests/verify_repro.py @ training-venv 锁版, db=本地 Release 预置件 RAG_SLIM_V242, systemd-run --user MemoryMax=8G MemorySwapMax=0 托管 unit=rs6-t5-golden41"}
print("T5 黄金41:", "PASS 41/41" if t5_pass else "FAIL/PENDING")

# ---------- T6 新鲜克隆（commit-tree 预检 commit 后由 rs6_t6_clone.py 跑，先占位）----------
t6f = OUT / "t6_fresh_clone.txt"
RES["T6"] = {"pass": t6f.exists() and "T6-PASS" in t6f.read_text(), "evidence": str(t6f)}
print("T6 新鲜克隆:", "见 t6_fresh_clone.txt" if t6f.exists() else "待预检 commit 后执行")

# ---------- T7 人查台账：token 化面零机器路径/零凭据 + 逐新增件 sha 台账 ----------
pat_home = re.compile(r"/home/ubuntu/|/mnt/[A-Za-z]/")
pat_secret = re.compile(r"sk-[a-zA-Z0-9]{16,}|github_" + "pat_|gh[opu]s?_[A-Za-z0-9]{16,}|-----BEGIN")
TOKN_SURF = [STG / "docs/plans/QUEUE_20260929.md",
             STG / "docs/plans/repo_sync6_20260929/BRIEF_REPOSYNC6.md"]
T7_EXEMPT = {"BRIEF_REPOSYNC6.md": "任务书 T4 门条款凭据模式枚举字面（描述文本非凭据值），"
                                   "沿 RS5 对 BRIEF_REPOSYNC5.md 豁免先例，登记 ledgers/T7_EXCLUSIONS_RS6.tsv"}
t7_hits = []
for base in TOKN_SURF:
    for p in ([base] if base.is_file() else [q for q in Path(base).rglob("*") if q.is_file()]):
        if p.suffix not in TEXT_EXT or "__pycache__" in str(p):
            continue
        if p.parent == OUT or OUT in p.parents:
            continue
        if p.name in SELFCLEAN or p.name in T7_EXEMPT:
            continue
        t = p.read_text(encoding="utf-8", errors="ignore")
        h1 = len(pat_home.findall(t))
        h2 = len(pat_secret.findall(t))
        if h2:
            t7_hits.append((str(p.relative_to(STG)), "SECRET", h2))
        if h1:
            t7_hits.append((str(p.relative_to(STG)), "ABS-PATH", h1))
# 逐新增件 sha 台账（本轮全部入仓件 + 修改面）
led_rows = []
newsets = [(STG / "kb/composition/EXPECTED_COMPOSITION_v1.json",), (STG / "kb/composition/EXPECTED_COMPOSITION_v1.md",)]
for p in sorted((STG / "docs/plans/comp_prior_v1_20260929").rglob("*")):
    if p.is_file():
        led_rows.append((str(p.relative_to(STG)), hashlib.sha256(p.read_bytes()).hexdigest()))
for p in sorted((CARD).rglob("*")):
    if p.is_file() and "/out/" not in str(p):
        led_rows.append((str(p.relative_to(STG)), hashlib.sha256(p.read_bytes()).hexdigest()))
for p in [STG / "docs/plans/QUEUE_20260929.md", STG / "kb/composition/SHA256SUMS.txt"]:
    led_rows.append((str(p.relative_to(STG)) + "  # MODIFIED", hashlib.sha256(p.read_bytes()).hexdigest()))
(OUT / "t7_sha_ledger.tsv").write_text("relpath\tsha256\n" + "\n".join(f"{a}\t{b}" for a, b in led_rows) + "\n",
                                       encoding="utf-8")
RES["T7"] = {"pass": not t7_hits, "machine_check": t7_hits[:10], "ledger_rows": len(led_rows),
             "human_review_note": "masked 件逐件=ledgers/T7_EXCLUSIONS_RS6.tsv；证据镜像面机器路径=沿 RS3/RS5 先例字节直收豁免登记；BRIEF6/QUEUE=rs6_pathnorm token 化后零残留（t2b 台账）"}
print(f"T7 mask 人查(机检面): {'PASS' if not t7_hits else 'CHECK'} (ledger={len(led_rows)} 件)")
for x in t7_hits[:10]:
    print("   T7-FLAG:", x)

# ---------- T8 commit 拓扑（预检 commit 校验；正式 commit 后终态复跑记录于卡）----------
t8f = OUT / "t8_topology.txt"
RES["T8"] = {"pass": t8f.exists() and "T8-PASS" in t8f.read_text(), "evidence": str(t8f)}
print("T8 拓扑:", "见 t8_topology.txt" if t8f.exists() else "待预检 commit 后执行")

# ---------- T0 >50MB 清单（不收，登记；预期本轮零大件）----------
big = []
for root in [STG / "docs/plans/comp_prior_v1_20260929", STG / "kb/composition"]:
    for p in Path(root).rglob("*"):
        if p.is_file() and p.stat().st_size > 50 * 1024 * 1024:
            big.append({"path": str(p), "bytes": p.stat().st_size})
(OUT / "t0_large_files_excluded.tsv").write_text(
    "path\tbytes\n" + ("\n".join(f"{b['path']}\t{b['bytes']}" for b in big) if big else "# 本轮拟收面最大件 <25KB，>50MB 零件（源侧扫描同结论，见 COMPLETED §三）") + "\n",
    encoding="utf-8")

(OUT / "gates_summary.json").write_text(json.dumps(RES, ensure_ascii=False, indent=1), encoding="utf-8")
done = [k for k in ("T1", "T2", "T3", "T4", "T5", "T7") if RES[k]["pass"]]
print(f"\n即时六门: {len(done)}/6 PASS ({','.join(done)})  | T6/T8 待预检 commit 后")
sys.exit(0 if len(done) == 6 else 1)
