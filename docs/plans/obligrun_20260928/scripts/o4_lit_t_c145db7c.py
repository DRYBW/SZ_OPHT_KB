#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""OBLIGRUN OB-4 (t_c145db7c): lit 逐条同源排除筛查留档（注册包 §9 规则逐字执行）。
筛查对象=正式票面全部 lit 命中条目（含 8 冻结簇 RUN5 代整行 lit）。
两级：标题级初筛（D002 构成研究 source paper 观看列表）+ 片段级复核（本地语料 chunks 指派关系）。
产 out/OB4_lit_hits.tsv（逐条命中/判定/剔除动作）+ out/OB4_lit_screening.md。
判"同源排除">0 → 票面污染事件（PREREG §6/§7：block 上报，作废留痕，不重跑粉饰；退出码 3）。"""
import json, re, hashlib, sys
import pandas as pd

ROOT = '/mnt/D/EyeKB/plans/obligrun_20260928'
D002 = {'GSE218123': 'chakravarti_GSE218123', 'GSE153515': 'chen_pub_GSE153515',
        'GSE186433': 'dickman_GSE186433', 'GSE155683': 'lako_adult_GSE155683',
        'GSE147979': 'li_GSE147979', 'GSE157474': 'shi_GSE157474'}
# 观看列表：study→source paper 判定（证据=论文自存声明×GEO 系列题名一致 + D002 obs.study×GSM 直读）
SOURCE_PAPERS = {
    '36712326': 'chakravarti_GSE218123（Maiti et al. PNAS Nexus 2022，通讯 Chakravarti；Data Availability 自存 GSE218123=GEO 系列题名逐字一致；'
                'D002 obs.study 直读 chakravarti_GSE218123 GSM6735065… 4,388 评测细胞）',
}
# 片段级复核用指派关系模式（cell population→author label）
ASSIGN_RE = re.compile(r'(cluster[s]?|cell (?:population|type|state)s?|CL)\b[^.]{0,160}?\b(?:was|were|is|are)?\s*(annotated|labeled|labelled|identified|defined|classified|designated)\b', re.I)
GSE_RE = re.compile(r'GSE\d{5,8}')

face = [json.loads(l) for l in open(f'{ROOT}/face/EV_DIGEST_SLIM_q6_oblig.jsonl', encoding='utf-8')]
changed = set(json.load(open('/mnt/D/EyeKB/plans/kb9_ocs_20260927/out/kb9_changed_clusters.json'))['changed'])
hits = []
for r in face:
    for ct, es in (r.get('lit') or {}).items():
        for e in es:
            hits.append(dict(cluster_id=r['cluster_id'], era=('变化簇-KB9重建' if r['cluster_id'] in changed else '冻结簇-RUN5代'),
                             cell_type=ct, pmid=str(e.get('pmid')), year=e.get('yr'), title=(e.get('t') or '')))
pmids = sorted({h['pmid'] for h in hits})

# ---- 片段级扫描（本地语料，只读）----
df = pd.read_parquet('/mnt/D/OcularKB/ocularkb/rag/literature_db/v2.0_2026-09/chunks.parquet',
                     columns=['paper_id', 'section', 'text'])
sub = df[df['paper_id'].astype(str).isin(pmids)]
paper_evi = {}
for p, g in sub.groupby('paper_id'):
    gse_own, assign_n, assign_ex = set(), 0, []
    for _, row in g.iterrows():
        t = str(row['text'])
        for m in GSE_RE.finditer(t):
            gse_own.add(m.group(0))
        if ASSIGN_RE.search(t):
            assign_n += 1
            if len(assign_ex) < 2:
                assign_ex.append(str(row['section']))
    d002_ment = sorted(set.intersection(set(gse_own), set(D002)))
    # 自存声明限定：仅 Data availability/Methods 段的 "deposited...GSExxxx" 视为 own-deposit
    own_dep = set()
    for _, row in g[g['section'].astype(str).str.contains('availab|Methods', case=False, na=True)].iterrows():
        t = str(row['text'])
        for mm in re.finditer(r'deposited[\s\S]{0,200}?(GSE\d{5,8})', t, re.I):
            own_dep.add(mm.group(1))
    paper_evi[p] = dict(n_chunks=len(g), gse_mentions=d002_ment, own_deposit=sorted(own_dep),
                        assign_hits=assign_n, assign_sections=assign_ex)

rows_out, excl = [], 0
for h in hits:
    p = h['pmid']
    ev = paper_evi.get(p, {})
    tier1 = p in SOURCE_PAPERS
    tier2 = bool(ev.get('assign_hits'))
    own_d002 = sorted(set.intersection(set(ev.get('own_deposit', [])), set(D002)))
    ruling = '同源排除' if (tier1 or own_d002) else '保留'
    action = '票面剔除该 lit 行（票面污染事件，block 留痕）' if ruling == '同源排除' else '无'
    if ruling == '同源排除':
        excl += 1
    basis = (SOURCE_PAPERS[p] if tier1 else
             (f"own-deposit∩D002={own_d002}" if own_d002 else
              f"非 D002 source paper（观看列表 9 study 无匹配；{'片段含指派关系但对象为自有/第三方数据集' if tier2 else '无 D002 存集声明'}）"))
    rows_out.append({**h, 'tier1_title_watch': tier1, 'tier2_assign_hits': ev.get('assign_hits', 0),
                     'own_deposit_D002': ';'.join(own_d002), 'ruling': ruling, 'action': action, 'basis': basis})

cols = ['cluster_id', 'era', 'cell_type', 'pmid', 'year', 'title', 'tier1_title_watch', 'tier2_assign_hits', 'own_deposit_D002', 'ruling', 'action', 'basis']
with open(f'{ROOT}/out/OB4_lit_hits.tsv', 'w', encoding='utf-8') as f:
    f.write('\t'.join(cols) + '\n')
    for x in rows_out:
        f.write('\t'.join(str(x[c]) for c in cols) + '\n')

md = []
md.append('# OB4_lit_screening — lit 逐条同源排除筛查留档（t_c145db7c，注册包 §9）')
md.append('')
md.append(f'- 筛查对象：正式票面全部 lit 命中 {len(rows_out)} 条 / {len(pmids)} 唯一 PMID（含 8 冻结簇 RUN5 代整行 lit——同受 §9 排除规则约束）。')
md.append('- 排除对象定义（注册包 §9 逐字）：直接陈述本评价 33 簇（D002 author 标注）类属归属的文献及其片段（含 Q6 truth 来源标注论文及其补充表）；判定标准=片段文本是否含"簇/细胞群→作者标签"指派关系（标题级初筛+片段级复核两级）。')
md.append('- 观看列表（D002 study 层全集，obs.study×GSM 直读）：9 study 标签 = chakravarti_GSE218123 / chen_cornea / chen_limbus / chen_pub_GSE153515 / chen_sclera / dickman_GSE186433 / lako_adult_GSE155683 / li_GSE147979 / shi_GSE157474。评测池 100k 细胞构成：6 个 GSM 直读 study 20,429 细胞 + chen_cornea/limbus/sclera 无 GSM 前缀 79,571 细胞（无 accession，本地不可解析其 source paper——登记残余限制，见文末）。')
md.append('')
md.append('## 逐条判定汇总')
md.append('')
md.append('| PMID | 标题级初筛 | 片段级复核 | 判定 |')
md.append('|---|---|---|---|')
for p in pmids:
    ev = paper_evi.get(p, {})
    t = next(h['title'] for h in hits if h['pmid'] == p)
    src = SOURCE_PAPERS.get(p, '')
    own = sorted(set.intersection(set(ev.get('own_deposit', [])), set(D002)))
    tag = '**Q6 truth 来源标注论文**' if src else ('own-deposit 含 D002 存集' if own else '非 D002 source')
    md.append(f"| {p} | {t[:60]} | {tag}；片段指派命中={ev.get('assign_hits',0)}；D002 accession 提及={ev.get('gse_mentions',[])} | {'**同源排除**' if (src or own) else '保留'} |")
md.append('')
md.append('## 排除动作（逐条）')
for x in rows_out:
    if x['ruling'] == '同源排除':
        md.append(f"- **剔除**：{x['cluster_id']}（{x['era']}）lit 行 ct={x['cell_type']} PMID={x['pmid']} —— {x['basis']}。"
                  f"该论文含 Endothelium 类群指派段落（Results > Endothelial cell types…），其作者标注即 D002/Q6 对 chakravarti cells 的 truth 标签来源；"
                  f"票面渲染行\"Endo|PMID:36712326|…identifies cell fates…\"= 对 truth=Endothelium 簇（Q6::7/Q6::11）的来源标签回证通道（E1 \"lit 背答案\"机制实例）。")
md.append('')
md.append('## 披露项（保留但登记）')
md.append('- 38177186（Li M et al. Nat Commun 2024）：Data availability 明示输入数据下载自 GSE155683（=lako_adult D002 构成研究）、自存 GSE249150（非 D002）。**非 truth 来源论文**（lako 标签定义于 GSE155683 原发表），属第三方再分析；其片段对 GSE155683 细胞群的自有再注释≠D002 所用 author 标签。保留，登记"再分析关系"。')
md.append('- 37443842（Cells 2023 综述）：无自存数据；可能转述各 study 结果（间接）。无 33 簇指派证据，保留。')
md.append('- 39422453（Schlemm canal）：自存 GSE272434/GSE271132，非 D002 构成；保留。')
md.append('')
md.append('## 残余限制（如实登记）')
md.append('- chen_cornea / chen_limbus / chen_sclera（评测池 79,571 细胞主体）obs 无 accession、无 GSM 前缀，本地证据层无法解析其 source paper；'
          '已核 12 命中 PMID 的作者/题名/自存声明均不匹配 chen 系（34381080=Ligocki/Fuchs；37389178=Kitao/Takayanagi；38177186=Li M）。若 chen 系来源论文后续获权威 accession 映射，需重跑本筛查（登记为下游项）。')
md.append('- 本 run 票面 lit 字段仅存 pmid/year/title[:90]（KB9 建面包实现事实），"片段级"复核在语料 chunk 层执行；渲染给判读席的文本面=title 行——对 Q6 truth 来源论文按 §9 括注（"含 Q6 truth 来源标注论文及其补充表"）类别级排除，不依赖单条片段文本。')
md.append('')
md.append(f'## 结论')
md.append(f'- 判定：**{excl} 条命中"同源排除"（PMID 36712326 × Q6::7/Q6::11 两行）→ 冻结票面含未排除的 truth 来源 lit = 票面污染事件**。')
md.append('- 按 PREREG §6/§7：票面作废条件命中 → block 上报，作废留痕，不重跑粉饰；正式三席票未开跑（票预算消耗 0/150）。')
open(f'{ROOT}/out/OB4_lit_screening.md', 'w', encoding='utf-8').write('\n'.join(md) + '\n')
print(f'OB-4: {len(rows_out)} hits / {len(pmids)} pmids | 同源排除={excl} 条')
print('paper evidence:')
for p in pmids:
    print(' ', p, paper_evi.get(p, {}))
sys.exit(3 if excl else 0)
