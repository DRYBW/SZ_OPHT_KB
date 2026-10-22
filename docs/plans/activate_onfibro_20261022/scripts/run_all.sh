#!/usr/bin/env bash
# run_all.sh -- one command that re-measures the activation, re-registers what it invalidates, runs
# the repository's gate chain, freezes this wave and judges it.
#
#   bash scripts/run_all.sh                 # measure + registrations + gates + manifest + wave gate
#   bash scripts/run_all.sh --with-commit   # + stage, take the release identity, commit locally
#   bash scripts/run_all.sh --with-clone    # + the clean-clone check at the commit under test
#
# Order matters and is not arbitrary:
#   * the flip (l1) and its pre-image (l0) are ONE-SHOT and already applied -- l1 runs in verify mode
#     here, so the chain cannot silently re-apply or lose the pre-image;
#   * the measurement (l2, l3, l3c) must run against the flipped core before anything is committed;
#   * docs/VERIFY_CONTRACT.md must reach its final bytes (l5) BEFORE the registry row for it is
#     re-taken (l4), otherwise the row would register a stale sha;
#   * the release identity is taken against the STAGED tree (--source index) after everything else is
#     staged, because the records are excluded from their own coverage;
#   * docs/W3_MANIFEST.sha256 is re-frozen after the registry's final bytes exist, and the release
#     identity is taken after that re-freeze -- the manifest is inside the identity's coverage, so a
#     take that precedes it makes `--check` fail (measured on this card's first attempt).
#
# Zero network is enforced rather than claimed: the chain runs with PYTHONPATH pointing at
# scripts/netaudit, whose audit hook covers child processes, and ledgers/net_audit.log must show
# zero connecting/HTTP EVENT lines. A load-receipt line proves the hook was installed, so "no
# events" can never be read as "the hook never ran".
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO=/home/ubuntu/EYEKB_REPO
PY=/usr/bin/python3
cd "$WAVE" || exit 2
mkdir -p out ledgers logs

export ONF_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
# PINNED on purpose: the worker sandbox exports another venv's site-packages on
# PYTHONPATH, which shadows the repository's dependencies (measured 2026-10-22: the
# tool-panel probe became rc=3 "cannot be driven", and numpy failed to load its C extension
# inside the G4 verifier). Only the audit hook's own directory is exported.
export PYTHONPATH="$WAVE/scripts/netaudit"
export PYTHONHASHSEED=0
export PYTHONDONTWRITEBYTECODE=1
echo "# chain start $(date -Is)" >> "$ONF_NET_AUDIT_LOG"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/logs/chain.log"; return "${PIPESTATUS[0]}"; }
step() { echo "== $1"; run "$2" "${@:3}" || { echo "STEP FAILED: $1"; exit 1; }; }

DO_COMMIT=0; DO_CLONE=0
for a in "$@"; do case "$a" in --with-commit) DO_COMMIT=1 ;; --with-clone) DO_CLONE=1 ;; esac; done

step "l1  the flip (verify mode: the change is already applied)"    scripts/l1_flip_apply.py
step "l2  measure the activation with the reused harness"           scripts/l2_flip_measure.py
step "l3  the default face: kill switch + delta census"             scripts/l3_default_face.py
step "l3c the field-level diff of the delta"                        scripts/l3c_field_diff.py
step "g4  re-anchor the G4 three byte anchors (reason recorded, pre-image kept)" \
                                                                    scripts/g4_reanchor.py
step "l5  register the default-ON precondition (R8)"                scripts/l5_verify_contract.py
step "l4  re-take the registry rows this activation invalidates"    scripts/l4_registry_rows.py
step "l6  the change-control instance row (27 columns)"             scripts/l6_g6_row.py

echo "== the repository's own gate chain (author tree)"
( cd "$REPO" && PYTHONHASHSEED=0 \
    EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 \
    EYEKB_MODEL_DIR=/mnt/D/OcularKB/models/bge-large-en-v1.5 \
    PYTHONPATH="$WAVE/scripts/netaudit" \
    /usr/bin/bash tests/run_gates.sh > "$WAVE/out/REPO_GATES.log" 2>&1 )
REPO_RC=$?
tail -12 "$WAVE/out/REPO_GATES.log"
if [ "$REPO_RC" != 0 ]; then echo "REPO GATE CHAIN FAILED (rc=$REPO_RC) -- see out/REPO_GATES.log"; exit 1; fi

if [ "$DO_COMMIT" = 1 ]; then
  echo "== staging and taking the release identity against the staged tree"
  cd "$REPO" || exit 2
  git add -A docs/plans/activate_onfibro_20261022 mcp_server/eyekb_core.py \
      docs/W3_PIPELINE_REGISTRY.tsv docs/VERIFY_CONTRACT.md \
      docs/CHANGE_CONTROL_G6_INSTANCE.tsv docs/GATE_INVENTORY_G5G6.tsv \
      tests/G4_EXPECTED.json tests/G4_EXPECTED_PRE-ONFIBRO.json docs/RELEASE_IDENTITY.json \
      docs/RELEASE_MANIFEST_v1.json docs/W3_MANIFEST.sha256 || exit 2
  echo "== re-freezing docs/W3_MANIFEST.sha256 (LAST content change before the identity)"
  "$PY" "$WAVE/scripts/m3_w3_manifest.py" --write || exit 2
  git add docs/W3_MANIFEST.sha256 || exit 2
  echo "== taking the release identity LAST, against the fully staged tree"
  "$PY" scripts/release_identity.py --take --source index || exit 2
  git add docs/RELEASE_IDENTITY.json docs/RELEASE_MANIFEST_v1.json || exit 2
  "$PY" scripts/release_identity.py --check --source index || exit 2
  echo "== commit (local only; the coordinator pushes)"
  git -c user.name="pi-chief" -c user.email="pi-chief@localhost" commit -q \
      -m "activate onfibro_v13 on the default route (PI-signed): pre-register, flip, prove the kill switch restores the pre-flip default byte-for-byte, re-measure 28 volumes x 721 clusters, re-register the changed identities" \
      -m "Evidence root: docs/plans/activate_onfibro_20261022/ (pre-registration, scripts, out/, REPORT.md).
No push: the coordinator pushes after verification." || exit 2
  git --no-pager log --oneline -1
fi

cd "$WAVE" || exit 2

# Order inside the record trio matters as much as the order of the measurement steps: the gate writes
# out/GATE.json, the report reads that verdict, and the manifest hashes both -- so the report can
# never disagree with the readout it quotes, and nothing is written after the manifest.
step "m6  assemble REPORT.md from the artefacts"                  scripts/m6_report.py
step "m2  manifest (taken by the gate that judges it)"             scripts/m2_manifest.py
echo "== m1 gate (author tree)"
"$PY" scripts/m1_gate.py --json out/GATE.json 2>&1 | tee -a "$WAVE/logs/chain.log"
GATE_RC="${PIPESTATUS[0]}"

if [ "$DO_CLONE" = 1 ]; then
  echo "== the clean-clone check"
  bash "$WAVE/scripts/m4_clone_check.sh" --commit="$(git -C "$REPO" rev-parse HEAD)" || true
  echo "== re-run the wave gate in the author tree so M16 judges the clone record"
  step "m6  refresh REPORT.md with the clean-clone reading"        scripts/m6_report.py
  step "m2  refresh the manifest"                                  scripts/m2_manifest.py
  "$PY" scripts/m1_gate.py --json out/GATE.json 2>&1 | tee -a "$WAVE/logs/chain.log"
  GATE_RC="${PIPESTATUS[0]}"
fi

if [ "$GATE_RC" != 0 ]; then
  echo "WAVE GATE FAILED (rc=$GATE_RC). If the only failure is M16 CLEAN-CLONE, commit the mirror"
  echo "and run: bash scripts/m4_clone_check.sh"
fi
echo "== chain end $(date -Is) rc=$GATE_RC" >> "$ONF_NET_AUDIT_LOG"
exit "$GATE_RC"