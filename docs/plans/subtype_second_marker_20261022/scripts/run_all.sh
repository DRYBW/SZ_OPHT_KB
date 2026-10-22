#!/usr/bin/env bash
# run_all.sh -- one command that re-runs this wave's whole read-only chain under the network audit
# hook, so "zero network" is a receipt rather than a claim.
#
#   bash scripts/run_all.sh
#
# Order matters: freeze inputs -> mine the literature -> measurability -> the ruler (control and
# augmented) -> the flip table and the attribution check -> robustness -> the panel -> registration
# (idempotent: it skips when already on disk) -> the default-face measurement (which writes the blob
# to commit, so it must run BEFORE the commit).
set -uo pipefail

# The Hermes background terminal strips PATH (a known, reproducible bug): with no PATH the shell
# cannot find dirname/mkdir/date/systemd-run and the whole chain dies before its first step.  Restore
# it explicitly rather than debugging the harness.
export PATH="/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY=/usr/bin/python3
cd "$WAVE" || exit 2
mkdir -p out logs ledgers

export S2M_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"
export PYTHONHASHSEED=0
echo "# chain start $(date -Is)" >> "$S2M_NET_AUDIT_LOG"

step() {
  name="$1"; shift
  echo "== $name"
  "$@" 2>&1 | tee -a "$WAVE/logs/chain.log"
  rc="${PIPESTATUS[0]}"
  if [ "$rc" != 0 ]; then echo "STEP FAILED rc=$rc: $name"; exit 1; fi
}

systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G "$PY" "$HERE/m0_freeze_inputs.py" \
  || { echo "m0 failed"; exit 1; }
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=2G "$PY" "$HERE/m1e_mine_lit_v5.py" \
  || { echo "m1e failed"; exit 1; }
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G "$PY" "$HERE/m2_measurability.py" \
  || { echo "m2 failed"; exit 1; }
# m3's augmented arm is EXPECTED to fail: the frozen ruler crashes while reporting marker_detail for a
# constant marker (see out/RULER_PATCH.json).  Its control arm is what matters here.
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G "$PY" "$HERE/m3_remeasure.py" \
  >> "$WAVE/logs/m3.log" 2>&1 || echo "   (m3 augmented arm failed as expected -- the frozen ruler's reporting bug)"
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G "$PY" "$HERE/m3b_remeasure_local.py" \
  || { echo "m3b failed"; exit 1; }
systemd-run --user --scope -p MemoryMax=8G -p MemorySwapMax=2G "$PY" "$HERE/m4_flips.py" \
  || { echo "m4 failed"; exit 1; }
systemd-run --user --scope -p MemoryMax=6G -p MemorySwapMax=2G "$PY" "$HERE/m4b_verify_claims.py" \
  || { echo "m4b failed"; exit 1; }
"$PY" "$HERE/m5_robustness.py" || { echo "m5 failed"; exit 1; }
"$PY" "$HERE/m6_build_panel.py" || { echo "m6 failed"; exit 1; }
"$PY" "$HERE/m7_register_library.py" || { echo "m7 failed"; exit 1; }
"$PY" "$HERE/m9_default_face.py" || { echo "m9 failed"; exit 1; }

echo "== audit receipt"
RECEIPTS=$(grep -c '^# hook-installed' "$S2M_NET_AUDIT_LOG" || true)
EVENTS=$(grep -c '^EVENT' "$S2M_NET_AUDIT_LOG" || true)
echo "load receipts=$RECEIPTS  EVENT lines=$EVENTS"
echo "== chain end $(date -Is) receipts=$RECEIPTS events=$EVENTS" >> "$S2M_NET_AUDIT_LOG"
[ "$RECEIPTS" -gt 0 ] || { echo "NO AUDIT HOOK RECEIPT -- zero-event claim is void"; exit 1; }
[ "$EVENTS" -eq 0 ] || { echo "NETWORK EVENTS PRESENT: $EVENTS"; exit 1; }
exit 0