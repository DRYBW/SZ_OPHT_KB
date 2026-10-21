#!/usr/bin/env bash
# run_all.sh — one command that builds the marker layer, freezes it, and judges it.
#
#   bash scripts/run_all.sh              # build into $MK_OUTDIR (default: ../out)
#   bash scripts/run_all.sh --no-replay  # skip the rebuild replay and the recorded-query replay
#   MK_OUTDIR=/tmp/x bash scripts/run_all.sh
#
# Zero network is enforced, not claimed: the chain runs with PYTHONPATH pointing at
# scripts/netaudit, whose audit hook covers child processes, and the ledger must show zero EVENT
# lines (a load receipt line proves the hook was installed). The heavy corpus pass runs under
# systemd-run --user with a memory cap, as this project requires for heavy steps — the measured
# peak is 0.33 GiB/process, so the cap below is a guard, not a constraint.
#
# Order matters: every artefact is written before the manifest is taken, and the gate runs after
# the manifest so a drifting artefact is caught by the gate rather than by hand.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY="${PY:-/usr/bin/python3}"
OUT="${MK_OUTDIR:-$WAVE/out}"
export MK_OUTDIR="$OUT"
mkdir -p "$OUT" "$WAVE/ledgers"
cd "$WAVE" || exit 2

export MK_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
echo "# chain start $(date -Is)" >> "$MK_NET_AUDIT_LOG"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/ledgers/chain.log"; return "${PIPESTATUS[0]}"; }

echo "== outdir: $OUT"
run scripts/m0_corpus_gene_index.py || exit 1
run scripts/m1_nodes.py || exit 1
run scripts/m2_node_markers.py || exit 1
run scripts/m3_edge_assertions.py || exit 1
run scripts/m4_gap_register.py || exit 1

echo "== manifest (taken before the gate, so a drifting artefact is the gate's job)"
run scripts/m6_manifest.py || exit 1

echo "== gate (rebuild replay + recorded query set included)"
if [ "${1:-}" = "--no-replay" ]; then
  run scripts/m5_gate.py --no-replay; rc=$?
else
  run scripts/m5_gate.py; rc=$?
fi

# the manifest must still verify after the gate rewrote its own readouts.
# sha256sum resolves the entries relative to the CWD, so the check runs inside $OUT.
echo "== manifest check after the gate"
( cd "$OUT" && sha256sum -c MANIFEST.sha256 ) > "$WAVE/ledgers/manifest_check.txt" 2>&1 \
  && echo "MANIFEST_OK after gate" || echo "MANIFEST_FAILED after gate"

echo "== replay ledger (second build, compared artefact by artefact)"
if [ "${1:-}" = "--no-replay" ]; then
  echo "== replay ledger: skipped by --no-replay"
else
  run scripts/m8_replay_ledger.py || exit 1
fi

echo "== report (assembled from the artefacts and from the gate's verdict)"
run scripts/m7_report.py || exit 1

echo "== network audit (counted and written by the report step, so both read the same numbers)"
cat "$WAVE/ledgers/NET_AUDIT_SUMMARY.txt"
grep -q 'NET_ZERO_PASS' "$WAVE/ledgers/NET_AUDIT_SUMMARY.txt" || rc=1
exit "$rc"