#!/usr/bin/env bash
# tests/run_gates.sh — 一键门链入口：G3 -> G4 -> G5 -> G6，末尾汇总（新增于 G5G6 卡，2026-10-12）
#
# 用法：bash $0        （clone 即可跑；本脚本只用 python3 + 仓内文件，零网络、零 GPU）
#   环境变量：
#     EYEKB_CORPUS   语料目录（G3 需要）。默认 $REPO/literature_db/v2.4.2_2026-09_slim
#     EYEKB_G3_PY    G3 要用的解释器（可选）：给定时其所在目录前置到 PATH。G3 的依赖按 G1 锁装在某个环境里时用
#                    （先例：本机 /home/ubuntu/.conda/envs/pipeline_env/bin/python）；不给则用 PATH 上的 python3。
#     EYEKB_GATE_OUT 本脚本的读数落盘目录（默认 $REPO/.gate_out，仅放运行时产物，不进 git 树）
#   说明：G4 的解释器由门自己钉死（pipeline_env / EYEKB_G4_PY），本脚本不干预；
#         本脚本本身不判 PASS/FAIL——判定在各门内部，本脚本只如实汇总各门 rc。
set -u

# 路径解析只用 bash 内建（不用 dirname/readlink）：最小环境（PATH 里没有 /usr/bin）也能定位仓根。
_src="${BASH_SOURCE[0]}"
_dir="${_src%/*}"
[ "$_dir" = "$_src" ] && _dir="."
HERE="$(cd "$_dir" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"

# 最小环境兜底：标准目录始终补在 PATH 末尾（不改变用户既有优先级，只保证 coreutils/python3 可达）
export PATH="${PATH:-}:/usr/local/bin:/usr/bin:/bin"

# 可选：G3 用的解释器所在目录前置到 PATH（G1 锁装的依赖可能在某个 conda/venv 里；G4 自己钉解释器，不受影响）
if [ -n "${EYEKB_G3_PY:-}" ]; then
  _g3dir="${EYEKB_G3_PY%/*}"
  [ "$_g3dir" = "$EYEKB_G3_PY" ] && _g3dir="."
  export PATH="$_g3dir:$PATH"
  printf '[gates] G3 interpreter dir prepended: %s\n' "$_g3dir"
fi

cd "$REPO" || exit 2

CORPUS="${EYEKB_CORPUS:-$REPO/literature_db/v2.4.2_2026-09_slim}"
OUT="${EYEKB_GATE_OUT:-$REPO/.gate_out}"
mkdir -p "$OUT"

NAMES=(); RCS=()

run_gate() {                       # run_gate <name> <cmd...>
  local name="$1"; shift
  printf '\n=================== %s ===================\n' "$name"
  "$@"
  local rc=$?
  NAMES+=("$name"); RCS+=("$rc")
  printf -- '------------------- %s rc=%s -------------------\n' "$name" "$rc"
  return 0
}

printf '[gates] repo=%s\n' "$REPO"
printf '[gates] corpus=%s\n' "$CORPUS"
printf '[gates] out=%s\n' "$OUT"

run_gate "G3 verify_repro (41-query retrieval anchor)" \
  python3 tests/verify_repro.py --db-dir "$CORPUS"

run_gate "G4 verify_pipeline (three byte anchors)" \
  python3 tests/verify_pipeline.py

run_gate "G5 gate_registry (registry surface enforced)" \
  python3 tests/gate_registry.py --json "$OUT/G5_RESULTS.json"

run_gate "G6 gate_change_control (eight machine rules)" \
  python3 tests/gate_change_control.py --json "$OUT/G6_RESULTS.json"

printf '\n=================== summary ===================\n'
bad=0
for i in "${!NAMES[@]}"; do
  printf '  %-52s rc=%s\n' "${NAMES[$i]}" "${RCS[$i]}"
  [ "${RCS[$i]}" = "0" ] || bad=$((bad + 1))
done
printf '  ------------------------------------------------------------\n'
printf '  gates=%s failed=%s  (%s)\n' "${#NAMES[@]}" "$bad" \
  "$([ "$bad" = 0 ] && echo 'CHAIN PASS' || echo 'CHAIN FAIL')"
exit $([ "$bad" = 0 ] && echo 0 || echo 1)