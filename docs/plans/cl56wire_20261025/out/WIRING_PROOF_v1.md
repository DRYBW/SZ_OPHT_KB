# WIRING_PROOF_v1 — the newest library wired like the other eight

Every number in this file is computed by `scripts/wiring_proof.py` from the shipped tree at build time (`kb/link_registry/LINK_REGISTRY_v1.jsonl`, `kb/**`, `mcp_server/eyekb_core.py`); nothing is quoted from a report. Recompute: `/home/ubuntu/training-venv/bin/python3 scripts/wiring_proof.py` (machine twin: `out/WIRING_PROOF_v1.json`).

**Verdict: PASS** — 4 rows added, 0 existing rows changed, 0 removed, 0 wiki page paths missing on disk, 0 routes not answering, 0 new names reachable on the default route.

## 1. Entries per library

| library | entries | in the default answer route |
|---|---|---|
| `textbook_t4` | 81 | textbook layer |
| `membrane` | 23 | yes |
| `antseg_v10` | 16 | yes |
| `retina` | 10 | yes |
| `retina_interneuron` | 10 | yes |
| `retina_v6` | 10 | yes |
| `face_v6` | 7 | yes |
| `k9_ocs` | 4 | yes |
| `cl56_v15` | 3 | no |
| `onfibro_v13` | 1 | yes |
| **total** | **165** | |

The registry's scope is the default route **plus** the libraries declared in `REGISTRY_EXTRA_LIBS` (`kb/link_registry/scripts/build_link_registry.py`); `cl56_v15` is the first of the latter, registered default-off with an empty whitelist.

## 2. Field completeness

- required fields per marker row: `entry_id`, `library`, `cell_type`, `panel_genes`, `kb_file`, `wiki_pages`, `n_wiki_pages`, `pmids`, `citations`, `mcp_route`, `skill_trigger`
- required fields per textbook row: `entry_id`, `library`, `cell_type`, `kb_file`, `wiki_pages`, `n_wiki_pages`, `mcp_route`, `skill_trigger`, `book_anchors`
- rows carrying all of them: **163/165** (98.8%)
- rows with a gap and a registered reason: 2
    - `face_v6::Fibroblast` missing ['panel_genes'] — the source library records no marker panel at all for this entry (registered gap, named in ANNOTATION_EVIDENCE_SUMMARY_v1.md)
    - `face_v6::Myofibroblast` missing ['panel_genes'] — the source library records no marker panel at all for this entry (registered gap, named in ANNOTATION_EVIDENCE_SUMMARY_v1.md)
- rows with an unexplained gap: none

The four-link rule of this repository (citation + page + route + skill) is not restated here: it is re-run.

```
linkage gate: 165/165 entries fully wired
PASS: every entry carries a citation, a page, a route and a skill entry point; every gene-verified citation matches the shipped full-text index
```

## 3. Wiki pages

- page paths listed across all rows: **403**
- resolved to a file under `kb/`: **403** (100.0%)
- missing: none

`kb_file` existence: all rows resolve.

## 4. Routes

- rows whose `mcp_route` was re-issued against the shipped service: **165**
- not answering: none

- new names reachable on the default `all` route (must be none, the library is registered default-off): none

## 5. Isomorphy against the pre-image

- pre-image rows: 161; current rows: 165
- rows unchanged (byte-identical JSON): **161/161**
- rows changed: none
- rows removed: none
- shipped row order preserved: True
- rows added (4): `cl56_v15::S cone cell`, `cl56_v15::keratocyte`, `cl56_v15::rod bipolar cell`, `onfibro_v13::Fibroblast`

The three rows of the newly wired library, as they now stand:

| entry | panel genes | citations | gene-verified | wiki pages |
|---|---:|---:|---:|---|
| `cl56_v15::S cone cell` | 22 | 46 | 37 | link_registry/out/ANNOTATION_EVIDENCE_APPENDIX_v1.md, vk_literature_index/cell-ontology-child-terms.md |
| `cl56_v15::keratocyte` | 60 | 58 | 52 | baselines/ocular_surface.md, composition/EXPECTED_COMPOSITION_v0.md, link_registry/out/ANNOTATION_EVIDENCE_APPENDIX_v1.md, literature_db/KBADD_KERATOCYTE_NOTES_20260924.md |
| `cl56_v15::rod bipolar cell` | 44 | 77 | 71 | baselines/retina.md, link_registry/out/ANNOTATION_EVIDENCE_APPENDIX_v1.md, priors/composition/human_retina.md, vk_literature_index/cell-ontology-child-terms.md |

## 6. Circularity (read, not quoted)

```
entries: 84
A. reachable at all            : 84/84
B. reachable excluding the registry's own rendered appendix: 84/84
   of which rely only on that appendix: 0
```

`kb/link_registry/scripts/audit_link_circularity.py` re-run: no entry is reachable *only* through the appendix this registry generates, including the three new ones.

## 7. What was NOT done, and why

- **The default route was not changed.** `CL56_DEFAULT_LIBS` is empty, and check 6 above re-reads that from the shipped service: the three names are not reachable on `all` in any state. Merging them is a separate decision that the pre-registered acceptance rule for this library failed.

- **Wiring the registry is not activating anything.** The registry is a disclosure surface: every row states the route that reaches it, and a default-off library's route is the explicit one. Check 6 re-reads from the shipped service that the three names answer on `library='cl56_v15'` and are NOT reachable on the default `all` route.

- **The rebuild carried one row this card did not ask for.** `onfibro_v13` was activated on the default route on 2026-10-22, after the registry snapshot was taken, so the builder produces its row (`onfibro_v13::Fibroblast`) from the route itself. Including it is what keeps the file reproducible by its own builder; dropping it would require pinning the library set, which is a bigger change than this one. It is disclosed here, in the registration notes and in the wave report.

- **Six registered libraries are still not wired** (`lacrimal_v6`, `retina_v7`, `retina_dev`, `lensiris_v11`, `holefill_v12`, `subtype_v14`). This proof does not claim otherwise. Each is the same one-line addition to `REGISTRY_EXTRA_LIBS`, and `subtype_v14` needs its body repaired first: its entries carry no top-level `markers` key, so its explicit route answers nothing and wiring it would create rows whose route is a dead end (measured in the CL-56 adoption report, §6.1).

