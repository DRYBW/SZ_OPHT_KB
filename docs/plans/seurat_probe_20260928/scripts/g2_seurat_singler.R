#!/usr/bin/env Rscript
# G2 track S: Seurat chain + SingleR (self-built cross reference) for one dataset.
# usage: Rscript g2_seurat_singler.R <DS1|DS2>
suppressPackageStartupMessages(library(Seurat))
suppressPackageStartupMessages(library(SingleR))
suppressPackageStartupMessages(library(Matrix))
W <- "<EYEKB>/plans/seurat_probe_20260928"
tag <- commandArgs(trailingOnly=TRUE)[1]
t0 <- proc.time()
mark <- function(m) cat(sprintf("[%s] %.1fs\n", m, (proc.time()-t0)[["elapsed"]]), file=stderr())

load_ds <- function(base, mapfile=NULL) {
  m <- as(readMM(paste0(base,"_counts.mtx")), "CsparseMatrix")
  g <- scan(paste0(base,"_features.tsv"), what="character", quiet=TRUE)
  b <- scan(paste0(base,"_barcodes.tsv"), what="character", quiet=TRUE)
  rownames(m) <- g; colnames(m) <- b
  tr <- read.delim(paste0(base,"_truth.tsv"), stringsAsFactors=FALSE)
  list(counts=m, truth=tr$truth[match(b, tr$barcode)])
}
MAP2 <- c("retinal rod cell type A"="Rod","retinal rod cell type B"="Rod","retinal rod cell type C"="Rod",
 "retinal cone cell"="Cone","retinal bipolar neuron type A"="BC","retinal bipolar neuron type B"="BC",
 "retinal bipolar neuron type C"="BC","retinal bipolar neuron type D"="BC","amacrine cell"="AC",
 "retinal ganglion cell"="RGC","Muller cell"="MG","microglial cell"="Micro",
 "unannotated"=NA,"unspecified"=NA)

D  <- load_ds(file.path(W, paste0("data/", tag)))
DR <- load_ds(file.path(W, paste0("data/", if (tag=="DS1") "DS2" else "DS1")))
truth <- D$truth
if (tag=="DS2") truth <- unname(MAP2[truth])   # NA for EXCL
ref_tag <- if (tag=="DS1") "DS2" else "DS1"
ref_lab <- DR$truth
if (ref_tag=="DS2") { ref_lab <- MAP2[ref_lab]; keep <- !is.na(ref_lab) } else { keep <- rep(TRUE, length(ref_lab)) }
ref_lab <- unname(ref_lab[keep]); DR$counts <- DR$counts[, keep, drop=FALSE]
mark("loaded")

obj <- CreateSeuratObject(D$counts)
obj <- NormalizeData(obj, normalization.method="LogNormalize", scale.factor=1e4, verbose=FALSE); mark("NormalizeData")
obj <- FindVariableFeatures(obj, selection.method="vst", nfeatures=2000, verbose=FALSE); mark("HVG")
if (ncol(obj) > 50000) { obj <- subset(obj, features=VariableFeatures(obj)); invisible(gc()); mark("feature-subset") }
obj <- ScaleData(obj, verbose=FALSE); mark("ScaleData")
obj <- RunPCA(obj, npcs=50, verbose=FALSE); mark("PCA")
obj <- FindNeighbors(obj, k.param=20, verbose=FALSE); mark("Neighbors")
obj <- FindClusters(obj, resolution=1.0, algorithm=1, verbose=FALSE); mark("Louvain")

# SingleR on cluster-level, reference = other dataset raw counts
cl <- as.character(obj$seurat_clusters)
hv <- intersect(VariableFeatures(obj), gsub("_","-",rownames(DR$counts)))
feats <- head(hv, 3000)
test <- LayerData(obj, layer="data", features=feats, verbose=FALSE)
refc <- DR$counts[feats, , drop=FALSE]; rownames(refc) <- feats
labs_u <- sort(unique(ref_lab))
agg <- sapply(labs_u, function(L) Matrix::rowMeans(refc[, ref_lab==L, drop=FALSE]))
dimnames(agg) <- list(feats, labs_u)
pred <- SingleR(test=test, ref=as(agg,"CsparseMatrix"), labels=colnames(agg), cluster=cl)
mark("SingleR")
out <- data.frame(barcode=colnames(obj), louvain=cl, truth=ifelse(is.na(truth),"EXCL",truth),
                  S_call=as.character(pred$labels[match(cl, rownames(pred))]))
write.csv(out, file.path(W, paste0("tables/trackS_", tag, "_celllabels.csv")), row.names=FALSE)
cs <- as.data.frame(table(out$louvain, out$S_call))
write.csv(cs, file.path(W, paste0("tables/trackS_", tag, "_cluster_call.csv")), row.names=FALSE)
saveRDS(obj, file.path(W, paste0("data/G2_", tag, ".rds")))
cat("G2_S_DONE", tag, "n_clusters=", length(levels(as.factor(cl))), "\n")
