#!/usr/bin/env bash
# n9_clone_check.sh -- the gate chain has to end green in a clean clone, not only in the author tree.
#
#   1. clone the repository at the commit under test (git clone file://..., no network, no hardlinks);
#   2. require this wave's mirror to be present in the clone, so the check judges what a reader of
#      the repository gets, not what happens to sit in the author's working tree;
#   3. run the repository's own gate chain INSIDE the clone (G3..G8);
#   4. run this wave's gate inside the clone with --inner-clone-check (the clone-check record is
#      produced by this step, so the inner invocation reports it as INFO and the author-tree
#      invocation judges it);
#   5. compare every mirrored file against the author's copy by sha256.
#
# Usage: bash scripts/n9_clone_check.sh [--mode=from_commit|copy_local]
#   --mode=from_commit  judges the committed mirror (default; run it after committing)
#   --mode=copy_local   also copies the working wave into the clone (before the mirror is committed)
#   NR_KEEP_CLONE=1     keeps the temporary clone for inspection
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO=/home/ubuntu/EYEKB_REPO
RELPATH=docs/plans/noregr_20261022
MODE=from_commit
for a in "$@"; do case "$a" in --mode=*) MODE="${a#--mode=}" ;; esac; done

PY=/usr/bin/python3
COMMIT="$(git -C "$REPO" rev-parse HEAD)"
CLONE="$(mktemp -d /tmp/noregr_clone_XXXXXX)"
trap 'if [ "${NR_KEEP_CLONE:-0}" != "1" ]; then rm -rf "$CLONE"; fi' EXIT

echo "== clone of $COMMIT -> $CLONE"
git clone -q --no-hardlinks "file://$REPO" "$CLONE" || { echo "clone failed"; exit 2; }
git -C "$CLONE" checkout -q "$COMMIT" || exit 2
MIRROR="$CLONE/$RELPATH"
if [ "$MODE" = "copy_local" ]; then
  echo "== mode copy_local: copying the working wave into the clone"
  mkdir -p "$MIRROR"
  ( cd "$WAVE" && tar cf - --exclude=__pycache__ --exclude='*.pyc' \
      --exclude=./out/CLEAN_CLONE_CHECK.json --exclude=./out/GATE.json \
      --exclude=./out/GATE_READOUT.md . ) | ( cd "$MIRROR" && tar xf - )
fi
if [ ! -d "$MIRROR" ]; then echo "the wave is not present in the clone at $RELPATH"; exit 3; fi

echo "== the repository's own gate chain inside the clone (G3..G8)"
( cd "$CLONE" && PYTHONHASHSEED=0 \
    EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 \
    EYEKB_MODEL_DIR=/mnt/D/OcularKB/models/bge-large-en-v1.5 \
    /usr/bin/bash tests/run_gates.sh > "$CLONE/.clone_repo_gates.log" 2>&1 )
REPO_GATE_RC=$?
REPO_GATE_TAIL="$(tail -9 "$CLONE/.clone_repo_gates.log" 2>/dev/null)"
echo "   repo gate chain in clone: rc=$REPO_GATE_RC"
printf '%s\n' "$REPO_GATE_TAIL"

echo "== this wave's gate inside the clone (N12 reported as INFO: this step produces that evidence)"
( cd "$MIRROR" && PYTHONHASHSEED=0 "$PY" scripts/n8_gate.py --inner-clone-check \
    --json out/GATE.json > out/GATE_READOUT.md 2>&1 )
RC=$?
V="$("$PY" -c "import json;print(json.load(open('$MIRROR/out/GATE.json'))['verdict'])" 2>/dev/null || echo UNREADABLE)"
FAILED="$("$PY" -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='FAIL'])" 2>/dev/null || echo UNREADABLE)"
INFO="$("$PY" -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='INFO'])" 2>/dev/null || echo UNREADABLE)"
echo "   wave gate in clone: rc=$RC verdict=$V failed=$FAILED info=$INFO"

echo "== mirror fidelity: author tree vs clone, file by file"
DIFF=0; N=0
while IFS= read -r rel; do
  case "$rel" in
    ./out/GATE.json|./out/GATE_READOUT.md|./out/CLEAN_CLONE_CHECK.json) continue ;;
    ./ledgers/*|./logs/*) continue ;;
    *__pycache__*|*.pyc) continue ;;
  esac
  N=$((N+1))
  a="$WAVE/${rel#./}"; b="$MIRROR/${rel#./}"
  if [ ! -f "$b" ] || ! cmp -s "$a" "$b"; then
    DIFF=$((DIFF+1)); echo "   DIFFERS or MISSING: ${rel#./}"
  fi
done < <(cd "$WAVE" && find . -type f | sort)
echo "   compared $N files, differing $DIFF"

echo "== writing the clone-check record into both trees"
"$PY" - "$WAVE" "$CLONE" "$COMMIT" "$RC" "$V" "$FAILED" "$INFO" "$N" "$DIFF" "$MODE" \
      "$REPO_GATE_RC" <<PYEOF
import json, os, sys
(wave, clone, commit, rc, verdict, failed, info, n, diff, mode, reporc) = sys.argv[1:12]
doc = {
    "generated_by": "scripts/n9_clone_check.sh",
    "mode": mode,
    "commit": commit,
    "clone_of_commit": commit,
    "clone_root": "(temporary clone of the repository, removed after the run)",
    "repo_gate_chain_rc_in_clone": int(reporc),
    "repo_gate_chain_note": "tests/run_gates.sh (G3 verify_repro, G4 verify_pipeline, G5 "
                            "gate_registry, G6 gate_change_control, G7 gate_ontology_layer, G8 "
                            "gate_ontlayer_portability), run inside the clone with the documented "
                            "precondition environment (EYEKB_G3_PY / EYEKB_MODEL_DIR)",
    "gate_rc": int(rc),
    "gate_verdict": verdict,
    "gate_failed": failed,
    "gate_info": info,
    "gate_info_note": ("N12 CLEAN-CLONE is reported as INFO inside this invocation: the clone check "
                       "is the step that produces the record N12 judges, so the author-tree "
                       "invocation judges it"),
    "files_compared_author_vs_clone": int(n),
    "files_differing_from_author_tree": int(diff),
    "ledgers_and_logs_excluded_from_fidelity": True,
    "ledgers_and_logs_exclusion_reason": ("ledgers/ and logs/ are runtime output that this chain "
                                          "rewrites while it runs; they are excluded from both the "
                                          "manifest and this comparison on purpose, and the reader "
                                          "is told so rather than left to guess"),
    "verdict": ("PASS" if (int(rc) == 0 and verdict == "PASS" and int(diff) == 0
                           and int(reporc) == 0) else "FAIL"),
    "how_the_clone_was_run": ("git clone --no-hardlinks file:///home/ubuntu/EYEKB_REPO, checked out "
                              "at the commit under test; both the repository's gate chain and this "
                              "wave's gate executed inside the clone"),
}
for target in (os.path.join(wave, "out/CLEAN_CLONE_CHECK.json"),
               os.path.join(clone, "docs/plans/noregr_20261022/out/CLEAN_CLONE_CHECK.json")):
    try:
        json.dump(doc, open(target, "w"), ensure_ascii=False, indent=1)
    except OSError:
        pass
print(json.dumps(doc, ensure_ascii=False, indent=1))
sys.exit(0 if doc["verdict"] == "PASS" else 1)
PYEOF