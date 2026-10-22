#!/usr/bin/env bash
# One-shot: run the gate chain in a clean clone of the repository, at a path whose name contains
# spaces, without the author tree being reachable from the working directory.
#
#   bash <this script> <source repo> <clone dir> <corpus source> <interpreter with mcp>
#
# The corpus is copied in because it is not part of the git tree (contract §G2: the corpus is a
# Release asset, not a repository file); copying a local directory is not a download.
set -eu

SRC="$1"; CLONE="$2"; CORPUS_SRC="$3"; PY="${4:-/home/ubuntu/.conda/envs/pipeline_env/bin/python}"

rm -rf "$CLONE"
mkdir -p "$(dirname "$CLONE")"
git clone --quiet --no-hardlinks "$SRC" "$CLONE"
echo "[clone] $CLONE  head=$(git -C "$CLONE" rev-parse HEAD)  worktree_clean=$( [ -z "$(git -C "$CLONE" status --porcelain)" ] && echo yes || echo no )"

# the corpus the G3 anchors were built against, put where the one-click entry looks for it
mkdir -p "$CLONE/literature_db"
cp -r "$CORPUS_SRC" "$CLONE/literature_db/"
echo "[clone] corpus: $(du -sh "$CLONE/literature_db" | cut -f1) at literature_db/$(basename "$CORPUS_SRC")"

export PATH="/usr/local/bin:/usr/bin:/bin:$(dirname "$PY"):${PATH:-}"
export EYEKB_G3_PY="$PY"
export EYEKB_G7_PY="$PY"
export EYEKB_CORPUS="$CLONE/literature_db/$(basename "$CORPUS_SRC")"
export EYEKB_GATE_OUT="$CLONE/.gate_out"
unset PYTHONPATH || true

cd "$CLONE"
bash tests/run_gates.sh