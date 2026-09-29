# G0 装机台账（SEURATPROBE t_5d18900e，2026-09-28 实测）

- env 名：`r_seurat_probe`，路径 `<CONDA_ROOT>/envs/r_seurat_probe`（conda envs_dirs 首选 .conda/envs）
- 不碰系统 R（/usr/bin/R 未动），未装入任何既有 env ✓
- 求解：conda 26.5.3 classic solver，channel_alias=清华 TUNA（.condarc: conda-forge+bioconda, channel_priority=flexible）

## 包版本（Rscript 实测加载）
- R version 4.5.3（r-base conda-forge）
- Seurat 5.5.1
- SingleR 2.12.0（bioconductor-singler；注：conda 包名非 r-singler，首求解 PackagesNotFoundInChannelsError 后改名重试）

## 下载体积（>1GB 停卡报批门实测）
- 方法：`conda create --download-only` + pkgs 缓存顶层归档文件（.conda/.tar.bz2/.partial）按 marker 时间戳增量求和，每 30s 看门狗（scripts/g0_download_watch.sh，>1100MB 自动 kill 停卡）
- 实测包归档下载增量 = **301 MB**（logs/g0_state.txt: `conda_rc=0 final_archive_increment_mb=301 abort=0`）
- 门判定：301MB ≤ 1GB → **G0 PASS，未触发报批**
- 另计：repodata 元数据两次拉取（current_repodata 失败→全量 repodata.json，conda-forge+bioconda，~百 MB 级，缓存于 pkgs/cache/*.json，非 R 包本体；PI 门针对"R 包下载"，如实单列此读数）

## link 阶段异常留痕
- `conda create`（link）阶段报 SafetyError（r-base packages.html "incorrect size" 3423 vs 77941）——TUNA 镜像解包一致性误报；transaction 仍 Executing...done，R 4.5.3+Seurat+SingleR `library()` 加载实测通过 → 判定装机可用，留痕备查。

## 补装（SingleR 2.12 运行期依赖，同门计数）
- `bioconductor-scrapper` 1.4.0（+rigraphlib/biocmake/dir.expiry 等）：conda install --solver=libmamba，实测增量 4.4MB（pkgs marker find 实测）
- G0 累计包归档下载 = **305.4 MB ≤ 1GB** ✓ 未触发报批
