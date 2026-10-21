#!/usr/bin/env bash
# mirror_to_repo.sh — copy this wave into the repository's review-layer mirror, and prove it.
#
# The construction site is the data volume (/mnt/D/EyeKB/plans/...); the repository keeps a mirror
# under docs/plans/<wave>/. This script copies (never moves), lists what it copied, and then
# compares author tree against mirror file by file so "the mirror is faithful" is measured.
#
# Excluded from the mirror, with the reason:
#   out/CLEAN_CLONE_CHECK.json   a runtime readout of the clone check; the clone writes its own
#   __pycache__/, *.pyc          interpreter byproducts
#   out/GATE_pass1*.json|md      the clone check's first pass, produced inside a clone
# (out/GATE.json and out/GATE_READOUT.md ARE mirrored: they are this wave's gate evidence.)
#
# Usage: bash scripts/mirror_to_repo.sh [--check-only]
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
REPO=/home/ubuntu/EYEKB_REPO
DEST="$REPO/docs/plans/devlineage_20261021/hygiene_v5_20261022"

if [ "${1:-}" != "--check-only" ]; then
  echo "== copying $WAVE -> $DEST (copy, not move; the originals stay)"
  mkdir -p "$DEST"
  ( cd "$WAVE" && tar cf - \
      --exclude=__pycache__ --exclude='*.pyc' \
      --exclude=./out/CLEAN_CLONE_CHECK.json \
      --exclude='./out/GATE_pass1*' . ) | ( cd "$DEST" && tar xf - )
fi

echo "== fidelity: author tree vs mirror"
N=0; DIFF=0
while IFS= read -r rel; do
  case "$rel" in
    ./out/CLEAN_CLONE_CHECK.json) continue ;;
    ./ledgers/*|./logs/*) continue ;;
    ./out/GATE_pass1*|*__pycache__*|*.pyc) continue ;;
  esac
  N=$((N+1))
  a="$WAVE/${rel#./}"; b="$DEST/${rel#./}"
  if [ ! -f "$b" ] || ! cmp -s "$a" "$b"; then DIFF=$((DIFF+1)); echo "   DIFF/MISSING ${rel#./}"; fi
done < <(cd "$WAVE" && find . -type f | sort)
echo "   compared $N files, differing $DIFF"
echo "   mirror tree: $(du -sh "$DEST" | cut -f1), $(find "$DEST" -type f | wc -l) files"
[ "$DIFF" = "0" ] && echo "MIRROR_FAITHFUL" || { echo "MIRROR_NOT_FAITHFUL"; exit 1; }