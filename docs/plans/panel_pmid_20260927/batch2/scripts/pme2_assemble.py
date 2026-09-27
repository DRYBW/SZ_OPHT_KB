#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME2 装配（PREREG §3 直译，零 LLM）：
b1 final(快照) + b2 engine − b2 自审降级(audit_fixes_v2) → 键级 combined_final + 行级 338 回填
+ sidecar evidence_chain_supplement_v2.json + 两批合计可核链终读(对照 E2 567 基账) + 残余 none 两态。"""
import json, csv, hashlib, datetime, collections, os

ROOT = '/mnt/D/EyeKB/plans/panel_pmid_20260927'
B2 = f'{ROOT}/batch2'
E2_VERDICT_PAIRS = 567
E2_INFILE_VERIFIABLE = 30   # E2_VERDICT §B面板侧基账（引用，不改）
E2_INTERNAL_DERIVED = 199

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

ORD = {'none': 0, 'weak': 1, 'strong': 2}

# ---- b1 键级 final（含一批审计修正）----
b1_engine, b1_final, b1_cand = {}, {}, {}
for l in open(f'{B2}/in_b1_snapshot/pme_hits_v2.jsonl'):
    d = json.loads(l)
    k = (d['class'], d['gene'])
    b1_engine[k] = d['grade']; b1_cand[k] = d.get('n_candidates', 0)
    b1_final[k] = d['grade']
for r in csv.DictReader(open(f'{B2}/in_b1_snapshot/audit_fixes.tsv'), delimiter='\t'):
    b1_final[(r['class'], r['gene'])] = r['final_grade']

# ---- b2 引擎 + 二批自审 ----
b2, b2_final = {}, {}
for l in open(f'{B2}/out/pme2_hits.jsonl'):
    d = json.loads(l)
    k = (d['class'], d['gene'])
    b2[k] = d; b2_final[k] = d['grade']
fixes2 = {}
for r in csv.DictReader(open(f'{B2}/ledgers/audit_fixes_v2.tsv'), delimiter='\t'):
    k = (r['class'], r['gene'])
    fixes2[k] = r
    assert b2[k]['grade'] == 'strong', (k, 'fix targets must be b2-strong')
    b2_final[k] = r['final_grade']

# ---- 键级 103 账 ----
keys = [tuple(l.rstrip('\n').split('|')) for l in open(f'{B2}/data/batch2_keys.txt')]
assert len(keys) == 103 and len(set(keys)) == 103
acct = open(f'{B2}/out/pme2_accounts.tsv', 'w')
acct.write('\t'.join(['class','gene','b1_final','b2_engine','b2_final','combined_final',
                      'transition','b2_pmids','evidence_sentence','query_route2','hitCount_b2',
                      'n_cand_b1','n_cand_b2','audit_note_v2','raw_file_b2'])+'\n')
kc = collections.Counter(); trans = collections.Counter()
for k in keys:
    bf1 = b1_final[k]; bf2 = b2_final[k]
    comb = bf1 if ORD[bf1] >= ORD[bf2] else bf2
    kc[comb] += 1
    trans[f'{bf1}->{comb}' if bf1 != comb else 'unchanged'] += 1
    d = b2[k]
    ev = d['strong_evidence'][0]['sentence'][:240].replace('\t',' ') if (comb=='strong' and d['strong_evidence']) else ''
    # 若 slot1 被降级但 comb=strong 且 slot2 才是依据（ISL1/DES 案）：取合格槽
    if comb == 'strong' and fixes2.get(k):
        ev = ''  # 不会发生：fixes 都是降出 strong
    if comb == 'strong' and bf1 != 'strong':
        # 救回键：优先 slot2（若 slot1 与最终审计无关），两槽都留证据句
        ev = ' || '.join(e['sentence'][:200].replace('\t',' ') for e in d['strong_evidence'][:2])
    sp = ';'.join(e['pmid'] for e in d['strong_evidence']) if bf2 == 'strong' else ''
    acct.write('\t'.join([k[0], k[1], bf1, d['grade'], bf2, comb,
                          ('RESCUED' if comb != bf1 and ORD[comb] > ORD[bf1] else ('unchanged' if comb==bf1 else 'n/a')),
                          sp, ev, d['query'], str(d['hitCount']),
                          str(b1_cand.get(k, '')), str(d.get('n_candidates','')),
                          fixes2[k]['note'] if k in fixes2 else '', d['raw_file']])+'\n')
acct.close()

# ---- 行级 338 回填（280 键 combined = b1 combined ∪ 本批 103）----
rows = [l.rstrip('\n').split('\t') for l in open(f'{B2}/data/no_record_338.tsv') if l.strip() and not l.startswith('#')]
assert len(rows) == 338, len(rows)
rowc = collections.Counter(); percls = collections.defaultdict(collections.Counter)
row1 = open(f'{B2}/out/pme_rows338_combined.tsv', 'w')
row1.write('library\tclass\tgene\tb1_final\tb2_final\tcombined_final\n')
for lib, cls, gene in rows:
    k = (cls, gene)
    bf1 = b1_final.get(k, 'MISSING'); bf2 = b2_final.get(k)
    comb = bf1
    if bf2 and ORD[bf2] > ORD[comb]:
        comb = bf2
    rowc[comb] += 1
    percls[f'{lib}|{cls}'][comb] += 1
    row1.write('\t'.join([lib, cls, gene, bf1, bf2 or 'n/a', comb])+'\n')
row1.close()

# ---- 残余 none 两态（四遍合并候选数）----
n2state = {}
for k in keys:
    if b2_final.get(k) == 'none' and b1_final.get(k) == 'none':
        ntot = b1_cand.get(k, 0) + b2[k].get('n_candidates', 0)
        n2state[f'{k[0]}|{k[1]}'] = ('真缺文献(四遍零候选)' if ntot == 0 else '摘要级不可核(有候选无G∧C)')

# ---- sidecar v2 ----
ann = collections.defaultdict(lambda: collections.defaultdict(dict))
for lib, cls, gene in rows:
    k = (cls, gene)
    if k not in b2:   # 本批只管 103 非 strong 键；strong 键不重复登记
        continue
    d = b2[k]; bf1 = b1_final[k]; comb = max(bf1, b2_final[k], key=lambda g: ORD[g])
    ann[lib][cls][gene] = {
        'combined_final': comb,
        'grade_b1_final': bf1,
        'grade_b2_engine': d['grade'],
        **({'audit_fix_v2': {'to': b2_final[k], 'note': fixes2[k]['note']}} if k in fixes2 else {}),
        'evidence_route2': d['strong_evidence'] if comb == 'strong' and d['strong_evidence'] else [],
        'weak_refs_route2': d['weak_refs'] if d['grade'] == 'weak' else [],
        'query_route2': d['query'], 'aliases_used': d['aliases_used'],
        'hitCount_route2': d['hitCount'],
        'raw_ledger_route2': f'batch2/ledgers/raw2/{d["raw_file"]}',
        **({'none_residual_state': n2state.get(f'{cls}|{gene}') if comb == 'none' else None} if comb == 'none' else {}),
    }
sidecar = {
 'version': 'evidence-chain-supplement-v2.0',
 'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
 'card': 't_95cbb3ec (EyeKB-PME2)',
 'caliber_header': '口径由 PI 锁定（USER_DIRECTIVE_20260927 D7）："expressed in <该细胞类型>" 算 membership 型支持=中等档，为现行正式口径；类特异严格档若启用须全库对称重判另卡。',
 'prereg': {'file': 'batch2/PME2_PREREG_v1.md',
            'sha256_pre_run': [x.split()[0] for x in open(f'{B2}/ledgers/sha_prereg.txt')][0:1],
            'sha256_all_amendments': [x.split()[0] for x in open(f'{B2}/ledgers/sha_prereg.txt')],
            'amendment_A1p': '裸 sort=CITED 被 EBI 503（一批 84/84 二遍全灭根因，取证 ledgers/raw/）；二批改 sort=CITED desc 实测 75/75 生效。一批数字不改，其账=单遍 relevance 口径。'},
 'scope': 'batch2_backlog 103 非 strong 键（50 weak+53 none）；别名表全类对称（data/alias_gene_v2.tsv，UniProt human+reviewed 源，留弃全登记）；pmid_context 通道零使用（E2R 告诫继承）',
 'europepmc_client': {
   'api': 'Europe PMC REST search (SRC:MED, resultType=core, pageSize=50, route-2 aliased query, 2 passes relevance+CITED desc)',
   'tool': 'batch2/scripts/pme2_search.py',
   'rule': '分级规则=一批 PREREG §4 同构，G/C 扩展为 符号∪UniProt别名 / 类doc_re∪§2.1扩展；M 一字未改。strong=单句 G∧C∧M；weak=文档级 G∧C；none 诚实阴性。零 LLM，worker 自审 15 键 strong→weak（ledgers/audit_fixes_v2.tsv），原始引擎判定不掩。'},
 'kb_files_untouched': True,
 'batch1_untouched': True,
 'counts_keys_103': dict(kc),
 'counts_keys_combined_280': None,  # filled below
 'counts_rows_338_combined': dict(rowc),
 'per_class_rows_combined': {kk: dict(v) for kk, v in sorted(percls.items())},
 'transitions_103': dict(trans),
 'rescued_strong': sorted([f'{c}/{g}' for c, g in keys if b1_final[(c,g)] != 'strong' and max(b1_final[(c,g)], b2_final[(c,g)], key=lambda x: ORD[x]) == 'strong']),
 'none_residual_two_state': n2state,
 'final_reading_vs_e2_567': None,  # filled below
 'annotations': {lib: ann[lib] for lib in sorted(ann)},
}
# 280 键合计终账
kc280 = collections.Counter()
for k in b1_final:
    comb = max(b1_final[k], b2_final.get(k, 'none'), key=lambda g: ORD[g])
    kc280[comb] += 1
sidecar['counts_keys_combined_280'] = dict(kc280)
strong_rows = rowc['strong']
fr = {
 'e2_baseline_pairs': E2_VERDICT_PAIRS,
 'e2_infile_verifiable': E2_INFILE_VERIFIABLE,
 'e2_internal_derived': E2_INTERNAL_DERIVED,
 'e2_no_record_rows': 338,
 'no_record_strong_rows_b1': 222,
 'no_record_strong_rows_b1b2_combined': strong_rows,
 'verifiable_chain_pairs_combined': E2_INFILE_VERIFIABLE + strong_rows,
 'verifiable_chain_coverage_pct_of_567': round(100.0*(E2_INFILE_VERIFIABLE + strong_rows)/E2_VERDICT_PAIRS, 2),
 'note': 'E2 数字零改动；本读数仅为未来评测口径修订提供账。S1 弃权面线性预估（同一批公式）=17.35pp×strong/338='+str(round(17.35*strong_rows/338,2))+'pp（结构估计，非重跑）',
}
sidecar['final_reading_vs_e2_567'] = fr
json.dump(sidecar, open(f'{B2}/out/evidence_chain_supplement_v2.json', 'w'), ensure_ascii=False, indent=1)
json.dump({'keys_103': dict(kc), 'keys_280_combined': dict(kc280), 'rows_338_combined': dict(rowc),
           'transitions': dict(trans), 'final_reading': fr},
          open(f'{B2}/out/pme2_summary.json', 'w'), ensure_ascii=False, indent=1)

print('== keys103 combined:', dict(kc))
print('== keys280 combined:', dict(kc280))
print('== rows338 combined:', dict(rowc))
print('== transitions:', dict(trans))
print('== FINAL READING:', json.dumps(fr, ensure_ascii=False, indent=1))
print('== rescued:', len(sidecar['rescued_strong']))
print('== none residual states:', collections.Counter(n2state.values()))
