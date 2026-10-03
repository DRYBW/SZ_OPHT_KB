# kbadd_KERATOCYTE_20260924.jsonl Archive Note (card t_e1febb8e, 2026-09-24)

This file registers marker library additions (Keratocytes/Corneal Endothelium, v1-membrane-20260924) and
**reference literature for composition baseline keratocyte reference cells, categorized by ingestion reason** (PI rules; reuses active 5 enums,
no new classes invented). Each entry includes `retrieval_status`:

- `VERIFIED_RETRIEVABLE` / `already_in_main_db=true`: Already in active RAG main library and this card verified retrievable via
  `search_literature` (e.g., PMID:34741068, 34381080, etc., 6 papers).
- `PENDING_MAIN_DB`: 4 papers (41060151/42115719/11328728/15914606) are new literature outside the main library—
  physical chunk augmentation must be written on the OcularKB side (writing prohibited in this card's territory) → **handled as blocking items per task brief red lines on separate cards**,
  this card's sidecar registration = traceable archive reason, ≠ RAG retrieval coverage (astra R6).
- Historical literature for downgraded/deprecated genes (MIME1/PDK4/CRYAB/MME/ANGPTL7/ALCAM supporting bibliographic records) are not included in this
  sidecar formal entries—their evidence status notes are in markers library provenance._aux_evidence /
  concepts.tsv EYEKBC-0018/0019, avoiding packaging unverified associations as ingestion evidence.

Machine-readable: `kbadd_KERATOCYTE_20260924.jsonl` (10 lines).
