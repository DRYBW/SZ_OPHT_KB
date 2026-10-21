#!/usr/bin/env bash
# w5_07_clone_check.sh — the gate chain has to end green in a clean clone, not only here.
#
# Sequence (and why it is this sequence):
#   1. clone the repository at the commit under test with `git clone file://...` (no network, no
#      hardlinks) into a fresh temporary directory;
#   2. require the wave's mirror to be present in that clone, so the check judges what a reader of
#      the repository gets, not what happens to sit in the author's working tree;
#   3. run the wave's gate *inside the clone* with --inner-clone-check: every check is judged
#      there except the clone-check record itself, which this very step produces and which the
#      author-tree invocation judges (reported as INFO, not silently passed);
#   4. compare every mirrored file against the author's copy by sha256, so "the mirror is
#      faithful" is measured rather than assumed;
#   5. write the clone-check record into both trees for the author-tree gate to judge.
#
# Usage: bash scripts/w5_07_clone_check.sh [--mode=from_commit|copy_local]
#   --mode=from_commit  judges the committed mirror (the default; run it after committing)
#   --mode=copy_local   also copies the working wave into the clone (before the mirror is committed)
#   W5_KEEP_CLONE=1     keeps the temporary clone for inspection
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO=/home/ubuntu/EYEKB_REPO
RELPATH=docs/plans/devlineage_20261021/hygiene_v5_20261022
MODE=from_commit
for a in "$@"; do case "$a" in --mode=*) MODE="${a#--mode=}" ;; esac; done

COMMIT="$(git -C "$REPO" rev-parse HEAD)"
CLONE="$(mktemp -d /tmp/w5_clone_XXXXXX)"
trap 'if [ "${W5_KEEP_CLONE:-0}" != "1" ]; then rm -rf "$CLONE"; fi' EXIT

echo "== clone of $COMMIT -> $CLONE"
git clone -q --no-hardlinks "file://$REPO" "$CLONE" || { echo "clone failed"; exit 2; }
git -C "$CLONE" checkout -q "$COMMIT" || exit 2
MIRROR="$CLONE/$RELPATH"
if [ "$MODE" = "copy_local" ]; then
  echo "== mode copy_local: copying the working wave into the clone"
  mkdir -p "$MIRROR"
  ( cd "$WAVE" && tar cf - --exclude=__pycache__ --exclude='*.pyc' \
      --exclude=./out/CLEAN_CLONE_CHECK.json . ) | ( cd "$MIRROR" && tar xf - )
fi
if [ ! -d "$MIRROR" ]; then echo "the wave is not present in the clone at $RELPATH"; exit 3; fi

echo "== gate inside the clone (G12 reported as INFO: this step produces that evidence)"
( cd "$MIRROR" && W5_DATA_ROOT="${W5_DATA_ROOT:-/mnt/D/EyeKB}" \
    /usr/bin/python3 scripts/w5_06_gate.py --inner-clone-check --json out/GATE.json \
    > out/GATE_READOUT.md 2>&1 )
RC=$?
V="$(/usr/bin/python3 -c "import json;print(json.load(open('$MIRROR/out/GATE.json'))['verdict'])" 2>/dev/null || echo UNREADABLE)"
FAILED="$(/usr/bin/python3 -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='FAIL'])" 2>/dev/null || echo UNREADABLE)"
INFO="$(/usr/bin/python3 -c "import json;print([c['code'] for c in json.load(open('$MIRROR/out/GATE.json'))['checks'] if c['status']=='INFO'])" 2>/dev/null || echo UNREADABLE)"
echo "   clone gate: rc=$RC verdict=$V failed=$FAILED info=$INFO"

echo "== mirror fidelity: author tree vs clone, file by file"
DIFF=0; N=0
while IFS= read -r rel; do
  case "$rel" in
    ./out/GATE.json|./out/GATE_READOUT.md) continue ;;
    ./out/CLEAN_CLONE_CHECK.json) continue ;;
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
/usr/bin/python3 - "$WAVE" "$CLONE" "$COMMIT" "$RC" "$V" "$FAILED" "$INFO" "$N" "$DIFF" "$MODE" <<'PYEOF'
import json, os, sys
(wave, clone, commit, rc, verdict, failed, info, n, diff, mode) = sys.argv[1:11]
doc = {
    "generated_by": "scripts/w5_07_clone_check.sh",
    "mode": mode,
    "commit": commit,
    "clone_of_commit": commit,
    "clone_root": "(temporary clone of the repository, removed after the run)",
    "gate_rc": int(rc),
    "gate_verdict": verdict,
    "gate_failed": failed,
    "gate_info": info,
    "gate_info_note": ("G12 is reported as INFO inside this invocation: the clone check is the "
                       "step that produces the record G12 judges, so the author-tree invocation "
                       "judges it instead"),
    "files_compared_author_vs_clone": int(n),
    "files_differing_from_author_tree": int(diff),
    "verdict": ("PASS" if (int(rc) == 0 and verdict == "PASS" and int(diff) == 0) else "FAIL"),
    "how_the_clone_was_run": ("git clone --no-hardlinks file:///home/ubuntu/EYEKB_REPO, checked "
                              "out at the commit under test; the wave's gate executed inside the "
                              "clone with W5_DATA_ROOT pointing at the local material, which is "
                              "outside the repository by design"),
}
for target in (os.path.join(wave, "out/CLEAN_CLONE_CHECK.json"),
               os.path.join(clone, "docs/plans/devlineage_20261021/hygiene_v5_20261022/out/"
                            "CLEAN_CLONE_CHECK.json")):
    try:
        json.dump(doc, open(target, "w"), ensure_ascii=False, indent=1)
    except OSError:
        pass
print(json.dumps(doc, ensure_ascii=False, indent=1))
sys.exit(0 if doc["verdict"] == "PASS" else 1)
PYEOF