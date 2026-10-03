# pipeline/fixtures — fixed inputs for G4 verification
pdr600.h5ad: 600 cells x 23,441 genes of integer raw counts; obs carries only the sample column (RRx public sample names).
Source: a sampled subset of the public matrix of GEO series GSE165784 (human PDR / vitreous membrane scRNA); no patient fields of any kind.
This file was curated by the manuscript team; its only purpose is pipeline determinism and reproduction verification (tests/verify_pipeline.py) — it is not a biological reference.
sha256 = fa8fc609c3920dd2506a7b81fafe5a6e363b98eb670ee523a3f411d5c913ce44
