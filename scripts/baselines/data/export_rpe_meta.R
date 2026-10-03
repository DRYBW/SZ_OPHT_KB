#!/usr/bin/env Rscript
# KB1v2b RPE backfill: export GSE158629 RData -> cell-level metadata + cluster marker tables (v2 sparse crossprod)
load("/mnt/D/OcularKB/data/GSE158629/extracted/RPE_donors1-4.RData")
suppressMessages(library(Matrix))
outdir <- "/home/ubuntu/.hermes/kanban/boards/pi-briefing/workspaces/t_16c3e020"
objs <- c("donor1.10x", "donor2.ICELL8", "donor3.ICELL8", "donor4.ICELL8")

cells_all <- list()
mk_all <- list()
for (o in objs) {
  x <- get(o)
  donor <- sub("\\..*$", "", o)
  tech <- unique(as.character(x@meta.data$tech))
  cl <- as.character(x@active.ident)
  cells_all[[o]] <- data.frame(
    donor = donor, tech = tech, object = o,
    barcode = rownames(x@meta.data), cluster = cl,
    nCount_RNA = x@meta.data$nCount_RNA, nFeature_RNA = x@meta.data$nFeature_RNA,
    percent.mt = x@meta.data$percent.mt, stringsAsFactors = FALSE)
  dat <- x@assays$RNA@data
  grp <- factor(cl)
  G <- sparseMatrix(i = seq_along(cl), j = as.integer(grp), x = 1,
                    dims = c(length(cl), nlevels(grp)))
  nper <- as.numeric(table(grp))
  mn <- as.matrix(dat %*% G); detm <- as.matrix((dat > 0) %*% G)
  colnames(mn) <- colnames(detm) <- levels(grp)
  gn <- rownames(dat); if (is.null(gn)) gn <- rownames(x@assays$RNA@counts)
  if (!is.null(gn) && nrow(mn)==length(gn)) rownames(mn) <- rownames(detm) <- gn
  mn <- sweep(mn, 2, nper, "/"); detm <- sweep(detm, 2, nper, "/")
  for (g in colnames(mn)) {
    rest <- rowMeans(mn[, colnames(mn) != g, drop = FALSE])
    score <- mn[, g] - rest
    score[detm[, g] < 0.5] <- -Inf   # require >=50% expressing cells within the cluster
    top <- head(order(score, decreasing = TRUE), 25)
    mk_all[[paste0(o, "_", g)]] <- data.frame(
      donor = donor, tech = tech, object = o, cluster = g,
      n_cells = as.numeric(nper[g]),
      gene = rownames(mn)[top],
      mean_logexpr = round(mn[top, g], 3),
      delta_vs_rest = round(score[top], 3),
      pct_expressing = round(100 * detm[top, g], 1),
      rank = seq_along(top), stringsAsFactors = FALSE)
  }
  cat(o, "done:", length(cl), "cells,", nlevels(grp), "clusters\n")
}
write.csv(do.call(rbind, cells_all), file.path(outdir, "rpe_GSE158629_cells_meta.csv"), row.names = FALSE)
write.csv(do.call(rbind, mk_all), file.path(outdir, "rpe_GSE158629_cluster_markers.csv"), row.names = FALSE)
cat("total cells:", sum(sapply(cells_all, nrow)), " marker rows:", sum(sapply(mk_all, nrow)), "\n")
