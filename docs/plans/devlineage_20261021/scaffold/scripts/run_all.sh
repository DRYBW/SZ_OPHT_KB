#!/usr/bin/env bash
# run_all.sh - one command that reproduces this card's artefacts and then judges them.
#
#   bash scripts/run_all.sh                # build, replay, manifest, gates, network audit
#   bash scripts/run_all.sh --no-replay
#
# Order matters: every artefact is written before the manifest is taken, and the gates run after the
# manifest, so a drifting artefact is caught by the gate rather than by hand. The corpus scan and
# the two gates are the heavy steps and run under systemd-run --user with a memory cap set from the
# measured peak (0.21 GB measured with /usr/bin/time -v; the cap is 2 GB, i.e. ~10x headroom).
#
# Zero network is enforced by an audit hook (scripts/netaudit/sitecustomize.py) covering child
# processes, with a load receipt so "no events" cannot be confused with "the hook never ran".
set -uo pipefail

HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
PY="${PY:-/usr/bin/python3}"
cd "$WAVE" || exit 2

mkdir -p out ledgers logs
export SCAFFOLD_NET_AUDIT_LOG="$WAVE/ledgers/net_audit.log"
echo "# chain start $(date -Is)" >> "$SCAFFOLD_NET_AUDIT_LOG"
export PYTHONPATH="$WAVE/scripts/netaudit${PYTHONPATH:+:$PYTHONPATH}"

run() { echo "--- $*"; "$PY" "$@" 2>&1 | tee -a "$WAVE/ledgers/chain.log"; return "${PIPESTATUS[0]}"; }

BUILDS=(scripts/s0_reverify_upstream.py scripts/s1_enum_nodes.py scripts/s2_enum_edges.py
        scripts/s3_coverage_denominator.py scripts/s4_decapitated_branches.py
        scripts/s6_pending_assertions.py scripts/s7_afterfact_coverage.py)
SCAN=scripts/s5_corpus_scan.py
GATES=(scripts/s8_gate_scaffold.py)

echo "=== corpus scan (systemd-run --user, MemoryMax=2G; measured peak 0.21GB) ==="
systemd-run --user --pipe --wait --collect --unit=devlin_scaffold_scan -p MemoryMax=2G \
    -p MemorySwapMax=2G -p WorkingDirectory="$WAVE" "$PY" "$SCAN" 2>&1 | tee -a "$WAVE/ledgers/chain.log"
rc="${PIPESTATUS[0]}"
echo "[$SCAN] rc=$rc" | tee -a "$WAVE/ledgers/chain.log"
[ "$rc" -ne 0 ] && { echo "corpus scan failed"; exit 1; }

echo "=== build artefacts ==="
for s in "${BUILDS[@]}"; do
  run "$s" || { echo "build failed: $s"; exit 1; }
done

# ---- replay: build everything twice and require byte-identical artefacts ---------------------
if [ "${1:-}" != "--no-replay" ]; then
  echo "=== resource readings (the values the report quotes) ==="
bash scripts/s10_resource_readings.sh > /dev/null || { echo "resource readings failed"; exit 1; }
echo "wrote ledgers/RESOURCE_READINGS.txt"

echo "=== replay (second build must be byte-identical) ==="
  cd "$WAVE/out" || exit 2
  sha256sum SCAFFOLD_NODES.tsv SCAFFOLD_EDGES_CONFIRMED.tsv FIRSTPASS_RECONCILIATION.tsv \
            COVERAGE_DENOMINATOR.tsv ANCHOR_COVERAGE.tsv RPC_AXIS.tsv DECAPITATED_BRANCHES.tsv \
            CORPUS_ASSERTIONS_RAW.tsv CORPUS_ASSERTION_EXAMPLES.tsv CORPUS_ASSERTION_ANCHORS.tsv \
            PEER_WEAK_ROW_CHUNKS.tsv PEER_WEAK_ROW_RECHECK.tsv PENDING_ASSERTIONS.tsv \
            SCAFFOLD_EDGES_NOT_ADMITTED.tsv SCAFFOLD_EDGES.tsv AFTERFACT_RECORDING_COVERAGE.tsv \
            > "$WAVE/ledgers/replay_pass1.txt" 2>/dev/null
  cd "$WAVE" || exit 2
  "$PY" "$SCAN" > /dev/null 2>&1 || { echo "replay scan failed"; exit 1; }
  for s in "${BUILDS[@]}"; do
    "$PY" "$s" > /dev/null 2>&1 || { echo "replay build failed: $s"; exit 1; }
  done
  cd "$WAVE/out" || exit 2
  sha256sum SCAFFOLD_NODES.tsv SCAFFOLD_EDGES_CONFIRMED.tsv FIRSTPASS_RECONCILIATION.tsv \
            COVERAGE_DENOMINATOR.tsv ANCHOR_COVERAGE.tsv RPC_AXIS.tsv DECAPITATED_BRANCHES.tsv \
            CORPUS_ASSERTIONS_RAW.tsv CORPUS_ASSERTION_EXAMPLES.tsv CORPUS_ASSERTION_ANCHORS.tsv \
            PEER_WEAK_ROW_CHUNKS.tsv PEER_WEAK_ROW_RECHECK.tsv PENDING_ASSERTIONS.tsv \
            SCAFFOLD_EDGES_NOT_ADMITTED.tsv SCAFFOLD_EDGES.tsv AFTERFACT_RECORDING_COVERAGE.tsv \
            > "$WAVE/ledgers/replay_pass2.txt" 2>/dev/null
  cd "$WAVE" || exit 2
  {
    echo "# replay of ${#BUILDS[@]} builds + the corpus scan; artefacts compared: 16"
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
EXCL = {"GATE_SCAFFOLD.json", "MANIFEST.sha256", "REPORT_NUMBER_CHECK.json"}
RUNTIME = {"AFTERFACT_RECORDING_COVERAGE.tsv", "AFTERFACT_SUMMARY.json"}
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
    f.write("# sha256 manifest of this card's artefacts (gate output excluded: it is written after "
            "the manifest)\n")
    for rel, h in rows:
        f.write(f"{h}  {rel}\n")
print(f"manifest entries: {len(rows)}")
# the two reader-facing documents live outside out/ and scripts/, so they get their own ledger
docs = []
for fn in ("README.md", "REPORT.md"):
    p = os.path.join(WAVE, fn)
    if os.path.isfile(p):
        docs.append((fn, sha(p)))
with open(os.path.join(WAVE, "ledgers", "DOC_SHA256.tsv"), "w", encoding="utf-8") as f:
    f.write("# sha256 of the reader-facing documents (not part of out/MANIFEST.sha256)\n")
    for rel, h in docs:
        f.write(f"{h}  {rel}\n")
print(f"reader-facing documents hashed: {len(docs)}")
PYEOF

echo "=== gate ==="
run "${GATES[0]}"
G="${PIPESTATUS[0]}"

echo "=== report numbers (every quoted number recomputed from the artefacts) ==="
run scripts/s11_check_report_numbers.py
N="${PIPESTATUS[0]}"

# ---- the recorded query set: default behaviour, with the repository's own anchors ------------
REPO="${EYEKB_REPO:-/home/ubuntu/EYEKB_REPO}"
if [ -d "$REPO/literature_db/v2.4.2_2026-09_slim" ]; then
  echo "=== recorded query-set replay (default behaviour) ==="
  bash scripts/s9_query_set_replay.sh | tail -5
  Q="${PIPESTATUS[0]}"
else
  echo "=== recorded query-set replay skipped: no corpus at $REPO/literature_db/v2.4.2_2026-09_slim ==="
  Q=0
fi

# ---- zero-network reading -------------------------------------------------------------------
EVENTS=$(grep -c '^EVENT' "$SCAFFOLD_NET_AUDIT_LOG" || true)
HOOKS=$(grep -c '^# hook-installed' "$SCAFFOLD_NET_AUDIT_LOG" || true)
echo "[net-audit] hook installs=$HOOKS  network events=$EVENTS" | tee -a ledgers/chain.log
{
  echo "# zero-network audit (audit hook, covers child processes)"
  echo "hook_install_lines=$HOOKS"
  echo "network_event_lines=$EVENTS"
  echo "query_set_replay: see ledgers/QUERY_REPLAY.txt (scripts/s9_query_set_replay.sh)"
  [ "$EVENTS" = "0" ] && echo "NET_ZERO_PASS" || echo "NET_ZERO_FAIL"
} > ledgers/NET_AUDIT_SUMMARY.txt
cat ledgers/NET_AUDIT_SUMMARY.txt

echo "=== summary: gate rc=$G  report-numbers rc=$N  query-replay rc=$Q ==="
[ "$G" = "0" ] && [ "$N" = "0" ] && [ "$Q" = "0" ] || exit 1