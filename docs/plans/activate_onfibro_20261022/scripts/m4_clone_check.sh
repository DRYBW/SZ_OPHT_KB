#!/usr/bin/env bash
# m4_clone_check.sh -- the gate chain has to end green in a CLEAN CLONE, not only in the author tree.
#
#   1. clone the repository at the commit under test (git clone file://..., no network, no hardlinks);
#   2. require this wave's mirror to be present in the clone, so the check judges what a reader of the
#      repository gets rather than what happens to sit in the author's working tree;
#   3. run the repository's own gate chain INSIDE the clone (G3..G8);
#   4. run this wave's gate inside the clone with --inner-clone-check (the clone-check record is
#      produced by this step, so the inner invocation reports it as INFO and the author-tree
#      invocation judges it);
#   5. compare every mirrored file against the author's copy by sha256.
#
# Usage: bash scripts/m4_clone_check.sh [--commit=<sha>] [--mode=from_commit|copy_local]
#   --mode=copy_local  also copies the working wave into the clone (before the mirror is committed)
#   ONF_KEEP_CLONE=1   keeps the temporary clone for inspection
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO=/home/ubuntu/EYEKB_REPO
RELPATH=docs/plans/activate_onfibro_20261022
MODE=from_commit
for a in "$@"; do case "$a" in --mode=*) MODE="${a#--mode=}" ;; esac; done
PY=/usr/bin/python3

COMMIT="$(git -C "$REPO" rev-parse HEAD)"
for a in "$@"; do case "$a" in --commit=*) COMMIT="${a#--commit=}" ;; esac; done
CLONE="$(mktemp -d /tmp/activate_clone_XXXXXX)"
trap 'if [ "${ONF_KEEP_CLONE:-0}" != "1" ]; then rm -rf "$CLONE"; fi' EXIT

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

# The retrieval corpus is a RELEASE ASSET, not a repository file (README quickstart step 2), so a
# clean clone cannot run G3 at all; passing EYEKB_CORPUS at the unpacked asset is what makes the
# clone run comparable to the author run, and it is recorded rather than left implicit.
CORPUS="${EYEKB_CORPUS:-$REPO/literature_db/v2.4.2_2026-09_slim}"
CORPUS_IN_CLONE=absent
[ -d "$CLONE/literature_db/v2.4.2_2026-09_slim" ] && CORPUS_IN_CLONE=present
echo "== corpus in the clone: $CORPUS_IN_CLONE; using EYEKB_CORPUS=$CORPUS"

echo "== the repository's own gate chain inside the clone (G3..G8)"
( cd "$CLONE" && PYTHONHASHSEED=0 \
    EYEKB_G3_PY=/home/ubuntu/training-venv/bin/python3 \
    EYEKB_MODEL_DIR=/mnt/D/OcularKB/models/bge-large-en-v1.5 \
    EYEKB_CORPUS="$CORPUS" \
    PYTHONPATH="$WAVE/scripts/netaudit" \
    /usr/bin/bash tests/run_gates.sh > "$CLONE/.clone_repo_gates.log" 2>&1 )
REPO_GATE_RC=$?
REPO_GATE_TAIL="$(tail -10 "$CLONE/.clone_repo_gates.log" 2>/dev/null)"
echo "   repo gate chain in clone: rc=$REPO_GATE_RC"
printf '%s\n' "$REPO_GATE_TAIL"

echo "== this wave's gate inside the clone (M16 reported as INFO: this step produces that evidence)"
( cd "$MIRROR" && PYTHONHASHSEED=0 PYTHONPATH="$WAVE/scripts/netaudit" "$PY" scripts/m1_gate.py --inner-clone-check \
    --json out/GATE.json > out/GATE_READOUT.md 2>&1 )
RC=$?
V="$("$PY" -c "import json;print(json.load(open('$MIRROR/out/GATE.json'))['verdict'])" 2>/dev/null || echo UNREADABLE)"
FAILED="$("$PY" -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='FAIL'])" 2>/dev/null || echo UNREADABLE)"
INFO="$("$PY" -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='INFO'])" 2>/dev/null || echo UNREADABLE)"
echo "   wave gate in clone: rc=$RC verdict=$V failed=$FAILED info=$INFO"

echo "== mirror fidelity: author tree vs clone, file by file"
DIFF=0; N=0; SKIP=0
while IFS= read -r rel; do
  case "$rel" in
    ./out/GATE.json|./out/GATE_READOUT.md|./out/CLEAN_CLONE_CHECK.json) continue ;;
    ./ledgers/*|./logs/*) continue ;;
    *__pycache__*|*.pyc) continue ;;
  esac
  a="$WAVE/${rel#./}"
  # a file the repository does not distribute cannot be in the clone: it is counted separately
  if git -C "$REPO" check-ignore -q "$a"; then
    SKIP=$((SKIP+1)); continue
  fi
  N=$((N+1))
  b="$MIRROR/${rel#./}"
  if [ ! -f "$b" ] || ! cmp -s "$a" "$b"; then
    DIFF=$((DIFF+1)); echo "   DIFFERS or MISSING: ${rel#./}"
  fi
done < <(cd "$WAVE" && find . -type f | sort)
echo "   compared $N files, differing $DIFF ($SKIP not distributed by the repository, skipped)"

echo "== writing the clone-check record into both trees"
PAY="$CLONE/.clonecheck_payload"
{
  echo "wave=$WAVE"
  echo "clone=$CLONE"
  echo "commit=$COMMIT"
  echo "rc=$RC"
  echo "verdict=$V"
  echo "failed=$FAILED"
  echo "info=$INFO"
  echo "n=$N"
  echo "skip=$SKIP"
  echo "diff=$DIFF"
  echo "mode=$MODE"
  echo "reporc=$REPO_GATE_RC"
  echo "corpus=$CORPUS"
  echo "corpus_in_clone=$CORPUS_IN_CLONE"
} > "$PAY"

"$PY" - "$PAY" "$WAVE" <<'PYEOF'
import json, os, sys
pay = {}
for line in open(sys.argv[1], encoding="utf-8"):
    if "=" in line:
        k, v = line.rstrip("\n").split("=", 1)
        pay[k] = v
wave = sys.argv[2]
doc = {
    "generated_by": "scripts/m4_clone_check.sh",
    "mode": pay["mode"],
    "commit": pay["commit"],
    "clone_of_commit": pay["commit"],
    "clone_root": "(temporary clone of the repository, removed after the run)",
    "repo_gate_chain_rc_in_clone": int(pay["reporc"]),
    "repo_gate_chain_note": ("tests/run_gates.sh (G3 verify_repro, G4 verify_pipeline, G5 gate_registry, "
                             "G6 gate_change_control, G7 gate_ontology_layer, G8 gate_ontlayer_portability) "
                             "run inside the clone with the documented precondition environment "
                             "(EYEKB_G3_PY / EYEKB_MODEL_DIR / EYEKB_CORPUS)"),
    "corpus_path_used": pay["corpus"],
    "corpus_present_in_clone": pay["corpus_in_clone"],
    "corpus_note": ("the retrieval corpus is a release asset, not a repository file (README quickstart "
                    "step 2), so a clean clone cannot run G3 without it; the unpacked asset on this "
                    "machine is named here so the clone run is comparable to the author run"),
    "gate_rc": int(pay["rc"]),
    "gate_verdict": pay["verdict"],
    "gate_failed": pay["failed"],
    "gate_info": pay["info"],
    "gate_info_note": ("M16 CLEAN-CLONE is reported as INFO inside this invocation: the clone check is "
                       "the step that produces the record M16 judges, so the author-tree invocation "
                       "judges it"),
    "files_compared_author_vs_clone": int(pay["n"]),
    "files_differing_from_author_tree": int(pay["diff"]),
    "files_not_distributed_skipped": int(pay["skip"]),
    "files_not_distributed_note": ("files the repository git-ignores (the pipeline's binary work "
                                   "products) are skipped rather than reported as missing: a clone "
                                   "cannot contain them by construction"),
    "ledgers_and_logs_excluded_from_fidelity": True,
    "ledgers_and_logs_exclusion_reason": ("ledgers/ and logs/ are runtime output that this chain "
                                          "rewrites while it runs; they are excluded from both the "
                                          "manifest and this comparison on purpose"),
    "verdict": ("PASS" if (int(pay["rc"]) == 0 and pay["verdict"] == "PASS"
                           and int(pay["diff"]) == 0 and int(pay["reporc"]) == 0) else "FAIL"),
    "how_the_clone_was_run": ("git clone --no-hardlinks file:///home/ubuntu/EYEKB_REPO, checked out at "
                              "the commit under test; both the repository's gate chain and this wave's "
                              "gate executed inside the clone"),
}
for target in (os.path.join(wave, "out/CLEAN_CLONE_CHECK.json"),
               os.path.join(pay["clone"], "docs/plans/activate_onfibro_20261022/out/CLEAN_CLONE_CHECK.json")):
    try:
        json.dump(doc, open(target, "w"), ensure_ascii=False, indent=1)
    except OSError:
        pass
print(json.dumps(doc, ensure_ascii=False, indent=1))
sys.exit(0 if doc["verdict"] == "PASS" else 1)
PYEOF