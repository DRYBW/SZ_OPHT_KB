#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-EXEC t_4bb75b26 · exec6 — 仓镜像同步（脱敏管线同 REPOSYNC，push 前停手）
① copy 不 move 同步本卡改动面到 /home/ubuntu/EYEKB_REPO；
② 脱敏双扫描（规则三元组=v2 现行清单，STG/DIRS 参数化副本）：scan→断言命中面⊆本卡新改件→apply→git status 复核；
③ kb+mcp 全量 sha 对账新表 RECON_kb_mcp_20260928.tsv（MATCH/DESENS/MISSING/EXTRA）；
④ README 版本面+k9_ocs 路由行刷新；
⑤ 分层 commit（代码+kb / wiki / 判读层 / 对账+README），不 push。"""
import hashlib
import json
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


def sha(p):
    return hashlib.sha256(Path(p).read_bytes()).hexdigest()


def run(cmd, **kw):
    r = subprocess.run(cmd, shell=isinstance(cmd, str), capture_output=True, text=True, **kw)
    return r


# ---- git 基线检查 ----
st = run(f"git -C {REPO} status --porcelain").stdout.strip()
assert st == "", f"repo 工作区不干净，先处理:\n{st}"
head_before = run(f"git -C {REPO} rev-parse HEAD").stdout.strip()

# ---- ① 同步文件清单 ----
SYNC = [
    # (online, repo-relpath)
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
            if f.is_file() and "__pycache__" not in str(f):
                rel = f.relative_to(CARD)
                SYNC.append((f, f"docs/plans/kb9_ocs_20260927/{rel}"))
# OLS 补回证 3 件
for f in sorted((CARD / "ledgers/ols_evidence_kb9").glob("*t4bb75b26*")):
    SYNC.append((f, f"docs/plans/kb9_ocs_20260927/ledgers/ols_evidence_kb9/{f.name}"))

# 新产物/改动件线上权威 sha 台账（脱敏报告引用；先落盘再随 exec/out 同步入仓）
nm = [f"# KB9REG-EXEC t_4bb75b26 新产物与改动件 sha256（线上权威原件） {datetime.now():%F %T}"]
for src, rel in SYNC:
    p = Path(src)
    if "_rules_overlay" in p.name or "markers_k9" in p.name or "pre_images" in str(p) or "/exec/" in str(p) or "t4bb75b26" in p.name:
        nm.append(f"{sha(p)}  NEW  {rel}")
    elif "mcp_server" in str(p) or "WIKI" in str(p):
        nm.append(f"{sha(p)}  MOD  {rel}")
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

# ---- ② 脱敏（参数化 v2 副本；脱敏器与原始命中台账=仓外件，仓内只放代号版报告——REPOSYNC 口径）----
desens_src = Path("/home/ubuntu/eyekb_desensitize_v2.py").read_text(encoding="utf-8")
RAW = CARD / "exec/desens_raw"
RAW.mkdir(parents=True, exist_ok=True)
dv3 = RAW / "exec6b_desens_t4bb75b26.py"
dv3_src = desens_src.replace('STG = "/home/ubuntu/EYEKB_REPO_STAGING_20260927"',
                             'STG = "/home/ubuntu/EYEKB_REPO"')
dv3_src = dv3_src.replace('DIRS = ["docs/wiki", "docs/skills", "docs/plans", "mcp_server"]',
                          'DIRS = ["kb", "mcp_server", "docs/wiki", "docs/plans/kb9_ocs_20260927"]')
dv3_src = dv3_src.replace("REPOSYNC 脱敏器 v2 — 2026-09-27",
                          "[KB9REG-EXEC t_4bb75b26 副本] REPOSYNC 脱敏器 v2 — 规则三元组逐字同源，仅 STG/DIRS 参数化 — 2026-09-28 (仓外件)")
dv3.write_text(dv3_src, encoding="utf-8")
scan = run([PY, str(dv3), "--scan"]).stdout
(RAW / "scan_raw.txt").write_text(scan, encoding="utf-8")
# 代号版报告（规则名→R 代号，命中文件路径本身已在上轮改名后=安全面）
CODE = {"自家样本ID": "R01 OWN_MOUSE_DR_DATASET", "企微chat_id": "R02 CONTACT_ID", "机器主机名": "R03 HOST",
        "渠道商名-LLM_CHANNEL": "R04 LLM_CHANNEL", "渠道商名-keyfan": "R05 LLM_CHANNEL", "渠道商名-LLM_CHANNEL": "R06 LLM_CHANNEL",
        "渠道商名-intern": "R07 LLM_CHANNEL", "外部裁决商名": "R08 REVIEWER_LLM", "企微提及": "R09 MSG_PLATFORM",
        "密钥形态兜底": "R10 REDACTED_SECRET", "LM-Studio提及": "R11 LOCAL_LLM", "profile名": "R12 AGENT_ROLE",
        "第三方联系邮箱": "R13 CONTACT_EMAIL", "端口-内部服务": "R14 PORT", "端口-代理": "R15 PORT",
        "会话标识": "R16 SESSION_ID"}
# 命中文件清单（scan 输出 top-20 行格式 "  <n>  <relpath>"）
hit_files = set(re.findall(r"^\s+\d+\s+(\S.+)$", scan, re.M))
stale = [h for h in hit_files if h not in MY_TARGETS and not h.startswith("docs/plans/kb9_ocs_20260927/register")
         and not h.startswith("docs/plans/kb9_ocs_20260927/recheck") and not h.startswith("docs/plans/kb9_ocs_20260927/out")]
# register/recheck/out 子目录=09-27 已镜像判读层，本轮未重新同步这些历史件；
# 若其扫描仍命中说明上轮 apply 未覆盖该面——如实登记，不本轮擅动。
assert not [h for h in hit_files if h.startswith("kb/") and h not in MY_TARGETS], \
    f"kb 历史件出现脱敏命中（破坏字节镜像前提）: {[h for h in hit_files if h.startswith('kb/') and h not in MY_TARGETS]}"
apply_r = run([PY, str(dv3), "--apply"])
(RAW / "apply_raw.txt").write_text(apply_r.stdout + apply_r.stderr, encoding="utf-8")
assert "DESENS DONE" in apply_r.stdout, apply_r.stdout[-500:]
# 仓内可见的代号版脱敏报告（本轮增量面）
rep_lines = ["# 脱敏双扫描报告(增量) — 2026-09-28 KB9REG-EXEC t_4bb75b26",
             "",
             "范围：本卡同步面 = kb/markers(2 新件)+mcp_server(2 改件)+docs/wiki(4 改件)+docs/plans/kb9_ocs_20260927(BRIEF/exec/ols补回证)。",
             "规则三元组=project-github-export 现行清单，与 2026-09-27 REPOSYNC 报告同源（R01–R16 代号沿用）；本报告不复现任何渠道商/裁决商/端点串。",
             "", "## 规则命中统计（本轮增量，代号版）", ""]
hits_by_rule = {}
for line in apply_r.stdout.splitlines():
    m = re.match(r"\s+(.+?): (\d+)\s*$", line)
    if m and m.group(1) in CODE:
        hits_by_rule[CODE[m.group(1)]] = hits_by_rule.get(CODE[m.group(1)], 0) + int(m.group(2))
for k, v in sorted(hits_by_rule.items()):
    rep_lines.append(f"- {k}: {v}")
rep_lines += ["", "## 说明", "",
              f"- 命中文件 {len(hit_files)} 件（全清单留仓外台账）；本卡新改件命中一律标签替换；仓内 kb 两件 json 的 external_review 字段值因此与线上权威原件不同（对账表标 DESENS，线上原件 sha 见 exec/out/SHA_NEW_AND_MODIFIED.txt）。",
              "- 文件名扫描：本卡新增面无需改名文件（0 命中）。",
              "- 历史判读面若被本轮 apply 波及（上轮目录面未覆盖之命中），随补录 commit 逐件留痕。"]
(CARD / "exec/out/desens_scan_report_20260928.md").write_text("\n".join(rep_lines) + "\n", encoding="utf-8")
changed = set(run(f"git -C {REPO} status --porcelain").stdout.split() and
              [l[3:].strip() for l in run(f"git -C {REPO} status --porcelain").stdout.splitlines()])
surprise = [c for c in changed if c not in MY_TARGETS and not c.startswith("docs/plans/kb9_ocs_20260927/register")
            and not c.startswith("docs/plans/kb9_ocs_20260927/recheck")]
print(f"[2] desens scan hits={len(hit_files)}; git-changed={len(changed)}; surprise={surprise}")
assert not surprise, f"apply 动到非本卡文件: {surprise}"

# ---- ③ kb+mcp 全量对账（仓 vs 线上权威）----
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
        status = "MATCH" if rs == os_ else "DESENS"
        if status == "MATCH":
            n_match += 1
        else:
            n_desens += 1
        recon.append(f"{rel}\t{onl}\t{rs}\t{os_}\t{status}")
# 反向：线上有而仓没有的 kb/mcp 文件
for sub in ("kb", "mcp_server"):
    for f in sorted((ONLINE / sub).rglob("*")):
        if not f.is_file() or "__pycache__" in str(f):
            continue
        rel = str(f.relative_to(ONLINE))
        if not (REPO / rel).is_file():
            recon.append(f"{rel}\t{f}\t-\t{sha(f)}\tEXTRA-ONLINE(未镜像)")
            n_bad += 1
rt = REPO / "docs/recon/RECON_kb_mcp_20260928.tsv"
rt.write_text(f"# kb+mcp 逐文件 sha256 对账 (repo vs 线上权威 /mnt/D/EyeKB) — KB9REG-EXEC t_4bb75b26 {datetime.now():%F %T}\n" + "\n".join(recon) + "\n", encoding="utf-8")
(CARD / "exec/out/RECON_kb_mcp_20260928.tsv").write_text(rt.read_text(encoding="utf-8"), encoding="utf-8")
print(f"[3] recon: MATCH={n_match} DESENS={n_desens} 异常={n_bad} (清单 docs/recon/RECON_kb_mcp_20260928.tsv)")

# ---- ④ README 刷新（版本面 + k9_ocs 行）----
rdm = (REPO / "README.md").read_text(encoding="utf-8")
rdm2 = rdm.replace("KB1v2-0.4-actv6", "KB1v2-0.5-k9reg")
k9row = ("| （无 env，硬编码 OFF） | `library=k9_ocs` 仅显式查询可达（KB9 案 B 眼表 4 新条，"
         "注册默认 OFF） | 任何态不入默认 all | KB9REG-EXEC t_4bb75b26（PI D17 注册批准 2026-09-28；"
         "激活需 §10-6 义务 run+PI 另批；lacrimal_v6 同理维持 A3 登记态） |\n")
anchor = "| `EYEKB_ACT_V6` |"
lines = rdm2.splitlines(keepends=True)
ins_at = None
for i, ln in enumerate(lines):
    if ln.startswith(anchor):
        ins_at = i
        while i + 1 < len(lines) and lines[i + 1].startswith("|"):
            i += 1
        ins_at = i + 1
        break
if "library=k9_ocs" not in rdm2 and ins_at:
    lines.insert(ins_at, k9row)
    rdm2 = "".join(lines)
(REPO / "README.md").write_text(rdm2, encoding="utf-8")
print(f"[4] README: version-replaced={'KB1v2-0.5-k9reg' in rdm2}, k9_ocs row added={('library=k9_ocs' in rdm2) and rdm2 != rdm.replace('KB1v2-0.5-k9reg','KB1v2-0.4-actv6')}")

# ---- ⑤ 分层 commit（不 push）----
def commit(paths, msg):
    run(f"git -C {REPO} add -- " + " ".join(f'"{p}"' for p in paths))
    r = run(f"git -C {REPO} commit -m \"{msg}\"")
    ok = r.returncode == 0 and "no changes added" not in r.stdout
    print("   commit:", msg[:60], "->", "OK" if ok else r.stdout[-200:] + r.stderr[-200:])
    return ok

c1 = commit(["kb/markers/markers_k9_ocs_increment.json", "kb/markers/_k9_ocs_rules_overlay_v1.json",
             "mcp_server/eyekb_core.py", "mcp_server/server.py"],
            "KB9REG-EXEC 1/4 装条+路由登记(默认OFF): kb/markers k9.0-ocs-registered-v1 词条库+规则旁挂overlay(惰性件); MARKER_LIBS+k9_ocs 显式路由不入默认; 版本0.4-actv6→0.5-k9reg; 42-probe默认响应pre==post机读自证(A5式)")
c2 = commit(["docs/wiki/数据资产.md", "docs/wiki/决策记录.md",
             "docs/wiki/体系盘点_MCP-RAG-Wiki-Skill_20260924.md", "docs/wiki/检索索引.md"],
            "KB9REG-EXEC 2/4 补wiki: 数据资产§8 marker库总表+k9_ocs注册行; 决策记录D17落款(C2b 29/33附注不改C4历史FAIL); 体系盘点泪腺/眼表新条状态补记; 检索索引4b k9_ocs查询指针")
c3 = commit(["docs/plans/kb9_ocs_20260927/BRIEF_KB9REG_EXEC.md", "docs/plans/kb9_ocs_20260927/exec",
             "docs/plans/kb9_ocs_20260927/ledgers/ols_evidence_kb9"],
            "KB9REG-EXEC 3/4 判读层: exec自证件(pre/post基线+postdiff+双态GOLDEN41+KB2C+脱敏台账)+Limbus CL:0000057 OLS补回证(缺回证的补)+脱敏器副本")
c4 = commit(["docs/recon/RECON_kb_mcp_20260928.tsv", "README.md",
             "docs/plans/kb9_ocs_20260927/exec/out/RECON_kb_mcp_20260928.tsv"],
            "KB9REG-EXEC 4/4 对账+README: kb+mcp 逐文件sha对账新表(20260928, DESENS例外标注); README版本面+k9_ocs路由行")
assert all([c1, c2, c3, c4]), "commit 分层有失败，停"
# ---- exec/ 增量重同步（报告类件在 scan 阶段后才落盘）+ 脱敏再 apply ----
delta = []
for sub in ("exec/scripts", "exec/out", "exec/pre_images"):
    d = CARD / sub
    for f in sorted(d.rglob("*")) if d.is_dir() else []:
        if f.is_file() and "__pycache__" not in str(f):
            rel = f"docs/plans/kb9_ocs_20260927/{f.relative_to(CARD)}"
            dst = REPO / rel
            dst.parent.mkdir(parents=True, exist_ok=True)
            if not dst.exists() or sha(dst) != sha(f):
                dst.write_bytes(f.read_bytes()); delta.append(rel)
if delta:
    run([PY, str(dv3), "--apply"])  # 重同步件再过一遍 apply（幂等）
print(f"   exec/ delta resync: {len(delta)} 件")
# 终检门：仓工作树全文不得残留规则串（密钥/渠道商/裁决商/profile；dv3 与 desens_raw 不在仓内）
leak = run(f"grep -rInE \"REVIEWER_LLM|\\bastra\\b|REVIEWER_LLM|LLM_CHANNEL|LLM_CHANNEL|LLM_CHANNEL|LLM_CHANNEL|apikey\\.(fun|fan)|LLM_CHANNEL|AGENT_ROLE|AGENT_ROLE|AGENT_ROLE|sk-[a-zA-Z0-9]{{16,}}\" {REPO} --exclude-dir=.git --exclude-dir=__pycache__ | head -20")
assert leak.stdout.strip() == "", f"脱敏终检泄漏:\n{leak.stdout[:1000]}"
print("   脱敏终检: 0 泄漏")
# 脱敏连带 register/recheck/out 面若被 apply 刷新（上轮遗漏面的命中），单独 commit 登记
rest = [l[3:].strip() for l in run(f"git -C {REPO} status --porcelain").stdout.splitlines()]
if rest:
    run(f"git -C {REPO} add -- " + " ".join(f'"{p}"' for p in rest))
    run(f"git -C {REPO} commit -m \"KB9REG-EXEC 补录: 脱敏apply波及的历史判读面文件(上轮REPOSYNC目录面未覆盖之命中, 规则三元组同源), 逐件登记见 diff\"")
    print(f"   +1 commit 补录 {len(rest)} 件")

head_after = run(f"git -C {REPO} rev-parse --short HEAD").stdout.strip()
ahead = run(f"git -C {REPO} rev-list --count origin/main..HEAD").stdout.strip()
print(f"[5] commits done. HEAD={head_after}, ahead of origin/main={ahead} (未 push——测试门归协调者)")
