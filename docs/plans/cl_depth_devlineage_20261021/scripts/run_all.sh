#!/usr/bin/env bash
# run_all.sh - one command that reproduces this wave's artefacts and then judges them.
#
#   bash scripts/run_all.sh            # build, replay, gates, manifest
#   bash scripts/run_all.sh --no-replay
#
# Zero network is enforced by an audit hook (scripts/netaudit/sitecustomize.py): the chain runs
# with PYTHONPATH pointing at it and the ledger must show zero event lines. The heavy corpus
# scans run under systemd-run --user with a memory cap, as this project requires for heavy steps.
#
# Order matters: every artefact is written before the manifest is taken, and the gates are run
# after the manifest so that a drifting artefact is caught by the gate rather than by hand.
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY="${PY:-/usr/bin/python3}"
cd "$WAVE" || exit 2

mkdir -p out ledgers logs
export CL_DEPTH_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
# a header line only; event lines are what the check counts
echo "# chain start $(date -Is)" >> "$CL_DEPTH_NET_AUDIT_LOG"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/ledgers/chain.log"; return "${PIPESTATUS[0]}"; }

BUILDS=(scripts/a1_build_nav.py scripts/a2_fourway_721.py scripts/a3_child_candidates.py
        scripts/b1_build_lineage.py scripts/c1_benchmark_gapcheck.py)
CORPUS=(scripts/b0_corpus_index.py scripts/b0b_germlayer_cooccurrence.py)

echo "=== corpus scans (systemd-run --user, MemoryMax=8G) ==="
for s in "${CORPUS[@]}"; do
  unit="cl_depth_$(basename "$s" .py)"
  systemd-run --user --pipe --wait --collect --unit="$unit" -p MemoryMax=8G \
      -p WorkingDirectory="$WAVE" "$PY" "$s" 2>&1 | tee -a "$WAVE/ledgers/chain.log"
  rc="${PIPESTATUS[0]}"
  echo "[$s] rc=$rc" | tee -a "$WAVE/ledgers/chain.log"
  [ "$rc" -ne 0 ] && { echo "corpus scan failed: $s"; exit 1; }
done

echo "=== build artefacts ==="
for s in "${BUILDS[@]}"; do
  run "$s" || { echo "build failed: $s"; exit 1; }
done

# ---- replay: build again and require byte-identical artefacts -------------------------------
if [ "${1:-}" != "--no-replay" ]; then
  echo "=== replay (second build must be byte-identical) ==="
  cd "$WAVE/out" || exit 2
  sha256sum ONT_CLOSURE_is_a.tsv ONT_LABELMAP_V2.tsv ONT_NAV_v1.json \
            GRANULARITY_FOURWAY_721.tsv GRANULARITY_SUMMARY.json \
            FAMILY_VS_ONTOLOGY_CROSSTAB.tsv CHILD_TERM_CANDIDATES.tsv CHILD_TERM_CANDIDATES.json \
            LINEAGE_NODES.tsv LINEAGE_EDGES.tsv LINEAGE_GERM_LAYER.tsv \
            LINEAGE_MARKER_TRANSITIONS.tsv LINEAGE_UNRESOLVED_DEVELOPMENT.tsv \
            LINEAGE_SUMMARY.json GAPCHECK_LINEAGE_vs_BENCHMARK.tsv \
            > "$WAVE/ledgers/replay_pass1.txt" 2>/dev/null
  cd "$WAVE" || exit 2
  for s in "${BUILDS[@]}"; do
    "$PY" "$s" > /dev/null 2>&1 || { echo "replay build failed: $s"; exit 1; }
  done
  cd "$WAVE/out" || exit 2
  sha256sum ONT_CLOSURE_is_a.tsv ONT_LABELMAP_V2.tsv ONT_NAV_v1.json \
            GRANULARITY_FOURWAY_721.tsv GRANULARITY_SUMMARY.json \
            FAMILY_VS_ONTOLOGY_CROSSTAB.tsv CHILD_TERM_CANDIDATES.tsv CHILD_TERM_CANDIDATES.json \
            LINEAGE_NODES.tsv LINEAGE_EDGES.tsv LINEAGE_GERM_LAYER.tsv \
            LINEAGE_MARKER_TRANSITIONS.tsv LINEAGE_UNRESOLVED_DEVELOPMENT.tsv \
            LINEAGE_SUMMARY.json GAPCHECK_LINEAGE_vs_BENCHMARK.tsv > "$WAVE/ledgers/replay_pass2.txt" 2>/dev/null
  cd "$WAVE" || exit 2
  {
    echo "# replay of ${#BUILDS[@]} builds; artefacts compared: 15"
    if diff -q ledgers/replay_pass1.txt ledgers/replay_pass2.txt > /dev/null; then
      echo "REPLAY_PASS byte-identical on the second build"
    else
      echo "REPLAY_FAIL artefacts differ between builds"
      diff ledgers/replay_pass1.txt ledgers/replay_pass2.txt | head -20
    fi
  } | tee ledgers/REPLAY.txt
fi

# ---- manifest (everything that must not drift; gate outputs and run-time logs excluded) ------
echo "=== manifest ==="
"$PY" - <<'PYEOF' | tee -a ledgers/chain.log
import hashlib, os
WAVE = os.path.abspath(".")
EXCL = {"GATE_A.json", "GATE_B.json", "ONT_SELFTEST.json", "MANIFEST.sha256",
        "REPORT_NUMBER_CHECK.json"}
def sha(p):
    h = hashlib.sha256()
    with open(p, "rb") as f:
        for b in iter(lambda: f.read(1 << 20), b""):
            h.update(b)
    return h.hexdigest()
rows = []
for d in ("out", "scripts"):
    for root, _dirs, files in os.walk(os.path.join(WAVE, d)):
        if "__pycache__" in root:
            continue
        for fn in sorted(files):
            if fn in EXCL or fn.endswith(".pyc"):
                continue
            p = os.path.join(root, fn)
            rows.append((os.path.relpath(p, WAVE), sha(p)))
rows.sort()
with open(os.path.join(WAVE, "out", "MANIFEST.sha256"), "w", encoding="utf-8") as f:
    f.write("# sha256 manifest of this wave's artefacts (gate outputs excluded: they are "
            "written after the manifest)\n")
    for rel, h in rows:
        f.write(f"{h}  {rel}\n")
print(f"manifest entries: {len(rows)}")
PYEOF

# ---- gates ----------------------------------------------------------------------------------
echo "=== report number check ==="
"$PY" scripts/d1_check_report_numbers.py 2>&1 | tee -a ledgers/chain.log
GD="${PIPESTATUS[0]}"

echo "=== gates ==="
"$PY" scripts/gate_ontology_nav.py 2>&1 | tee -a ledgers/chain.log
GA="${PIPESTATUS[0]}"
"$PY" scripts/gate_lineage.py 2>&1 | tee -a ledgers/chain.log
GB="${PIPESTATUS[0]}"

# ---- zero-network reading -------------------------------------------------------------------
EVENTS=$(grep -c '^EVENT' "$CL_DEPTH_NET_AUDIT_LOG" || true)
HOOKS=$(grep -c '^# hook-installed' "$CL_DEPTH_NET_AUDIT_LOG" || true)
echo "[net-audit] hook installs=$HOOKS  network events=$EVENTS" | tee -a ledgers/chain.log
{
  echo "# zero-network audit (audit hook, covers child processes)"
  echo "hook_install_lines=$HOOKS"
  echo "network_event_lines=$EVENTS"
  [ "$EVENTS" = "0" ] && echo "NET_ZERO_PASS" || echo "NET_ZERO_FAIL"
} > ledgers/NET_AUDIT_SUMMARY.txt
cat ledgers/NET_AUDIT_SUMMARY.txt

echo "=== summary: report-number check rc=$GD  gate A rc=$GA  gate B rc=$GB ==="
[ "$GD" = "0" ] && [ "$GA" = "0" ] && [ "$GB" = "0" ] || exit 1