#!/usr/bin/env bash
# run_all.sh — one command that builds this wave's evidence, freezes it, and judges it.
#
#   bash scripts/run_all.sh                  # the whole chain, ending with the gate
#   bash scripts/run_all.sh --no-replay      # skip the recorded-query replay inside the gate
#
# Zero network is enforced rather than claimed: the chain runs with PYTHONPATH pointing at
# scripts/netaudit, whose audit hook covers child processes, and the ledger must show zero EVENT
# lines. A load receipt line proves the hook was installed, so "no events" can never be read as
# "the hook never ran".
#
# Order matters: every artefact is written before the manifest is taken, and the gate runs after
# the manifest, so a drifting artefact is caught by the gate rather than by hand. The clone check
# runs last: it is the one step that needs the gate to exist, and the gate's own clone-record
# check reads what it writes.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY="${PY:-/usr/bin/python3}"
cd "$WAVE" || exit 2
mkdir -p out ledgers logs

export MK_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
echo "# chain start $(date -Is)" >> "$MK_NET_AUDIT_LOG"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/ledgers/chain.log"; return "${PIPESTATUS[0]}"; }

echo "== item 1a: fix the upstream builder at the root, regenerate the table, re-run the upstream gate"
run scripts/w5_01_fix_upstream.py || exit 1

echo "== item 1b: grade the same rows with the marker layer's four-condition rule and reconcile"
run scripts/w5_02_strict_regrade.py || exit 1

echo "== item 3: re-point the node/edge builders at the scaffold and re-run the layer"
run scripts/w5_03_repoint.py || exit 1

echo "== item 2: the two kb/markers copies, byte ledger and authority"
run scripts/w5_04_item2_kb.py || exit 1

echo "== item 4: the evaluation-basis finding"
run scripts/w5_05_evalbasis.py || exit 1

echo "== manifest (taken before the gate, so a drifting artefact is the gate's job)"
run scripts/w5_08_manifest.py || exit 1

echo "== gate (author tree)"
if [ "${1:-}" = "--no-replay" ]; then
  run scripts/w5_06_gate.py --no-replay; rc=$?
else
  run scripts/w5_06_gate.py; rc=$?
fi

echo "== clone check (clean clone, gate re-run there, mirror fidelity measured)"
if [ "${W5_SKIP_CLONE:-0}" = "1" ]; then
  echo "   skipped (W5_SKIP_CLONE=1): run scripts/w5_07_clone_check.sh after committing the mirror"
else
  bash scripts/w5_07_clone_check.sh "${W5_CLONE_MODE:+--mode=$W5_CLONE_MODE}" \
    2>&1 | tee -a "$WAVE/ledgers/chain.log"
fi

echo "== gate again, now that the clone-check record exists"
if [ "${1:-}" = "--no-replay" ]; then
  run scripts/w5_06_gate.py --no-replay; rc=$?
else
  run scripts/w5_06_gate.py; rc=$?
fi

echo "== manifest check after the gate (the gate only writes files the manifest excludes)"
( cd "$WAVE" && sha256sum -c out/MANIFEST.sha256 > ledgers/manifest_check.txt 2>&1 ) \
  && echo "MANIFEST_OK" || { echo "MANIFEST_FAILED"; rc=1; }

echo "== network audit"
EVENTS="$(grep -c '^EVENT ' "$MK_NET_AUDIT_LOG" 2>/dev/null)"; EVENTS="${EVENTS:-0}"
HOOKS="$(grep -c '^# hook-installed' "$MK_NET_AUDIT_LOG" 2>/dev/null)"; HOOKS="${HOOKS:-0}"
{
  echo "network audit receipts (hook installed): $HOOKS"
  echo "network events: $EVENTS"
  if [ "$EVENTS" = "0" ] && [ "$HOOKS" -gt 0 ]; then echo "NET_ZERO_PASS"; else echo "NET_FAIL"; fi
} | tee "$WAVE/ledgers/NET_AUDIT_SUMMARY.txt"
grep -q NET_ZERO_PASS "$WAVE/ledgers/NET_AUDIT_SUMMARY.txt" || rc=1

echo "== resource readings"
{
  echo "# available and peak readings, taken by the chain"
  echo "available_after_chain_gib: $(awk '/MemAvailable/{printf "%.1f", $2/1048576}' /proc/meminfo)"
  for f in ledgers/resource_*.txt; do [ -f "$f" ] && cat "$f"; done
  echo "this_wave_on_disk: $(du -sh "$WAVE" | cut -f1)"
} | tee "$WAVE/ledgers/RESOURCE_READINGS.txt"

exit "$rc"