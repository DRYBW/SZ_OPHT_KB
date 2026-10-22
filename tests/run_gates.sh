#!/usr/bin/env bash
# tests/run_gates.sh - one-click gate chain: G3 -> G4 -> G5 -> G6, with a summary at the end (added by the G5G6 card, 2026-10-12)
#
# Usage: bash $0        (runnable straight after cloning; uses only python3 + in-repo files, no network, no GPU)
#   Environment variables:
#     EYEKB_CORPUS   corpus directory (needed by G3). Defaults to $REPO/literature_db/v2.4.2_2026-09_slim
#     EYEKB_G3_PY    interpreter for G3 (optional): when set, its directory is prepended to PATH. Use it when
#                    the G3 dependencies were locked (G1) into a particular environment
#                    (previous case: /home/ubuntu/.conda/envs/pipeline_env/bin/python); otherwise the python3 on PATH.
#     EYEKB_GATE_OUT directory for this script's readouts (default $REPO/.gate_out, runtime-only, not in the git tree)
#   Note: G4 pins its own interpreter (pipeline_env / EYEKB_G4_PY); this script does not interfere;
#         this script itself does not judge PASS/FAIL - each gate judges internally; it only reports each rc.
set -u

# Path resolution uses bash builtins only (no dirname/readlink): the repo root is found even in a minimal
# environment whose PATH lacks /usr/bin.
_src="${BASH_SOURCE[0]}"
_dir="${_src%/*}"
[ "$_dir" = "$_src" ] && _dir="."
HERE="$(cd "$_dir" && pwd)"
REPO="$(cd "$HERE/.." && pwd)"

# Minimal-environment fallback: standard directories are always appended to PATH (existing precedence is
# preserved; coreutils/python3 merely become reachable)
export PATH="${PATH:-}:/usr/local/bin:/usr/bin:/bin"

# Optional: prepend the G3 interpreter directory to PATH (G1-locked dependencies may live in a conda/venv;
# G4 pins its own interpreter and is unaffected)
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

# G7/G8 were added by the card that wired the read-only Cell Ontology explanation layer. G7 needs an
# interpreter that can import the service (the MCP SDK and its dependencies), so it follows the G3
# convention; G8 needs nothing but the standard library.
G7_PY="${EYEKB_G7_PY:-${EYEKB_G3_PY:-python3}}"
run_gate "G7 gate_ontology_layer (read-only ontology explanation layer)" \
  python3 tests/gate_ontology_layer.py --service-python "$G7_PY" --json "$OUT/G7_RESULTS.json"

run_gate "G8 gate_ontlayer_portability (portability and fail-closed behaviour)" \
  python3 tests/gate_ontlayer_portability.py --json "$OUT/G8_RESULTS.json"

# G9 was added after the same defect was observed twice in one day: a before/after judgement
# script that reads its pre-image with a *relative* git reference (`git show HEAD:path`) silently
# compares the new revision against itself once the change is committed. The gate forbids
# relative references as pre/post-image sources, and self-tests on a synthetic tree so that a
# scanner which flags nothing cannot pass.
run_gate "G9 gate_preimage_ref_immutable (pre/post-image refs must be immutable)" \
  python3 tests/gate_preimage_ref_immutable.py --json "$OUT/G9_RESULTS.json"

printf '\n=================== summary ===================\n'
bad=0
for i in "${!NAMES[@]}"; do
  case "${RCS[$i]}" in
    0) label='pass' ;;
    3) label='INCONCLUSIVE (precondition missing - not a result)'; bad=$((bad + 1)) ;;
    *) label='fail'; bad=$((bad + 1)) ;;
  esac
  printf '  %-52s rc=%s %s\n' "${NAMES[$i]}" "${RCS[$i]}" "$label"
done
printf '  ------------------------------------------------------------\n'
printf '  gates=%s failed=%s  (%s)\n' "${#NAMES[@]}" "$bad" \
  "$([ "$bad" = 0 ] && echo 'CHAIN PASS' || echo 'CHAIN FAIL')"
exit $([ "$bad" = 0 ] && echo 0 || echo 1)