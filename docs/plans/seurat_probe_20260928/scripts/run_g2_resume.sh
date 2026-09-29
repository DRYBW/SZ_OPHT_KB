#!/bin/bash
# G2 chain resume (trackS_DS2 onward)
export PATH=/usr/local/bin:/usr/bin:/bin:/usr/sbin:/sbin
export OMP_NUM_THREADS=16 OPENBLAS_NUM_THREADS=16 MKL_NUM_THREADS=16 NUMBP=16
W=<EYEKB>/plans/seurat_probe_20260928
E=<CONDA_ROOT>/envs/r_seurat_probe
PY=<TRAINING_VENV>/bin/python3
LOGD=$W/logs
step () {
  NAME=$1; shift
  echo "STEP $NAME start $(date -Is)" >> $LOGD/G2_chain.log
  /usr/bin/time -v "$@" > $LOGD/G2_${NAME}.out 2> $LOGD/G2_${NAME}.time
  RC=$?
  RSS=$(grep "Maximum resident set size" $LOGD/G2_${NAME}.time | awk -F: '{print $2}' | tr -d ' ')
  AVAIL=$(free -g | awk 'NR==2{print $7}')
  echo "STEP $NAME rc=$RC rss_kb=$RSS free_available_gb=$AVAIL end=$(date -Is)" >> $LOGD/G2_chain.log
  if [ $RC -ne 0 ]; then echo "CHAIN_FAIL $NAME" >> $LOGD/G2_chain.log; return 1; fi
}
cd $W
step trackS_DS2   $E/lib/R/bin/Rscript scripts/g2_seurat_singler.R DS2 || exit 1
step trackP_DS1   $PY scripts/trackP_scanpy.py DS1 || exit 1
step trackS_DS1   $E/lib/R/bin/Rscript scripts/g2_seurat_singler.R DS1 || exit 1
step metrics      $PY scripts/three_numbers.py || exit 1
echo "CHAIN_DONE $(date -Is)" >> $LOGD/G2_chain.log
