#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME 装配：pme_hits.jsonl + no_record_338.tsv -> accounts/sidecar/summary/recovery estimate。
审计修正（若有）读 ledgers/audit_fixes.tsv（key=class|gene），final grade 列体现修正，原始判定不掩。"""
import json, os, csv, datetime, hashlib, collections

ROOT = '/mnt/D/EyeKB/plans/panel_pmid_20260927'
E2 = '/mnt/D/EyeKB/plans/e2_decontam_20260926'
DIRECTIVE = '/mnt/D/OcularKB/WIKI/USER_DIRECTIVE_20260927_scoring_wave.md'
CARD = 't_f16d4e9f (EyeKB-PME)'

def sha(p):
    h = hashlib.sha256()
    with open(p, 'rb') as f:
        for c in iter(lambda: f.read(1 << 20), b''):
            h.update(c)
    return h.hexdigest()

def main():
    # key-level hits (v2 = post-A5 uniform regrade)
    hits = {}
    src = f'{ROOT}/out/pme_hits_v2.jsonl'
    if not os.path.exists(src):
        src = f'{ROOT}/out/pme_hits.jsonl'
    for l in open(src):
        d = json.loads(l)
        hits[(d['class'], d['gene'])] = d
    # audit fixes (worker self-audit; class|gene -> new_grade + note)
    fixes = {}
    fp = f'{ROOT}/ledgers/audit_fixes.tsv'
    if os.path.exists(fp):
        for row in csv.DictReader(open(fp), delimiter='\t'):
            fixes[(row['class'], row['gene'])] = row
    def kg(c, g):
        d = hits.get((c, g))
        if d is None:
            return None, None, 'MISSING'
        fx = fixes.get((c, g))
        return d, fx, (fx['final_grade'] if fx else d['grade'])

    # ---- strong self-audit sheet (regardless of fixes; I review this file) ----
    with open(f'{ROOT}/ledgers/strong_selfaudit.tsv', 'w') as f:
        f.write('class\tgene\tpmid\twhy\tsentence\n')
        for (c, g), d in sorted(hits.items()):
            if d['grade'] == 'strong':
                for e in d['strong_evidence'][:1]:
                    f.write(f"{c}\t{g}\t{e['pmid']}\t{e['why']}\t{e['sentence'].replace(chr(9),' ')}\n")

    # ---- row-level accounts (338) ----
    rows = [l.rstrip('\n').split('\t') for l in open(f'{ROOT}/data/no_record_338.tsv')]
    assert len(rows) == 338, len(rows)
    acct = open(f'{ROOT}/out/pme_accounts.tsv', 'w')
    acct.write('\t'.join(['library', 'class', 'gene', 'grade_key', 'final_grade', 'audit_note',
                          'strong_pmids', 'n_weak_pmids', 'evidence_first', 'query', 'raw_file']) + '\n')
    row_cnt = collections.Counter()
    key_cnt = collections.Counter()
    percls = collections.defaultdict(lambda: collections.Counter())
    for lib, cls, gene in rows:
        d, fx, fg = kg(cls, gene)
        if d is None:
            acct.write(f'{lib}\t{cls}\t{gene}\tMISSING\tMISSING\tkey not retrieved\t\t0\t\t\t\n')
            row_cnt['MISSING'] += 1
            continue
        key_cnt[d['grade']] += 0
        sp = ';'.join(e['pmid'] for e in d['strong_evidence']) if fg == 'strong' else ''
        ev = d['strong_evidence'][0]['sentence'][:220].replace('\t', ' ') if (fg == 'strong' and d['strong_evidence']) else ''
        acct.write('\t'.join([lib, cls, gene, d['grade'], fg,
                              (fx['note'] if fx else ''), sp,
                              str(len(d['weak_refs']) if fg == 'weak' else 0),
                              ev, d['query'], d['raw_file']]) + '\n')
        row_cnt[fg] += 1
        percls[f'{lib}|{cls}'][fg] += 1
    acct.close()
    for (c, g), d in hits.items():
        pass

    # ---- sidecar ----
    ann = collections.defaultdict(lambda: collections.defaultdict(dict))
    seen = set()
    for lib, cls, gene in rows:
        if (cls, gene) in seen and False:
            continue
        d, fx, fg = kg(cls, gene)
        if not d:
            continue
        seen.add((cls, gene))
        ann[lib][cls][gene] = {
            'grade': fg,
            'grade_engine': d['grade'],
            **({'audit_fix': {'to': fx['final_grade'], 'note': fx['note']}} if fx else {}),
            'evidence': d['strong_evidence'] if fg == 'strong' else [],
            'weak_refs': d['weak_refs'] if fg == 'weak' else [],
            'query': d['query'], 'hitCount': d['hitCount'],
            'raw_ledger': f'ledgers/raw/{d["raw_file"]}',
        }
    sidecar = {
        'version': 'evidence-chain-supplement-v1.0',
        'generated_at': datetime.datetime.now().isoformat(timespec='seconds'),
        'directive': DIRECTIVE,
        'prereg': {'file': f'{ROOT}/PME_PREREG_v1.md', 'sha256': sha(f'{ROOT}/PME_PREREG_v1.md'),
                   'amendments': 'A1 two-pass(+CITED) / A2 rods-cones guard / A3 pageSize50+4threads — all pre-run'},
        'card': CARD,
        'scope': 'E2 no_record 338 pairs (338 rows / 280 unique class-gene keys), batch-1; E2R 120 pmid_context pairs disjoint (overlap=0, ledgers/e2r_overlap_check.txt)',
        'europepmc_client': {
            'api': 'Europe PMC REST search (SRC:MED, resultType=core, pageSize=50, 2 passes per key when needed)',
            'tool': f'{ROOT}/scripts/pme_search.py',
            'evidence_dir': f'{ROOT}/ledgers/raw/',
            'rule': 'PMID 可解析 + 摘要级句内 基因∧类∧marker 词 = strong；文档级 基因∧类 = weak；查无=none（诚实阴性）。分级规则见 prereg §4，零 LLM 判读，worker 自审仅做降级修正并留痕。',
        },
        'kb_files_untouched': True,
        'counts_rows_338': dict(row_cnt),
        'counts_by_class': {k: dict(v) for k, v in sorted(percls.items())},
        'annotations': {lib: ann[lib] for lib in sorted(ann)},
    }
    json.dump(sidecar, open(f'{ROOT}/out/evidence_chain_supplement_v1.json', 'w'),
              ensure_ascii=False, indent=1)

    # ---- verdict matrix + summary ----
    strong = row_cnt['strong']; weak = row_cnt['weak']; none = row_cnt['none']
    cov = 100.0 * strong / 338
    if cov >= 50:
        verdict = 'row1: 工程缺口第一批关闭过半，剩余列第二批清单'
    elif cov >= 30:
        verdict = 'row2: 部分成立，按类拆分列缺口'
    else:
        verdict = 'row3: "无记录先验多不可外部证"定性，反馈 KB 线降档提案（不执行）'
    summary = {'rows_338': dict(row_cnt), 'strong_coverage_pct_rows': round(cov, 2),
               'keys_280': dict(collections.Counter(
                   (fx['final_grade'] if (fx := fixes.get((c, g))) else d['grade'])
                   for (c, g), d in hits.items())),
               'verdict_matrix': verdict,
               'card': CARD, 'generated_at': datetime.datetime.now().isoformat(timespec='seconds')}
    json.dump(summary, open(f'{ROOT}/out/pme_summary.json', 'w'), ensure_ascii=False, indent=1)

    # ---- S1 recovery estimate (structural proxy; NOT re-scored) ----
    # class-level panel composition from E2 summary
    e2sum = {}
    for l in open(f'{E2}/data/e2_matrix_rows_summary.tsv'):
        c = l.rstrip('\n').split('\t')
        if c[0] == 'library':
            continue
        e2sum[f'{c[0]}|{c[1]}'] = {'n_genes': int(c[2]), 'ext': int(c[3]), 'iax': int(c[4]), 'nor': int(c[5])}
    est = open(f'{ROOT}/out/s1_recovery_estimate.tsv', 'w')
    est.write('\t'.join(['lib|class', 'n_genes', 'no_record', 'strong', 'weak', 'none',
                         'strong_frac_of_nor', 'note']) + '\n')
    for k in sorted(percls):
        cc = percls[k]
        s = e2sum.get(k, {'n_genes': 0, 'nor': 0})
        nor = max(s['nor'], sum(cc.values()))
        est.write('\t'.join([k, str(s['n_genes']), str(nor), str(cc['strong']), str(cc['weak']), str(cc['none']),
                             f"{cc['strong']/nor:.3f}" if nor else 'NA', 'structural only, not re-scored']) + '\n')
    f_str = strong / 338; f_sw = (strong + weak) / 338
    gap = 17.35
    est.write(f'# STRUCTURAL ESTIMATE (not E2 numbers, not re-scored): S1-S2 gap=17.35pp '
              f'(S1 63.27 vs S2 45.92, E2_VERDICT §5).\n')
    est.write(f'# lower band 17.35*{f_str:.3f}={gap*f_str:.2f}pp (strong-only acceptance); '
              f'upper band 17.35*{f_sw:.3f}={gap*f_sw:.2f}pp (strong+weak acceptance), '
              f'assumes gap ∝ no_record chain coverage (most-optimistic linear attribution; class composition effects ignored).\n')
    est.close()

    print(json.dumps({'rows_338': dict(row_cnt), 'strong_cov_pct': round(cov, 2),
                      'verdict': verdict,
                      'band_pp': [round(gap*f_str, 2), round(gap*f_sw, 2)]}, ensure_ascii=False))

if __name__ == '__main__':
    main()
