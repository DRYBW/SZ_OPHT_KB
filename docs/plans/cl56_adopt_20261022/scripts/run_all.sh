#!/usr/bin/env bash
# run_all.sh -- the whole CL-56 chain, in order, with the zero-network audit hook installed.
#
# Everything runs as a child of this shell with PYTHONPATH pointing at the audit hook only (the `site`
# module imports `sitecustomize` at interpreter start, so every child process is audited too) and every
# service switch cleared. Nothing here downloads or connects; the hook proves it.
#
#   bash scripts/run_all.sh          # full chain
set -uo pipefail
W=/mnt/D/EyeKB/plans/cl56_adopt_20261022
cd "$W" || exit 2
mkdir -p out logs ledgers pre_images
export CL56_NET_AUDIT_LOG="$W/ledgers/net_audit.log"
export PYTHONPATH="$W/discipline/net_audit"
export PYTHONDONTWRITEBYTECODE=1
export PYTHONHASHSEED=0
unset EYEKB_ACT_CL56 EYEKB_ACT_V6 EYEKB_ACT_K9 EYEKB_ACT_ANTSEG EYEKB_ACT_ONFIBRO \
      EYEKB_ACT_SUBTYPE EYEKB_TISSUE_SCOPE EYEKB_KB_ANTIUNION EYEKB_STATE_GUARD \
      EYEKB_S0_ENFORCE EYEKB_FALLBACK_WIDEN EYEKB_KBGOV_B5 EYEKB_ONT_LAYER 2>/dev/null
PY=/usr/bin/python3
rc=0
step() {                       # step <name> <script...>
  local name="$1"; shift
  printf '\n=== [%s] %s\n' "$(date +%H:%M:%S)" "$name"
  "$@" > "logs/$name.log" 2>&1
  local r=$?
  tail -3 "logs/$name.log"
  [ $r -ne 0 ] && { echo "STEP FAILED rc=$r: $name"; rc=$r; }
  return 0
}
step f0_freeze_inputs   "$PY" scripts/f0_freeze_inputs.py
step r0_recon           "$PY" scripts/r0_recon.py
step s1_scope           "$PY" scripts/s1_scope.py
step b1_build           "$PY" scripts/b1_build_increment.py
step w1_wire            "$PY" scripts/w1_wire.py
step m1_measure         "$PY" scripts/m1_measure.py
step a1_acceptance      "$PY" scripts/a1_acceptance.py
step s2_sensitivity     "$PY" scripts/s2_sensitivity.py
step m2_default_face    "$PY" scripts/m2_default_face.py
echo
echo "=== chain rc=$rc"
exit $rc