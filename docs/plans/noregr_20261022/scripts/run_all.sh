#!/usr/bin/env bash
# run_all.sh -- one command that measures this wave, freezes it, judges it, and proves the default
# face did not move.
#
#   bash scripts/run_all.sh                 # measure + manifest + gate
#   bash scripts/run_all.sh --with-clone    # + the clean-clone check at the commit under test
#
# Zero network is enforced rather than claimed: the chain runs with PYTHONPATH pointing at
# scripts/netaudit, whose audit hook covers child processes, and ledgers/net_audit.log must show
# zero EVENT lines. A load-receipt line proves the hook was installed, so "no events" can never be
# read as "the hook never ran".
#
# Order matters. n6 (the default-face comparison) must run BEFORE the commit, because it compares
# the working tree against the parent commit's core in place; committing first would compare the
# change with itself. The manifest is taken after every artefact is written and before the gate, so
# a drifting artefact is the gate's job rather than a human's.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY=/usr/bin/python3
cd "$WAVE" || exit 2
mkdir -p out ledgers logs

export NR_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONHASHSEED=0
echo "# chain start $(date -Is)" >> "$NR_NET_AUDIT_LOG"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/logs/chain.log"; return "${PIPESTATUS[0]}"; }
step() {
  echo "== $1"
  run "$2" "${@:3}" || { echo "STEP FAILED: $1"; exit 1; }
}

step "n0  freeze the inputs (sha256 of every frozen input)"        scripts/n0_freeze_inputs.py
step "n1  reproduce the source-of-truth finding (G1)"              scripts/n1_reproduce.py
step "n2  sweep every exclusion row of every tissue (G2/G3)"       scripts/n2_sweep_exclusions.py
step "n3  the regression harness: acceptance-rule self-test (G7)"  scripts/n3_harness.py \
     --self-test --out out/harness
step "n4a harvest evidence for the carrier from the closed set"    scripts/n4a_mine_carrier.py
step "n4b build the carrier panel (G4 input)"                      scripts/n4b_build_carrier_panel.py
step "n4c register the library on the service surface"             scripts/n4c_register_library.py
step "n4d re-take the registry rows this card touches"             scripts/n4d_registry_update.py
step "n4e shared-ledger honesty fix for other cards' stale rows"  scripts/n4e_ledger_heal.py
step "n5  measure the fix on 28 volumes x 721 clusters (G4)"       scripts/n5_measure_fix.py
step "n6  the default-face red line (G5)"                          scripts/n6_default_face.py

echo "== the repository's own gate chain"
( cd /home/ubuntu/EYEKB_REPO && EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 \
    EYEKB_MODEL_DIR=/mnt/D/OcularKB/models/bge-large-en-v1.5 \
    /usr/bin/bash tests/run_gates.sh > "$WAVE/logs/repo_gates.log" 2>&1 )
REPO_RC=$?
tail -9 "$WAVE/logs/repo_gates.log"
if [ "$REPO_RC" != 0 ]; then echo "REPO GATE CHAIN FAILED (rc=$REPO_RC)"; exit 1; fi

step "n7  manifest (taken before the gate)"                        scripts/n7_manifest.py

echo "== n8 gate (author tree)"
"$PY" scripts/n8_gate.py --json out/GATE.json 2>&1 | tee -a "$WAVE/logs/chain.log"
GATE_RC="${PIPESTATUS[0]}"
if [ "$GATE_RC" != 0 ]; then
  echo "WAVE GATE FAILED (rc=$GATE_RC). If the only failure is N12 CLEAN-CLONE, commit the mirror"
  echo "and run: bash scripts/n9_clone_check.sh   then re-run: $PY scripts/n8_gate.py"
fi
echo "== chain end $(date -Is) rc=$GATE_RC" >> "$NR_NET_AUDIT_LOG"
exit "$GATE_RC"