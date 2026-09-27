#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec6 v2 — 仓镜像同步（脱敏管线同 REPOSYNC，push 前停手报协调者）
本卡教训固化：09-27 REPOSYNC 扫描面 DIRS 未含 kb/ → kb 历史件含 R08/REVIEWER_LLM、R12/AGENT_ROLE
形态命中（3k+ 处）且已随字节镜像 push 至远端。本卡处置：
  ① 脱敏 apply 严格限定=本卡同步件（DESENS_ONLY 过滤）；
  ② kb 历史面命中=全量清单登记（仓外 tsv + 仓内代号版报告 + 卡片汇报），修不修=协调者/PI 裁定，本卡不擅动；
  ③ 全树 inventory 用 dv3 提取的同一 RULES 清单（ast 解析源码字面量，不另写正则，防漂移）。
流程：SYNC copy→全量 scan 登记→限定 apply→kb+mcp 对账新表→README→分层 commit×4+补录→终检门(限本卡面)。"""
import ast
import hashlib
import os
import re
import subprocess
import sys
from datetime import datetime
from pathlib import Path

REPO = Path("/home/ubuntu/EYEKB_REPO")
ONLINE = Path("/mnt/D/EyeKB")
WIKI = Path("/mnt/D/OcularKB/WIKI")
CARD = ONLINE / "plans/kb9_ocs_20260927"
PY = sys.executable
RAW = CARD / "exec/desens_raw"
RAW.mkdir(parents=True, exist_ok=True)


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd, **kw):
    return subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)


run(f"git -C {REPO} checkout -- .")  # 前轮部分 apply 的 tracked 面还原（本卡 SYNC 会重拷权威原件）
por = run(f"git -C {REPO} -c core.quotepath=false status --porcelain -uall").stdout.splitlines()
tracked_mod = [l for l in por if not l.startswith("??")]
assert not tracked_mod, "repo tracked 面 checkout 后仍不干净:\n" + "\n".join(tracked_mod[:5])
untracked = [l[3:].strip() for l in por if l.startswith("??")]
# 本卡前轮半成品（同一 TSV 稍后由步骤③整体重生成）——先摘除防误判
_left = REPO / "docs/recon/RECON_kb_mcp_20260928.tsv"
if _left.exists():
    _left.unlink()
print(f"[0] repo: tracked 还原干净, 前轮 untracked 副本 {len(untracked)} 件将被本 run 覆盖")

# ---- ① SYNC ----
SYNC = [
    (ONLINE / "kb/markers/markers_k9_ocs_increment.json", "kb/markers/markers_k9_ocs_increment.json"),
    (ONLINE / "kb/markers/_k9_ocs_rules_overlay_v1.json", "kb/markers/_k9_ocs_rules_overlay_v1.json"),
    (ONLINE / "mcp_server/eyekb_core.py", "mcp_server/eyekb_core.py"),
    (ONLINE / "mcp_server/server.py", "mcp_server/server.py"),
    (WIKI / "数据资产.md", "docs/wiki/数据资产.md"),
    (WIKI / "决策记录.md", "docs/wiki/决策记录.md"),
    (WIKI / "体系盘点_MCP-RAG-Wiki-Skill_20260924.md", "docs/wiki/体系盘点_MCP-RAG-Wiki-Skill_20260924.md"),
    (WIKI / "检索索引.md", "docs/wiki/检索索引.md"),
    (CARD / "BRIEF_KB9REG_EXEC.md", "docs/plans/kb9_ocs_20260927/BRIEF_KB9REG_EXEC.md"),
]
for sub in ("exec/scripts", "exec/out", "exec/pre_images"):
    d = CARD / sub
    if d.is_dir():
        for f in sorted(d.rglob("*")):
            if f.is_file() and "__pycache__" not in str(f) and "desens_raw" not in str(f):
                SYNC.append((f, f"docs/plans/kb9_ocs_20260927/{f.relative_to(CARD)}"))
for f in sorted((CARD / "ledgers/ols_evidence_kb9").glob("*t4bb75b26*")):
    SYNC.append((f, f"docs/plans/kb9_ocs_20260927/ledgers/ols_evidence_kb9/{f.name}"))
# 线上权威 sha 台账
nm = [f"# KB9REG-EXEC t_4bb75b26 新产物与改动件 sha256（线上权威原件） {datetime.now():%F %T}"]
for src, rel in SYNC:
    p = Path(src)
    tag = "NEW" if (str(p).endswith((".json",)) and "markers_k9" in p.name or "_rules_overlay" in p.name
                    or "/exec/" in str(p) or "t4bb75b26" in p.name or "pre_images" in str(p)) else "MOD"
    nm.append(f"{sha(p)}  {tag}  {rel}")
(CARD / "exec/out/SHA_NEW_AND_MODIFIED.txt").write_text("\n".join(nm) + "\n", encoding="utf-8")
SYNC.append((CARD / "exec/out/SHA_NEW_AND_MODIFIED.txt", "docs/plans/kb9_ocs_20260927/exec/out/SHA_NEW_AND_MODIFIED.txt"))

MY_TARGETS = set()
for src, rel in SYNC:
    dst = REPO / rel
    dst.parent.mkdir(parents=True, exist_ok=True)
    dst.write_bytes(Path(src).read_bytes())
    assert sha(dst) == sha(src), f"copy 校验失败 {rel}"
    MY_TARGETS.add(rel)
print(f"[1] synced {len(SYNC)} files, byte-verified")

# ---- ② 脱敏：全量 inventory（同 RULES，ast 提取）+ 限定 apply ----
dv2_src = Path("/home/ubuntu/eyekb_desensitize_v2.py").read_text(encoding="utf-8")
tree = ast.parse(dv2_src)
RULES = None
for node in tree.body:
    if isinstance(node, ast.Assign) and getattr(node.targets[0], "id", "") == "RULES":
        RULES = ast.literal_eval(node.value)
assert RULES and len(RULES) == 16, "RULES 提取失败"
PROSE_ONLY = {".md", ".txt", ".log", ".err", ".out", ".py", ".sh"}
TEXT_EXT = {".md", ".json", ".yaml", ".txt", ".tsv", ".py", ".sh", ".log",
            ".jsonl", ".out", ".err", ".list", ".sha256"}
EMAIL_EXEMPT = re.compile(r"(eyekb@local|example|noreply|localhost)", re.I)
CODE = {"自家样本ID": "R01", "企微chat_id": "R02", "机器主机名": "R03", "渠道商名-LLM_CHANNEL": "R04",
        "渠道商名-keyfan": "R05", "渠道商名-LLM_CHANNEL": "R06", "渠道商名-intern": "R07",
        "外部裁决商名": "R08", "企微提及": "R09", "密钥形态兜底": "R10", "LM-Studio提及": "R11",
        "profile名": "R12", "第三方联系邮箱": "R13", "端口-内部服务": "R14", "端口-代理": "R15", "会话标识": "R16"}

def scan_tree(dirs):
    inv = {}
    for d in dirs:
        base = REPO / d
        for f in sorted(base.rglob("*")):
            if not f.is_file() or "__pycache__" in str(f) or f.suffix not in TEXT_EXT:
                continue
            try:
                t = f.read_text(encoding="utf-8")
            except Exception:
                continue
            rel = str(f.relative_to(REPO))
            hits = {}
            for name, pat, rep, scope in RULES:
                if scope == "prose" and f.suffix not in PROSE_ONLY:
                    continue
                n = 0
                for m in re.finditer(pat, t):
                    if name == "第三方联系邮箱" and EMAIL_EXEMPT.search(m.group(0)):
                        continue
                    n += 1
                if n:
                    hits[name] = n
            if hits:
                inv[rel] = hits
    return inv

inv = scan_tree(["kb", "mcp_server", "docs/wiki", "docs/plans/kb9_ocs_20260927"])
mine = {k: v for k, v in inv.items() if k in MY_TARGETS}
hist = {k: v for k, v in inv.items() if k not in MY_TARGETS}
with open(CARD / "exec/out/desens_full_inventory_20260928.tsv", "w", encoding="utf-8") as fh:
    fh.write("relpath\tscope\ttotal_hits\trule_counts(名称=代号)\n")
    for k, v in sorted(inv.items()):
        scope = "MINE" if k in MY_TARGETS else "PREEXISTING"
        fh.write(f"{k}\t{scope}\t{sum(v.values())}\t" + ";".join(f"{CODE[n]}:{c}" for n, c in sorted(v.items())) + "\n")
hist_kb = {k: v for k, v in hist.items() if k.startswith("kb/") or k.startswith("mcp_server/")}
hist_docs = {k: v for k, v in hist.items() if k.startswith("docs/")}
print(f"[2a] inventory: mine_files={len(mine)} preexisting_kb_mcp_files={len(hist_kb)} preexisting_docs_files={len(hist_docs)}")

# 限定 apply（dv3 + DESSENS_ONLY 过滤）
dv3 = RAW / "exec6b_desens_t4bb75b26.py"
d = dv2_src.replace('STG = "/home/ubuntu/EYEKB_REPO_STAGING_20260927"', 'STG = "/home/ubuntu/EYEKB_REPO"')
d = d.replace('DIRS = ["docs/wiki", "docs/skills", "docs/plans", "mcp_server"]',
              'DIRS = ["kb", "mcp_server", "docs/wiki", "docs/plans/kb9_ocs_20260927"]')
d = d.replace("REPOSYNC 脱敏器 v2 — 2026-09-27",
              "[KB9REG-EXEC t_4bb75b26 副本 v3] REPOSYNC 脱敏器 v2 — 规则三元组逐字同源；STG/DIRS 参数化 + DESSENS_ONLY 白名单过滤（kb 历史面命中=登记不擅动）— 2026-09-28 (仓外件)")
d = d.replace("def iter_files():", "ONLY = [x for x in os.environ.get('DESENS_ONLY','').split(os.pathsep) if x]\n\n\ndef iter_files():")
d = d.replace("            for fn in files:\n                yield os.path.join(root, fn)",
              "            for fn in files:\n                p = os.path.join(root, fn)\n                if ONLY and not any(p.endswith(x) for x in ONLY):\n                    continue\n                yield p")
dv3.write_text(d, encoding="utf-8")
env = dict(os.environ)
env["DESENS_ONLY"] = os.pathsep.join(sorted(mine))
apply_r = subprocess.run([PY, str(dv3), "--apply"], capture_output=True, text=True, env=env)
(RAW / "apply_raw.txt").write_text(apply_r.stdout + apply_r.stderr, encoding="utf-8")
assert "DESENS DONE" in apply_r.stdout, apply_r.stdout[-400:] + apply_r.stderr[-400:]
changed = {l[3:].strip() for l in run(f"git -C {REPO} -c core.quotepath=false status --porcelain -uall").stdout.splitlines()}
surprise = sorted(c for c in changed if c not in MY_TARGETS)
assert not surprise, f"apply 波及非本卡件: {surprise[:10]}"
print(f"[2b] limited apply: mine files rewritten; git-changed={len(changed)} (全部∈本卡面)")

# 仓内代号版报告
rep = ["# 脱敏双扫描报告(增量) — 2026-09-28 KB9REG-EXEC t_4bb75b26", "",
       "范围：本卡同步面 = kb/markers(2 新件)+mcp_server(2 改件)+docs/wiki(4 改件)+docs/plans/kb9_ocs_20260927(BRIEF/exec/ols 补回证)。",
       "规则三元组=project-github-export 现行清单，与 2026-09-27 REPOSYNC 报告同源（R01–R16 代号沿用）；本报告不复现任何渠道商/裁决商/端点串。",
       "", "## 本卡面命中（已按标签替换）", ""]
for k, v in sorted(mine.items()):
    rep.append(f"- `{k}`: " + "; ".join(f"{CODE[n]}={c}" for n, c in sorted(v.items())))
rep += ["", "## ⚠ 存量发现（登记，不擅动——处置归协调者/PI）", "",
        f"- kb/ 与 mcp_server/ 历史件 **{len(hist_kb)} 文件**存在 R08(REVIEWER_LLM)/R12(AGENT_ROLE) 形态命中，合计 "
        f"{sum(sum(v.values()) for v in hist_kb.values())} 处。根因=2026-09-27 REPOSYNC 的扫描 DIRS 未含 kb/，"
        "kb/mcp 按线上字节 1:1 镜像（当时对账 104/104 MATCH 即此口径）→ 相应字样已随该轮 push 存在于远端。",
        f"- docs/ 历史面另有 {len(hist_docs)} 文件命中（多为判读层原文引用，上轮按『数值证据面不触碰』口径放行）。",
        "- 处置选项（协调者定）：①对 kb/面补 apply 脱敏→对账表改标 DESENS（仓与线上字节分歧，需 PI 认可语义）；②维持字节镜像+接受字样暴露（这些词是否敏感属 PI 判断，R08/R12 是内部协作称谓而非密钥）；③改线上原件措辞=触发基线字节变更，禁。",
        "- 本卡产物（仓内）的 external_review 字段值因替换与线上权威原件不同，对账表逐件标 DESENS；线上原件 sha 见 exec/out/SHA_NEW_AND_MODIFIED.txt。",
        "", "## 文件名扫描", "- 本卡新增面 0 命中（无需改名）。"]
(CARD / "exec/out/desens_scan_report_20260928.md").write_text("\n".join(rep) + "\n", encoding="utf-8")

# ---- ③ 对账表（kb+mcp 全量）----
recon = ["relpath\tonline_path\trepo_sha256\tonline_sha256\tstatus"]
n_match = n_desens = n_bad = 0
for sub in ("kb", "mcp_server"):
    for f in sorted((REPO / sub).rglob("*")):
        if not f.is_file() or "__pycache__" in str(f):
            continue
        rel = str(f.relative_to(REPO))
        onl = ONLINE / rel
        if not onl.is_file():
            recon.append(f"{rel}\tMISSING-ONLINE\t{sha(f)}\t-\tMISSING"); n_bad += 1; continue
        rs, os_ = sha(f), sha(onl)
        if rs == os_:
            stt = "MATCH"; n_match += 1
        elif rel == "mcp_server/softflags.py":
            stt = "PRIOR_DESENS(c4a8f53 注释级脱敏, 协调者已批)"; n_desens += 1
        else:
            stt = "DESENS" if rel in MY_TARGETS else "DRIFT!!"
            n_desens += stt == "DESENS"
            n_bad += stt == "DRIFT!!"
        recon.append(f"{rel}\t{onl}\t{rs}\t{os_}\t{stt}")
for sub in ("kb", "mcp_server"):
    for f in sorted((ONLINE / sub).rglob("*")):
        if not f.is_file() or "__pycache__" in str(f):
            continue
        rel = str(f.relative_to(ONLINE))
        if not (REPO / rel).is_file():
            recon.append(f"{rel}\t{f}\t-\t{sha(f)}\tEXTRA-ONLINE"); n_bad += 1
tbl = f"# kb+mcp 逐文件 sha256 对账 (repo vs 线上权威 /mnt/D/EyeKB) — KB9REG-EXEC t_4bb75b26 {datetime.now():%F %T}\n" + "\n".join(recon) + "\n"
(REPO / "docs/recon/RECON_kb_mcp_20260928.tsv").write_text(tbl, encoding="utf-8")
(CARD / "exec/out/RECON_kb_mcp_20260928.tsv").write_text(tbl, encoding="utf-8")
assert n_bad == 0, f"对账异常（MISSING/EXTRA/DRIFT）: {n_bad}"
print(f"[3] recon: MATCH={n_match} DESENS={n_desens} 异常={n_bad}")

# ---- ④ README ----
rdm = (REPO / "README.md").read_text(encoding="utf-8")
rdm2 = rdm.replace("KB1v2-0.4-actv6", "KB1v2-0.5-k9reg")
lines = rdm2.splitlines(keepends=True)
k9row = ("| （无 env，硬编码 OFF） | `library=k9_ocs` 仅显式查询可达（KB9 案 B 眼表 4 新条，注册默认 OFF） | "
         "任何态不入默认 all | KB9REG-EXEC t_4bb75b26（PI D17 注册批准 2026-09-28；激活需 §10-6 义务 run+PI 另批；"
         "lacrimal_v6 同理维持 A3 登记态） |\n")
ins_at = None
for i, ln in enumerate(lines):
    if ln.startswith("| `EYEKB_ACT_V6`"):
        while i + 1 < len(lines) and lines[i + 1].startswith("|"):
            i += 1
        ins_at = i + 1
        break
if ins_at and "library=k9_ocs" not in rdm2:
    lines.insert(ins_at, k9row)
    rdm2 = "".join(lines)
(REPO / "README.md").write_text(rdm2, encoding="utf-8")
print(f"[4] README version={'KB1v2-0.5-k9reg' in rdm2} k9row={'library=k9_ocs' in rdm2}")

# ---- ⑤ 分层 commit ----
def commit(paths, msg):
    run(f"git -C {REPO} add -- " + " ".join(f'"{p}"' for p in paths))
    r = run(f"git -C {REPO} commit -m \"{msg}\"")
    ok = r.returncode == 0 and "no changes added" not in (r.stdout or "")
    print("   commit:", msg[:56], "->", "OK" if ok else (r.stdout or "")[-150:] + (r.stderr or "")[-150:])
    return ok

ok = all([
    commit(["kb/markers/markers_k9_ocs_increment.json", "kb/markers/_k9_ocs_rules_overlay_v1.json",
            "mcp_server/eyekb_core.py", "mcp_server/server.py"],
           "KB9REG-EXEC 1/4 装条+路由登记(默认OFF): kb/markers k9.0-ocs-registered-v1 词条库+规则旁挂overlay(惰性件); MARKER_LIBS增k9_ocs显式路由不入默认; 版本0.4-actv6->0.5-k9reg; 42-probe默认响应pre==post机读自证(A5式)"),
    commit(["docs/wiki/数据资产.md", "docs/wiki/决策记录.md",
            "docs/wiki/体系盘点_MCP-RAG-Wiki-Skill_20260924.md", "docs/wiki/检索索引.md"],
           "KB9REG-EXEC 2/4 补wiki: 数据资产新增marker库总表+k9_ocs注册行; 决策记录D17落款(C2b 29/33仅附注, C4历史FAIL记录不改); 体系盘点泪腺/眼表新条状态补记; 检索索引k9_ocs查询指针"),
    commit([f"docs/plans/kb9_ocs_20260927/{Path(r).name}" if False else r for r in sorted(m for m in MY_TARGETS if m.startswith("docs/plans"))] or ["docs/plans/kb9_ocs_20260927"],
           "KB9REG-EXEC 3/4 判读层: exec自证件(pre/post基线+postdiff+双态GOLDEN41+KB2C+脱敏台账)+Limbus CL:0000057 OLS补回证(缺回证的补)"),
    commit(["docs/recon/RECON_kb_mcp_20260928.tsv", "README.md"],
           "KB9REG-EXEC 4/4 对账+README: kb+mcp逐文件sha对账新表(DESENS例外=本卡两件kb json, 存量kb面命中登记不擅动); README版本面+k9_ocs路由行"),
])
assert ok, "commit 分层有失败，停"
# exec 面在 commit3 后又新增（对账表/报告），delta 重同步 + 限定 apply + 补录
inv2 = scan_tree(["docs/plans/kb9_ocs_20260927"])
mine2 = {k: v for k, v in inv2.items() if k in MY_TARGETS or "/exec/" in k}
delta = []
for sub in ("exec/scripts", "exec/out", "exec/pre_images"):
    for f in sorted((CARD / sub).rglob("*")) if (CARD / sub).is_dir() else []:
        if f.is_file() and "__pycache__" not in str(f) and "desens_raw" not in str(f):
            rel = f"docs/plans/kb9_ocs_20260927/{f.relative_to(CARD)}"
            dst = REPO / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or sha(dst) != sha(f):
                dst.write_bytes(f.read_bytes()); delta.append(rel)
mine2 = {k for k in (set(mine2) | set(delta)) if k in MY_TARGETS or "/exec/" in k}
env["DESENS_ONLY"] = os.pathsep.join(sorted(mine2))
subprocess.run([PY, str(dv3), "--apply"], capture_output=True, text=True, env=env)
print(f"[5] exec delta resync: {len(delta)} 件 + 限定 apply")
# 终检门（限本卡面）：git 已改/将改文件不得残留规则串
leak_patterns = [p for (_n, p, _r, _s) in RULES]
bad = []
for m in sorted(MY_TARGETS):
    p = REPO / m
    if p.suffix in TEXT_EXT:
        try:
            t = p.read_text(encoding="utf-8")
        except Exception:
            continue
        for lp in leak_patterns:
            mo = re.search(lp, t)
            if mo and not (lp.startswith("[A-Za-z0-9._%") and EMAIL_EXEMPT.search(mo.group(0))):
                bad.append((m, mo.group(0)[:30]))
                break
assert not bad, f"本卡面脱敏终检泄漏: {bad[:8]}"
print("[6] 终检门: 本卡面 0 泄漏")
rest = [l[3:].strip() for l in run(f"git -C {REPO} -c core.quotepath=false status --porcelain -uall").stdout.splitlines()]
if rest:
    run(f"git -C {REPO} add -- " + " ".join(f'"{p}"' for p in rest))
    r = run(f"git -C {REPO} commit -m \"KB9REG-EXEC 收尾: exec面增补件(对账副本/双态log/终检) + 限定apply刷新\"")
    print("   收尾 commit:", "OK" if r.returncode == 0 else r.stdout[-200:])
head = run(f"git -C {REPO} rev-parse --short HEAD").stdout.strip()
ahead = run(f"git -C {REPO} rev-list --count origin/main..HEAD").stdout.strip()
print(f"[7] HEAD={head} ahead(origin/main)={ahead} —— 未 push（测试门归协调者）")
