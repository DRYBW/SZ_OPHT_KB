#!/usr/bin/env Rscript
# G1 pilot: Seurat standard chain on DS1sub20k counts.
# chain = log-normalize + HVG2000 + ScaleData(HVG) + PCA(50) + FindNeighbors(k=20) + FindClusters(louvain, res=1.0)
# Prints step timings; peak RSS is measured externally by /usr/bin/time -v.
suppressPackageStartupMessages(library(Seurat))
W <- "<EYEKB>/plans/seurat_probe_20260928"
t0 <- proc.time()
mark <- function(m) cat(sprintf("[%s] %.1fs elapsed\n", m, (proc.time()-t0)[["elapsed"]]), file=stderr())

mtx <- Matrix::readMM(file.path(W,"data/DS1sub20k_counts.mtx"))
genes <- scan(file.path(W,"data/DS1sub20k_features.tsv"), what="character", quiet=TRUE)
bc    <- scan(file.path(W,"data/DS1sub20k_barcodes.tsv"), what="character", quiet=TRUE)
rownames(mtx) <- genes; colnames(mtx) <- bc
mark("readMM")

obj <- CreateSeuratObject(mtx, project="DS1sub20k")
mark("CreateSeuratObject")
obj <- NormalizeData(obj, normalization.method="LogNormalize", scale.factor=1e4, verbose=FALSE)
mark("NormalizeData")
obj <- FindVariableFeatures(obj, selection.method="vst", nfeatures=2000, verbose=FALSE)
mark("FindVariableFeatures")
obj <- ScaleData(obj, features=VariableFeatures(obj), verbose=FALSE)
mark("ScaleData")
obj <- RunPCA(obj, npcs=50, verbose=FALSE)
mark("RunPCA")
obj <- FindNeighbors(obj, k.param=20, verbose=FALSE)
mark("FindNeighbors")
obj <- FindClusters(obj, resolution=1.0, algorithm=1, verbose=FALSE)
mark("FindClusters-louvain-res1.0")

truth <- read.delim(file.path(W,"data/DS1sub20k_truth.tsv"))
tab <- table(obj$seurat_clusters, truth$truth[match(colnames(obj), truth$barcode)])
write.csv(as.matrix(tab), file.path(W,"tables/G1_cluster_vs_truth.csv"))
cat("n_clusters:", nlevels(obj$seurat_clusters), "\n")
print(table(obj$seurat_clusters))
obj <- saveRDS(obj, file.path(W,"data/G1_DS1sub20k_seurat.rds"))
mark("saveRDS")
cat("G1_CHAIN_OK\n")
