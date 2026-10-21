#!/usr/bin/env bash
# s10_resource_readings.sh - the resource/perf readings this card's report quotes, captured by
# running the commands rather than by remembering them. Output: ledgers/RESOURCE_READINGS.txt
set -uo pipefail
HERE="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
WAVE="$(cd "$HERE/.." && pwd)"
OUT="$WAVE/ledgers/RESOURCE_READINGS.txt"
{
  echo "# resource and performance readings, captured $(date -Is)"
  echo
  echo "## \$ free -g          # before the corpus scan"
  free -g
  echo
  echo "## \$ du -sh of the corpus and of the ontology file"
  du -sh /mnt/D/OcularKB/ocularkb/rag/literature_db/v2.6-dev_2026-10
  du -sh /mnt/D/EyeKB/plans/devline_ont_20261002/downloads/cl.obo
  echo
  echo "## \$ /usr/bin/time -v on the corpus scan (single process, no concurrency)"
  grep -E "Maximum resident set size|Elapsed \(wall clock\)|Exit status|Percent of CPU" \
      "$WAVE/logs/s5_corpus_scan.time"
  echo
  echo "## corpus rows read by the scan (from out/CORPUS_SCAN_META.json)"
  /usr/bin/python3 -c "
import json;m=json.load(open('$WAVE/out/CORPUS_SCAN_META.json'))
print({k:m[k] for k in ('chunks_in_corpus','chunks_carrying_a_lineage_verb','sentences_examined','sentences_with_two_or_more_phrases','ordered_pairs_found','examples_recorded','examples_verified','examples_failed_verification')})"
  echo
  echo "## \$ nvidia-smi --query-gpu=... (this card uses no GPU)"
  nvidia-smi --query-gpu=name,utilization.gpu,memory.used,memory.total,temperature.gpu \
      --format=csv,noheader 2>/dev/null || echo "nvidia-smi unavailable"
  echo
  echo "## \$ free -g          # after the whole chain"
  free -g
  echo
  echo "## \$ wc -l on the delivered node/edge tables"
  wc -l "$WAVE/out/SCAFFOLD_NODES.tsv" "$WAVE/out/SCAFFOLD_EDGES.tsv" \
        "$WAVE/out/SCAFFOLD_EDGES_CONFIRMED.tsv" "$WAVE/out/DECAPITATED_BRANCHES.tsv" \
        "$WAVE/out/PENDING_ASSERTIONS.tsv"
  echo
  echo "## \$ sha256sum of the delivered tables (the values the report quotes)"
  (cd "$WAVE" && sha256sum out/SCAFFOLD_NODES.tsv out/SCAFFOLD_EDGES_CONFIRMED.tsv \
      out/SCAFFOLD_EDGES.tsv out/DECAPITATED_BRANCHES.tsv out/PENDING_ASSERTIONS.tsv \
      out/COVERAGE_DENOMINATOR.tsv out/GATE_SCAFFOLD.json)
} > "$OUT"
cat "$OUT"