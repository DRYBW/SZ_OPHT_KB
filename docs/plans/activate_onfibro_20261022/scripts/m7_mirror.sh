#!/usr/bin/env bash
# m7_mirror.sh -- mirror this card's evidence root into the project's plan root on the data volume.
#
# The repository holds the committed mirror (docs/plans/activate_onfibro_20261022); the project root
# /mnt/D/EyeKB/plans/ is where the laboratory reads its evidence. Both are kept, and the copy is
# verified file by file (sha256) rather than trusted: a mirror that cannot be checked is not a
# record.
#
# Usage: bash scripts/m7_mirror.sh [--dest <dir>]
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
DEST=/mnt/D/EyeKB/plans/activate_onfibro_20261022
for a in "$@"; do case "$a" in --dest=*) DEST="${a#--dest=}" ;; --dest) shift; DEST="$1" ;; esac; done
PY=/usr/bin/python3

echo "== mirror $WAVE -> $DEST"
mkdir -p "$DEST"
# rsync is not assumed: tar over a pipe, excluding the pipeline's binary work products (which the
# repository itself does not distribute) and the python caches.
( cd "$WAVE" && tar cf - \
    --exclude=__pycache__ --exclude='*.pyc' \
    --exclude=./out/g4_reanchor \
    PREREG_ACTIVATION_ONFIBRO_20261022.md REPORT.md scripts out pre_images ledgers logs ) \
  | ( cd "$DEST" && tar xf - )

echo "== verifying the copy, file by file"
DIFF=0; N=0
while IFS= read -r rel; do
  case "$rel" in
    ./out/g4_reanchor/*|*__pycache__*|*.pyc) continue ;;
  esac
  N=$((N+1))
  a="$WAVE/${rel#./}"; b="$DEST/${rel#./}"
  if [ ! -f "$b" ] || ! cmp -s "$a" "$b"; then
    DIFF=$((DIFF+1)); echo "   DIFFERS or MISSING: ${rel#./}"
  fi
done < <(cd "$WAVE" && find . -type f | sort)
echo "   compared $N files, differing $DIFF"

"$PY" - "$WAVE" "$DEST" "$N" "$DIFF" <<'PYEOF'
import hashlib, json, os, sys
wave, dest, n, diff = sys.argv[1], sys.argv[2], int(sys.argv[3]), int(sys.argv[4])
doc = {"probe": "m7_mirror.sh", "source": wave, "destination": dest,
       "files_compared": n, "files_differing": diff,
       "excluded": ["out/g4_reanchor/** (pipeline work products the repository does not distribute)",
                    "__pycache__/**"],
       "verdict": "PASS" if diff == 0 else "FAIL",
       "note": ("the repository holds the committed mirror; this copy is what the laboratory reads "
                "on the data volume, and it is verified rather than trusted")}
json.dump(doc, open(os.path.join(dest, "MIRROR_CHECK.json"), "w"), ensure_ascii=False, indent=1)
print(json.dumps(doc, ensure_ascii=False, indent=1))
sys.exit(0 if diff == 0 else 1)
PYEOF