#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Step D1 — take the before/after pair of shipped-surface dumps, from committed bytes.
#
#   before = the HEAD tree extracted with `git archive` into a scratch directory, so the
#            pre-change surface is the committed content and not "whatever the work tree
#            happened to hold before the editor touched it".
#   after  = /home/ubuntu/EYEKB_REPO itself, i.e. the working tree that carries the fix.
#
# Both dumps are produced by the same script (a1_dump_panel.py) with the same interpreter, so the
# two files are comparable call by call; c2_stage_surface.py reads the pair.
#
# Usage: bash d1_dump_pair.sh <out-dir> [<tag>]
set -u
OUT="${1:?out-dir}"; TAG="${2:-run}"
PY=/home/ubuntu/training-venv/bin/python3
REPO=/home/ubuntu/EYEKB_REPO
HERE="$(cd "$(dirname "$0")" && pwd)"
HEAD_SHA="$(cd "$REPO" && git rev-parse HEAD)"
TREE="$OUT/tree_HEAD_${HEAD_SHA:0:7}"

mkdir -p "$OUT"
if [ ! -d "$TREE" ]; then
  mkdir -p "$TREE"
  (cd "$REPO" && git archive "$HEAD_SHA") | tar -x -C "$TREE"
fi

echo "=== before: HEAD ${HEAD_SHA:0:7} extracted at $TREE ==="
"$PY" "$HERE/a1_dump_panel.py" --repo "$TREE" --out "$OUT/DUMP_PRE_HEAD_${TAG}.json" \
  --interpreter "$PY" 2>&1 | tail -2

echo "=== after: working tree $REPO ==="
"$PY" "$HERE/a1_dump_panel.py" --repo "$REPO" --out "$OUT/DUMP_POST_WORKTREE_${TAG}.json" \
  --interpreter "$PY" 2>&1 | tail -2

echo "done"