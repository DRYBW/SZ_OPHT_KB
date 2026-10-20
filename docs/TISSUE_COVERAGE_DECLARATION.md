# Tissue coverage declaration

Owner: the PI of this project. Declared: 2026-10-20.
Applies to: the marker knowledge base shipped in `kb/markers/` (production `all` route).

## What this document is

A declaration of which ocular tissues this knowledge base **claims** annotated coverage for, and
which tissues are **declared gaps** where no such claim is made. It exists so that a low score on a
declared-gap tissue is read as a known limitation of coverage, not as a defect of the caller's data
and not as a model that silently underperforms.

"Claims coverage" here means: the class vocabulary contains the cell types an author of that tissue
would normally use, and a gene panel typical of that tissue resolves to them. It is not a claim of
clinical accuracy for any single cluster.

## Basis of the declaration

Measured on the shipped default route over 28 author-annotated volumes / 721 clusters / 1,495,330
cells, judging by exact Cell Ontology term with coarser/finer answers reported separately. Figures
are cells weighted, per tissue. The three posterior rows were re-measured after the 2026-10-20
anterior-segment activation and are unchanged by it.

| tissue | exact CL | we answered finer | we answered coarser | KB lacks the author's class | wrong class | abstained |
|---|---|---|---|---|---|---|
| retina | 37.81 | 27.65 | 2.08 | 2.90 | 12.19 | 17.37 |
| rpe / choroid | 24.53 | 28.55 | 2.53 | 1.10 | 25.04 | 18.26 |
| optic nerve | 21.79 | 27.78 | 0.00 | 8.79 | 13.39 | 28.26 |
| ocular surface / cornea | 50.74 | — | — | — | 14.43 | — |
| trabecular meshwork | 61.09 | — | — | — | 11.09 | — |
| ciliary body | 80.88 | — | — | — | 5.85 | — |
| **lens** | **5.36** | **0.00** | **0.00** | **21.89** | **16.90** | **55.85** |
| **iris** | **18.65** | **2.08** | **0.00** | **13.44** | **21.63** | **44.21** |

## Covered: no limitation declared

`retina`, `rpe`, `optic nerve`, `ocular surface`, `trabecular meshwork`, `ciliary body`.

Two notes that belong with these numbers rather than in a footnote:

* For retina, RPE and optic nerve the single largest non-matching block is **the knowledge base
  answering a more specific term than the author used** (27–29% of cells). Those answers are not
  counted as correct here, because only an exact term match is; they are also not counted as wrong.
  Do not read 37.81% on retina as "the remaining 62% is wrong".
* RPE (25.04%) and iris (21.63%) carry the largest genuine mis-assignment rates in the corpus. For
  RPE this is recorded as an open problem, not a declared gap.

## Declared gap: lens

No annotated coverage is claimed for lens tissue.

* Only **5.36%** of lens cells resolve to the exact author term; **55.85%** abstain.
* The dominant author classes are not in the vocabulary in a matching form: `anterior lens cell`
  (CL:0002223) covers 54.3% of the tissue and `secondary lens fiber` (CL:0002225) a further 10.1%.
  The knowledge base carries `lens epithelial cell` (CL:0002224) and `lens fiber cell`
  (CL:0011004), which are different branches of the ontology for these volumes.
* A measured mis-assignment that is not a granularity artefact: lens epithelial and anterior lens
  cells are returned as **amacrine cell** (CL:0000561) for 5,252 cells in one volume, because the
  panels share genes with the retinal amacrine panel.

Consequence: a lens volume processed through the default route will return a mixture of abstentions
and retinal identities. Callers should treat lens output as unsupported and must not publish it as
an annotation result.

## Declared gap: iris

No annotated coverage is claimed for iris tissue.

* Only **18.65%** of iris cells resolve to the exact author term; **44.21%** abstain.
* The dominant author class `pigmented epithelial cell` (CL:0000529) covers **43.7%** of the tissue
  and has no counterpart in the vocabulary; the base carries `iris pigment epithelial cell`
  (CL:0002565), a different branch. Of those cells, 16,971 abstain and 7,524 are returned as
  `SMC` (CL:0000192).
* Other measured mis-assignments in the same volume: iris fibroblast returned as `trabecular
  meshwork cell` (7,817 cells) and as `pDC` (CL:0000784, 3,703 cells).
* The iris pigment panel (24 genes) contributes a single shared gene to a typical 10-gene query,
  which the >= 2 shared-gene admission rule refuses to act on. The refusal is correct behaviour; the
  panel is too thin to produce an answer.

Consequence: same as lens. Iris output is unsupported and must not be published as an annotation
result.

## How a caller should use this

1. Route on the tissue the volume declares. For `lens` and `iris`, treat the result as
   `unsupported_tissue` rather than as an annotation.
2. Do not tune thresholds to make lens or iris look better; that converts a declared gap into a
   silent overcall.
3. Improving either tissue requires new class definitions and thicker panels, which is a separate,
   registered change. Until that lands, this declaration stands.
