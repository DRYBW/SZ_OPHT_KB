---
title: Cell-Ontology child terms adopted for finer-grained naming
created: 2026-10-25
updated: 2026-10-25
type: reference
tags: [ontology, naming, markers, retina, ocular-surface, cell-ontology]
sources: [kb/ontology/cl/releases/2026-06-08/cl-base.obo, literature_db v2.4.2_2026-09]
confidence: high
---

# Cell-Ontology child terms (finer names for clusters the dictionary names coarsely)

The shipped marker dictionary names a cell type at one granularity (`BC`, `Cone`, `Fibroblast`).
Where a recorded public cluster's **own reference label is a finer Cell-Ontology term**, an answer
built from the dictionary can only ever be the coarser name: the finer name does not exist in the
dictionary, so the gap is a **naming** gap and not a recognition failure. This page documents the
child terms that were adopted into the naming layer, together with the registered, default-off
marker increment that can answer with them (`library = cl56_v15`).

Registration status: the increment is **registered and default-off** — its whitelist is empty by
design, so it is not part of the default `all` route in any state and a default-route answer never
carries one of these names. The names are reachable by name through an explicit route, and each one
is a row in the link registry (`kb/link_registry/LINK_REGISTRY_v1.jsonl`), which is where the papers
behind it are listed (reader-facing twin: the annotation evidence appendix).

## The adopted terms

| our class | adopted child term | Cell-Ontology id | `is_a` path (frozen snapshot) | panel genes | recorded clusters labelled with the term | cells |
|---|---|---|---:|---:|---:|
| `BC` | rod bipolar cell | CL:0000751 | CL:0000751 → CL:0000749 → CL:0000748 | 44 | 8 | 23,484 |
| `Fibroblast` | keratocyte | CL:0002363 | CL:0002363 → CL:0000005 → CL:0000057 | 60 | 3 | 11,836 |
| `Cone` | S cone cell | CL:0003050 | CL:0003050 → CL:0000573 | 22 | 3 | 3,685 |

Each term resolves in the frozen snapshot shipped with this knowledge base
(`kb/ontology/cl/releases/2026-06-08/cl-base.obo`) and is a **strict `is_a` descendant** of the term
our class already carries.

## How a term was admitted

Three conditions, fixed before the list was computed:

1. **ontology** — the child term resolves in the frozen snapshot and is a strict `is_a` descendant
   of our class's term;
2. **naming support** — the held in-repo corpus states the term (25 of the candidate pairs; the 31
   pairs the corpus never states stay out — importing a name the literature never applies to those
   cells would be a vocabulary import with no local evidence);
3. **floor** — at least one recorded cluster whose reference label is literally the term; at least
   two discriminating positive genes in the assay vocabulary; and at least two of those genes
   observable in a demand cluster's recorded top-window.

Twenty-two corpus-supported pairs failed condition 3 and are listed with their reason rather than
adopted: for eighteen of them the corpus states the term but never attaches a marker to it, so there
is no panel to build.

## What each entry carries

Each entry carries **only that pair's discriminating positive genes**, with parent-shared genes
removed, so a child entry cannot re-state the parent's identity genes and cannot merge two of our
classes. The panel source is the subdivision-readiness wave's discriminating-gene column (genes
supported by at least two studies), i.e. the genes are read from a pre-registered construction and
not proposed here.

## How to reach a term

```
query_marker(cell_type='rod bipolar cell', library='cl56_v15')
query_marker(cell_type='keratocyte',       library='cl56_v15')
query_marker(cell_type='S cone cell',      library='cl56_v15')
```

Each of the three names is also a row of the link registry, carrying the entry's key markers, its
wiki page, its route and the papers that back it.

## Caveats, measured and stated

- **The panels are broad.** In the recorded-set reading of a merge into the default route, these
  three entries renamed 92 clusters, and only 3 of those 92 carry the adopted term as their own
  author label. The merge fails the pre-registered acceptance rule (the cell-weighted `consistent`
  share falls and the `inconsistent` share rises), which is why the increment stays default-off and
  the shipped default route is byte-identical with it registered. Read this page as "the finer name
  is now nameable", never as "this panel re-annotates a cluster automatically".
- **`keratocyte` also exists already** as `Keratocytes` in the shipped label map
  (CL:0002363), carried by a three-gene membrane entry that does not answer those clusters. The two
  are different panels for the same term; a future revision should decide between a rename and a
  second entry rather than keep both indefinitely.
- Eight pairs where **our** term is finer than the author's are a different question and are not
  folded into this adoption.

## Related pages

- `baselines/retina.md`, `vk_literature_index/photoreceptor.md` — retinal classes and their markers
- `baselines/ocular_surface.md`, `vk_literature_index/tissue-cornea.md` — corneal/ocular-surface classes
- `link_registry/README.md` — how an entry keeps its trail to papers, pages and routes