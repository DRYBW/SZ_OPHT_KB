# G1 试点门（预注册判据实测，2026-09-28）

- 试点集：DS1（shekhar human retina）随机 20,000 细胞子集（seed=20260928，scripts/export_ds1_sub.py），counts=原始整数矩阵，60,671 基因
- 链：CreateSeuratObject → LogNormalize → HVG vst 2000 → ScaleData(仅 HVG) → PCA 50 → FindNeighbors k=20 → FindClusters Louvain res=1.0（Seurat 5.5.1，algorithm=1=Louvain）
- 托管：systemd-run --user -p MemoryMax=24G -p MemorySwapMax=2G；/usr/bin/time -v 实测
- 并发治理：R 首跑 OpenBLAS 自动 128 线程（4min 烧 7h46 CPU）——终止重跑并限 OMP/OPENBLAS/MKL/NUMBP=16，以下为限线程后的正式读数

## 门判据 vs 实测

| 判据 | 门限 | 实测 | 判定 |
|------|------|------|------|
| 峰值 RSS | ≤ 20 GB | **3.31 GiB**（3,469,808 KB） | ✓ |
| 端到端 wall | ≤ 15 min | **1 min 04 s** | ✓ |
| 退出码 | 0 | 0（20 簇，min2711/max40） | ✓ |

→ **G1 GO**，放行 G2 全量三数字（DS1 180,093 + DS2 19,694）。

证据：logs/G1_time.txt、logs/G1_run.txt、logs/G1_metrics.txt、data/G1_DS1sub20k_seurat.rds（161MB）、tables/G1_cluster_vs_truth.csv
