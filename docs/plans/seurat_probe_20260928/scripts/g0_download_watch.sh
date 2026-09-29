#!/bin/bash
# G0: conda download-only for r_seurat_probe, watchdog aborts if downloaded archives > 1100MB.
export PATH=/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin
set -u
CONDA=<MINICONDA>/bin/conda
PKGS=<MINICONDA>/pkgs
W=<EYEKB>/plans/seurat_probe_20260928
LOG=$W/logs/g0_download.log
STATE=$W/logs/g0_state.txt
MARK=/tmp/g0_pkgs_marker
KILL_MB=1100

new_archives_mb() {
  find "$PKGS" -maxdepth 1 -type f -newer "$MARK" \( -name '*.conda' -o -name '*.tar.bz2' -o -name '*.partial' \) -printf '%s\n' 2>/dev/null | awk '{s+=$1} END {printf "%d", s/1048576}'
}

echo "start $(date -Is)" > "$STATE"
touch "$MARK"

$CONDA create -y -n r_seurat_probe --download-only \
  -c conda-forge -c bioconda r-base r-seurat bioconductor-singler > "$LOG" 2>&1 &
DL=$!

ABORT=0
while kill -0 $DL 2>/dev/null; do
  sleep 30
  INC=$(new_archives_mb)
  echo "$(date -Is) increment_mb=$INC" >> "$STATE"
  if [ "${INC:-0}" -gt "$KILL_MB" ]; then
    echo "$(date -Is) OVER-limit abort at increment_mb=$INC" >> "$STATE"
    kill $DL 2>/dev/null; sleep 3; kill -9 $DL 2>/dev/null
    pkill -f "conda create -y -n r_seurat_probe" 2>/dev/null
    ABORT=1
    break
  fi
done
wait $DL 2>/dev/null
RC=$?
FINAL=$(new_archives_mb)
echo "conda_rc=$RC final_archive_increment_mb=$FINAL abort=$ABORT end=$(date -Is)" >> "$STATE"
echo "G0_DONE rc=$RC" >> "$STATE"
