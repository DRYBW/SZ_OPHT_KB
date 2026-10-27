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

# G10 was added after a before/after measurement of the recorded set silently returned `changed = 0`
# for a change that was in fact active: the frozen harness clears a hard-coded tuple of switch
# names, and a switch added to the router after that tuple was written was never cleared, so the
# before arm's setting survived into the after arm and the comparison ran the tree against itself.
# The gate enforces the switch registry staying in sync with the source, and -- as a property of the
# arm pair rather than of any single spec -- that no arm may set a switch the harness does not clear
# unless every arm of that comparison sets it.
run_gate "G10 gate_switch_coverage (switch registry in sync; before/after arms separated)" \
  python3 tests/gate_switch_coverage.py --json "$OUT/G10_RESULTS.json"

# G11 was added after the shipped service description kept quoting its launch-era corpus size
# (v2.0's 2,713 papers / 174,616 passages) while the bundled corpus had been re-cut
# (v2.4.2_2026-09_slim: 3,869 papers / 242,928 passages — the built-in switch of 2026-10-01).
# The description now renders from mcp_server/corpus_stats.py (reads the bundled
# build_stats.json; frozen fallback for a fresh clone). This gate re-derives every number
# from disk: rendered vs bundled build_stats.json vs the pointer's registered v2.4.2 identity,
# plus a no-hardcode scan of the description clause and a planted-shape self-test. A digit
# sabotaged in the description or the fallback must flip rc to 2; a tree without the G2 corpus
# asset is INCONCLUSIVE (rc=3), with the fallback still pinned to the pointer
# (contract: docs/VERIFY_CONTRACT.md §5.6; evidence: docs/plans/mcpdesc_20261025/).
run_gate "G11 gate_mcpdesc_corpus (description corpus numbers vs the bundled corpus)" \
  python3 tests/gate_mcpdesc_corpus.py --json "$OUT/G11_RESULTS.json"

# G12 was added after the link registry's citation records turned out to carry no usable title key:
# the builder wrote `(hit title)[:120]` on the retrieval route and `""` on the full-text gene-index
# route, so 2,429 of the shipped registry's 3,993 citation records had no title at all and 509 had a
# 120-character prefix of one. Every cited paper is in the corpus and the corpus holds the complete
# title, so nothing on disk could catch the drift and a title-keyed audit read it as "the two
# libraries disagree" (measured: A strict 247/825 = 29.94%, B prefix-40 369/825 = 44.73%). The
# builder now joins title / doi / pmcid from the corpus on `paper_id == pmid`, and the delivered
# registry carries title_full / doi / pmcid on every citation record. This gate re-derives that from
# disk (source regression, metadata presence, metadata vs corpus, coverage, byte anchor against the
# delivery's immutable pre-image, builder-vs-gate reader parity) plus a planted-shape self-test.
# A corpus-absent tree is INCONCLUSIVE (rc=3), the G3/G11 precedent; evidence and reverse controls:
# docs/plans/cittitle_20261025/ (out/G12_CONTROLS.json).
run_gate "G12 gate_cittitle_meta (citation title/doi/pmcid vs the corpus)" \
  python3 tests/gate_cittitle_meta.py --json "$OUT/G12_RESULTS.json"

# G13 was added after the frozen RUN4W golden-41 gate reported 0/41 on EVERY case while nothing was
# actually broken: its direct arm had .../literature_db/v2.0_2026-09 hard-coded while its MCP arm
# resolved the default library through the pointer, so the two arms read two different libraries and
# the gate could only ever report a difference. A stale pin fails in exactly the shape of a real
# regression, and it cost a long detour to separate the two (measured 2026-10-27; recorded in
# docs/plans/lit_gapfill_20261026/SAME_STUDY_DEDUP_RECORD_20261027.md). This gate reads the library
# versions each gate/verification script references, compares them with the pointer's declared
# default, and FAILS only when a member of THIS chain is pinned to a non-default library; standalone
# historical audit files are reported as WARN, because they legitimately pin the library of their own
# date. Static, standard library only, no network, no GPU, and it carries five controls that build
# each situation from scratch -- a gate that cannot fail is not a gate.
run_gate "G13 gate_library_pin_consistency (no chain member pinned to a stale library)" \
  python3 tests/gate_library_pin_consistency.py --controls --json "$OUT/G13_RESULTS.json"

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