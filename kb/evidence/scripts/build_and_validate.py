#!/usr/bin/env python3
"""Build d0_claims_v1.jsonl from draft + run verbatim literal validation."""
import json

draft = json.load(open('d0_claims_draft.json'))
d0 = json.load(open('d0_chunks.json'))
admission = json.load(open('/mnt/D/OcularKB/ocularkb/rag/data_d0/d0_admission.json'))

by_pmid = {}
for c in d0:
    by_pmid.setdefault(c['paper_id'], []).append(c)

ALLOWED_REASON = {"core_reference","method_anchor","data_anchor","contradicting_evidence","background"}
ALLOWED_REL = {"supports","refutes","qualifies","context_only"}
ALLOWED_TARGET_PREFIX = {"baseline_human_retina","human_retina","human_pdr_membrane","PDR__fibrovascular_membrane","proliferative_DR","GSE165784V2"}

records=[]
fails=[]
for cl in draft:
    ex = cl['extracted']
    ingested = admission[cl['pmid']]['checks']['fulltext']['ingested']
    rec = {
        "claim_id": cl['id'],
        "pmid": cl['pmid'],
        "title": admission[cl['pmid']]['title'],
        "inclusion_reason": cl['inclusion_reason'],
        "claim_relation": cl['claim_relation'],
        "evidence_context": {
            "kb_target": cl['kb_target'],
            "section": ex['section'] if ex['section'].strip() else ex['chunk_type'],
            "verbatim": ex['verbatim'],
            "limitation": cl['limitation'],
        },
        "provenance": {
            "chunk_type": ex['chunk_type'],
            "ingested": ingested,
            "extract_mode": "scripted_probe_sentence",
            "generated_by": "extract_claims.py @ t_1e783e43",
        },
    }
    records.append(rec)

with open('/mnt/D/EyeKB/kb/evidence/d0_claims_v1.jsonl','w') as f:
    for r in records:
        f.write(json.dumps(r, ensure_ascii=False)+"\n")
print(f"wrote {len(records)} records -> d0_claims_v1.jsonl")

# ---------- validation pass (independent re-check, literal substring) ----------
n_pass=0; n_fail=0; fail_list=[]
for r in records:
    ec = r['evidence_context']; errs=[]
    if r['inclusion_reason'] not in ALLOWED_REASON: errs.append('bad inclusion_reason')
    if r['claim_relation'] not in ALLOWED_REL: errs.append('bad claim_relation')
    if ec['kb_target'].split('#')[0] not in ALLOWED_TARGET_PREFIX: errs.append('bad kb_target')
    if not (0 < len(ec['verbatim'].split()) <= 50): errs.append('verbatim word count')
    if not ec['limitation'].strip(): errs.append('empty limitation')
    hit = [c for c in by_pmid[r['pmid']] if ec['verbatim'] in c['text']]
    if not hit: errs.append('VERBATIM NOT LITERAL SUBSTRING OF ANY CHUNK')
    elif r['provenance']['ingested']=='abstract_only' and all(c['chunk_type']!='abstract' for c in hit):
        errs.append('abstract-only paper but quote not from abstract chunk')
    if errs:
        n_fail+=1; fail_list.append((r['claim_id'], errs))
    else:
        n_pass+=1

total=n_pass+n_fail
print(f"validation: {n_pass}/{total} pass = {100*n_pass/total:.1f}%")
for cid, e in fail_list: print("  FAIL", cid, e)

summary = {"total": total, "pass": n_pass, "fail": n_fail, "pass_rate": n_pass/total,
           "fail_list": [{"claim_id": c, "errors": e} for c,e in fail_list]}
json.dump(summary, open('validation_result.json','w'), indent=1)

# coverage stats for report
from collections import defaultdict, Counter
per_paper = Counter(r['pmid'] for r in records)
per_target = Counter(r['evidence_context']['kb_target'] for r in records)
per_reason = Counter(r['inclusion_reason'] for r in records)
per_rel = Counter(r['claim_relation'] for r in records)
print("per_paper", dict(per_paper))
print("per_reason", dict(per_reason))
print("per_rel", dict(per_rel))
json.dump({"per_paper":dict(per_paper),"per_target":dict(per_target),"per_reason":dict(per_reason),"per_rel":dict(per_rel)},
          open('coverage_stats.json','w'), ensure_ascii=False, indent=1)
