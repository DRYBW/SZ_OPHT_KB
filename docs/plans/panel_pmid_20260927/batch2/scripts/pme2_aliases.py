#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""PME2 别名表构建（PME2_PREREG_v1 §2.2 直译，规则冻结，零 LLM）。
UniProt human+reviewed 取 gene synonyms 与 RecName/AltName 的 Full/Short；
机械过滤 F1-F5 全表统一；符号形别名过主符号冲突核查(F3)；面板内冲突双方弃用(F4)。
输出 data/alias_gene_v2.tsv（留+弃全登记）+ ledgers/raw_uniprot/*.json 审计件。"""
import json, re, time, urllib.parse, urllib.request, os, sys

ROOT = '/mnt/D/EyeKB/plans/panel_pmid_20260927/batch2'
RAWU = f'{ROOT}/ledgers/raw_uniprot'
UP = 'https://rest.uniprot.org/uniprotkb/search'
FIELDS = 'accession,id,gene_names,protein_name'

F_SYM = re.compile(r'^[A-Z][A-Z0-9-]{2,}$')                   # F3 触发形
F_CHARS = re.compile(r"^[A-Za-z0-9][A-Za-z0-9 ,.'/()-]*$")    # F2
BAD_NAME = re.compile(r'putative|uncharacterized|hypothetical|cdna flj|for ', re.I)  # F5

def fetch(params, tries=4):
    u = f'{UP}?{urllib.parse.urlencode(params)}&format=json'
    for i in range(tries):
        try:
            req = urllib.request.Request(u, headers={'User-Agent': 'PME2-alias/1.0 (offline audit)'})
            with urllib.request.urlopen(req, timeout=40) as r:
                return json.loads(r.read().decode('utf-8')), u, None
        except Exception as e:
            err = f'{type(e).__name__}: {e}'
            time.sleep(4 * (i + 1))
    return None, u, err

def primary_symbol(e):
    gn = e.get('genes')
    if isinstance(gn, list) and gn:
        gn = gn[0]
    gn = gn or {}
    return (gn.get('geneName') or {}).get('value')

def names_from_entry(e, gene):
    """取 primaryGeneName==gene 的条目；返回 [(alias, source)]"""
    if primary_symbol(e) != gene:
        return []
    out = []
    gn = e.get('genes')
    items = gn if isinstance(gn, list) else ([gn] if gn else [])
    for it in items:
        if (it.get('geneName') or {}).get('value') != gene:
            continue
        for s in it.get('synonyms', []) or []:
            v = (s.get('value') or '').strip()
            if v:
                out.append((v, 'uniprot_syn'))
    pd = e.get('proteinDescription') or {}
    def addname(obj, srcfull, srcshort):
        fn = (obj.get('fullName') or {}).get('value', '').strip()
        if fn:
            out.append((fn, srcfull))
            for part in re.split(r'[;,]', fn):   # 去 EC 后缀等分号段
                part = part.strip()
                if part and part != fn and len(part) >= 4:
                    out.append((part, srcfull + '_segment'))
        for sn in obj.get('shortNames', []) or []:
            v = (sn.get('value') or '').strip()
            if v:
                out.append((v, srcshort))
    if pd.get('recommendedName'):
        addname(pd['recommendedName'], 'uniprot_recname_full', 'uniprot_recname_short')
    for alt in pd.get('alternativeNames', []) or []:
        fn = (alt.get('fullName') or {}).get('value', '').strip()
        if fn:
            out.append((fn, 'uniprot_altname_full'))
        for sn in alt.get('shortNames', []) or []:
            v = (sn.get('value') or '').strip()
            if v:
                out.append((v, 'uniprot_altname_short'))
    return out

def main():
    genes = [l.strip() for l in open(f'{ROOT}/data/genes_103.txt') if l.strip()]
    assert len(genes) == 103, len(genes)
    rows = {}
    for g in genes:
        rp = f'{RAWU}/{g}.json'
        if os.path.exists(rp):
            cached = json.load(open(rp))
            if cached.get('raw') and cached['raw'].get('results'):
                d = cached['raw']
            else:
                d = None
        else:
            d = None
        if d is None:
            d, u, err = fetch({'query': f'gene_exact:{g} AND organism_id:9606 AND reviewed:true',
                               'fields': FIELDS, 'size': 25})
            json.dump({'gene': g, 'url': u, 'error': err, 'raw': d}, open(rp, 'w'), ensure_ascii=False)
            time.sleep(0.15)
        else:
            u = json.load(open(rp)).get('url')
        cands = []
        for e in (d or {}).get('results', []):
            cands += names_from_entry(e, g)
        rows[g] = {}
        for alias, src in cands:
            if alias.upper() == g.upper() or alias in rows[g]:
                continue
            if len(alias) < 4:
                rows[g][alias] = (src, 0, 'F1_len<4'); continue
            if not F_CHARS.match(alias):
                rows[g][alias] = (src, 0, 'F2_charset'); continue
            if BAD_NAME.search(alias):
                rows[g][alias] = (src, 0, 'F5_badword'); continue
            if re.search(r'\bIso[A-Z]', alias) or 'Precursor' in alias or 'Fragment' in alias \
               or re.match(r'^\d', alias) or alias.lower() in ('chain', 'subunit'):
                rows[g][alias] = (src, 0, 'F5_formname'); continue
            rows[g][alias] = (src, 1, '')
        print(f'[u1] {g}: cands={len(rows[g])} kept={sum(1 for v in rows[g].values() if v[1])}', flush=True)

    sym_alias = [(g, a) for g in rows for a, (s, k, r) in rows[g].items() if k and F_SYM.match(a)]
    print(f'[F3] symbol-like aliases to check: {len(sym_alias)}', flush=True)
    for g, a in sym_alias:
        cp = f'{RAWU}/_check_{re.sub(r"[^A-Za-z0-9-]","_",a)}.json'
        if os.path.exists(cp):
            d = json.load(open(cp)).get('raw')
        else:
            d, u, err = fetch({'query': f'gene_exact:{a} AND organism_id:9606 AND reviewed:true',
                               'fields': 'accession,id,gene_names', 'size': 25})
            json.dump({'alias': a, 'url': u, 'raw': d}, open(cp, 'w'), ensure_ascii=False)
            time.sleep(0.15)
        others = set()
        for e in (d or {}).get('results', []):
            p = primary_symbol(e)
            if p and p != g:
                others.add(p)
        if others:
            rows[g][a] = (rows[g][a][0], 0, 'F3_conflict:' + ','.join(sorted(others)))

    genes_up = {g.upper() for g in genes}
    by_alias = {}
    for g in rows:
        for a, (s, k, r) in rows[g].items():
            if k:
                by_alias.setdefault(a, []).append(g)
    for a, gs in by_alias.items():
        dup = len(gs) > 1 or (a.upper() in genes_up)
        for g in gs:
            if dup:
                rows[g][a] = (rows[g][a][0], 0, 'F4_panel_conflict')
            for og in genes:
                if og.upper() == a.upper() and og != g:
                    rows[g][a] = (rows[g][a][0], 0, 'F4_panel_conflict')

    with open(f'{ROOT}/data/alias_gene_v2.tsv', 'w') as f:
        f.write('gene\talias\tsource\tkept\tdrop_reason\n')
        for g in sorted(rows):
            for a, (s, k, r) in sorted(rows[g].items()):
                f.write(f'{g}\t{a}\t{s}\t{k}\t{r}\n')
    tot = sum(len(v) for v in rows.values())
    kept = sum(1 for g in rows for a in rows[g] if rows[g][a][1])
    genes_with = sum(1 for g in rows if any(rows[g][a][1] for a in rows[g]))
    print(f'[PME2-alias] cands={tot} kept={kept} genes_with_alias={genes_with}/103')

if __name__ == '__main__':
    main()
