#!/usr/bin/env python3
"""Independent verbatim validator for d0_claims_v1.jsonl (acceptance re-runnable).
Usage: python3 verify_d0_claims.py [claims.jsonl]
Exit 0 iff 100% literal-substring pass + schema/enum checks pass."""
import json, sys, collections

CLAIMS = sys.argv[1] if len(sys.argv) > 1 else '/mnt/D/EyeKB/kb/evidence/d0_claims_v1.jsonl'
DB = '/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.2_2026-09/chunks.parquet'
PMIDS = {"35061025","37917183","39220810","40069725","40562775","41578023","42601615"}
ALLOWED_REASON = {"core_reference","method_anchor","data_anchor","contradicting_evidence","background"}
ALLOWED_REL = {"supports","refutes","qualifies","context_only"}
ALLOWED_TARGET = {"baseline_human_retina","human_retina","human_pdr_membrane","PDR__fibrovascular_membrane","proliferative_DR","GSE165784V2"}

import pyarrow.parquet as pq
tbl = pq.read_table(DB, columns=["paper_id","chunk_type","text"])
pdf = tbl.to_pandas()
d0 = pdf[pdf['paper_id'].isin(PMIDS)]
chunks_by_pmid = collections.defaultdict(list)
for pid, ct, tx in d0[['paper_id','chunk_type','text']].itertuples(index=False):
    chunks_by_pmid[pid].append((ct, tx))

n_fail = 0; n = 0
for line in open(CLAIMS):
    r = json.loads(line); n += 1
    ec = r['evidence_context']; errs = []
    if r['inclusion_reason'] not in ALLOWED_REASON: errs.append('inclusion_reason enum')
    if r['claim_relation'] not in ALLOWED_REL: errs.append('claim_relation enum')
    if ec['kb_target'].split('#')[0] not in ALLOWED_TARGET: errs.append('kb_target allowlist')
    if not (0 < len(ec['verbatim'].split()) <= 50): errs.append('verbatim >50 words or empty')
    if not ec['limitation'].strip(): errs.append('empty limitation')
    hits = [tx for ct, tx in chunks_by_pmid[r['pmid']] if ec['verbatim'] in tx]
    if not hits: errs.append('verbatim not literal substring of any D0 chunk')
    if errs:
        n_fail += 1
        print(f"FAIL {r['claim_id']} ({r['pmid']}): {errs}")
print(f"checked {n} claims, {n-n_fail} pass, {n_fail} fail -> {'100% PASS' if n_fail==0 else 'GATE FAILED'}")
sys.exit(0 if n_fail == 0 else 1)
