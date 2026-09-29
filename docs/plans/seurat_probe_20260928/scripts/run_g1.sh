#!/bin/bash
# G1 pilot runner: systemd-run --user MemoryMax=24G, measure RSS + wall time with /usr/bin/time -v
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
W=<EYEKB>/plans/seurat_probe_20260928
R=$W/data
E=<CONDA_ROOT>/envs/r_seurat_probe
OUT=$W/logs/G1_run.txt
ERR=$W/logs/G1_time.txt

# build subset data dir
mkdir -p $R
cd $W
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16 NUMBP=16
/usr/bin/time -v "$E/lib/R/bin/Rscript" scripts/g1_seurat_pilot.R > "$OUT" 2> "$ERR"
RC=$?
echo "exit_code=$RC" >> "$ERR"
grep -E "Maximum resident set size|Elapsed \(wall" "$ERR" >> $W/logs/G1_metrics.txt
echo "G1 finished rc=$RC $(date -Is)" >> $W/logs/G1_metrics.txt
