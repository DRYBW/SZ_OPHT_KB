#!/usr/bin/env bash
# -*- coding: utf-8 -*-
# Step 3 — bisect the one digest move the panel probe could not attribute.
#
# The probe keeps digests only, so it cannot say which of the five moved calls changed because the
# server refused the arguments and which changed because an answer's text moved. It also cannot say
# *when* the one answered move happened. This driver extracts each commit's tree to its own
# directory (via `git archive`, so the repository's own work tree and .git state are untouched) and
# dumps the same twelve calls against each of them.
#
# Usage: bash b1_bisect.sh <out-dir> <interpreter> <commit> [<commit> ...]
set -u
OUT="$1"; shift
PY="$1"; shift
REPO=/home/ubuntu/EYEKB_REPO
HERE="$(cd "$(dirname "$0")" && pwd)"
mkdir -p "$OUT"
for c in "$@"; do
  short="$(cd "$REPO" && git rev-parse --short "$c")"
  full="$(cd "$REPO" && git rev-parse "$c")"
  ws="$OUT/tree_$short"
  if [ ! -d "$ws" ]; then
    mkdir -p "$ws"
    (cd "$REPO" && git archive "$full") | tar -x -C "$ws"
  fi
  echo "=== $short  $full  $(cd "$REPO" && git log -1 --format=%s "$c") ==="
  "$PY" "$HERE/a1_dump_panel.py" --repo "$ws" --out "$OUT/dump_$short.json" \
    --interpreter "$PY" >"$OUT/dump_$short.log" 2>&1
  tail -1 "$OUT/dump_$short.log"
done
echo "done -> $OUT"