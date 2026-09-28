#!/usr/bin/env python3
"""RAGGAP step 7 — 交付件组装：报批清单 (TIER_A_approval_list.md) + B/C 档说明 + 主报告 (REPORT_RAGGAP.md)。"""
import csv, json, collections

OUT = '/mnt/D/EyeKB/plans/rag_gap_20260928/out'
DST = '/mnt/D/EyeKB/plans/rag_gap_20260928'

final = list(csv.DictReader(open(f'{OUT}/tier_FINAL.tsv'), delimiter='\t'))
items = {r['pmid']: r for r in csv.DictReader(open(f'{OUT}/tier_A_items.tsv'), delimiter='\t')}
stats = json.load(open(f'{OUT}/RAGGAP_STATS.json'))
gene_check = {}
for fn in ('epmc_gene_check.tsv', 'epmc_gene_check_extra.tsv'):
    for r in csv.DictReader(open(f'{OUT}/{fn}'), delimiter='\t'):
        gene_check.setdefault((r['gene'], r['ctx']), r)

# ---------- 内联重建 A 档去重 agg（不依赖 tier_A_agg.tsv 的坏格式） ----------
Arows = [f for f in final if f['tier'] == 'A']
bygene = {}
for f in Arows:
    k = (f['gene'], f['ctx_family'])
    d = bygene.setdefault(k, dict(entries=set()))
    d['entries'].add(f"{f['library'].replace(':prov', '')}/{f['entry']}")
agg = []
for (g, ctx), d in sorted(bygene.items()):
    chk = gene_check.get((g, ctx), {})
    cand = [p for p in (chk.get('top_pmids') or '').replace(';', ',').split(',') if p.strip().isdigit()]
    agg.append(dict(gene=g, ctx=ctx, n_entries=len(d['entries']), cand_pmids=cand[:3],
                    entries=';'.join(sorted(d['entries']))[:160]))
# 重写干净的 agg tsv
with open(f'{OUT}/tier_A_agg.tsv', 'w', newline='') as w:
    wr = csv.writer(w, delimiter='\t')
    wr.writerow(['gene', 'ctx', 'n_entries', 'cand_pmids', 'entries'])
    for a in agg:
        wr.writerow([a['gene'], a['ctx'], a['n_entries'], ','.join(a['cand_pmids']), a['entries']])

# ---------- A 档报批清单 ----------
pm_benefit = collections.Counter()
pm_genes = collections.defaultdict(list)
for a in agg:
    for p in a['cand_pmids']:
        pm_benefit[p] += 1
        pm_genes[p].append(f"{a['gene']}({a['ctx']})")
# 引用链 PMID（cited_chain origin）优先级最高
chain_pm = {p for p, r in items.items() if 'cited_chain' in r.get('origin', '')}
# 每基因至少保 1 篇候选 → 必补集 = chain_pm ∪ {每个 A 基因 cand[0]}
must = set(chain_pm)
for a in agg:
    if a['cand_pmids']:
        must.add(a['cand_pmids'][0])
extra = [p for p in pm_benefit if p not in must]
lines = ['# RAGGAP — A 档报批清单（零下载盘点产物，勾了才动）\n',
         f"生成: 2026-09-27 | 口径: RAG v2.1（附属核查 v2.2/v2.3 去重）| 全部 **未下载未重建**\n",
         '判据预注册: R1 库外引用链=R 必须补 / R2 EPMC 眼语境命中>5=可补 / R3 命中1-5=B 稀缺登记 / R4 命中0=B 真缺。\n',
         '体积说明: EPMC fullTextXML 为 chunked 流式（HEAD 无 Content-Length、拒绝 Range），单篇体积**无法零下载实测**；',
         '按经验上界 ≤0.5 MB/篇估算，**全清单 ≤ ~85 MB，>1GB 单独批条款不触发**；PI 批准执行时按所选管线复测。\n',
         f"## 汇总\n- A 档缺口基因（去重 gene×组织语境）: **{len(agg)}**（retina 58 / membrane 21 / lacrimal 7 / face 3 / kb9 3）\n",
         f"- 候选一手论文去重: **{len(pm_benefit)}** 篇（其中 OA 全文 {sum(1 for p in pm_benefit if items.get(p,{}).get('oa')=='Y')} 篇、摘要级 {sum(1 for p in pm_benefit if items.get(p,{}).get('oa')!='Y')} 篇）\n",
         f"- 已被 v2.2/v2.3 增量吸收: **{sum(1 for p in pm_benefit if items.get(p,{}).get('already_in'))}** 篇（免补）\n",
         f"- **净需批 = {sum(1 for p in must if not items.get(p,{}).get('already_in'))} 篇必补 + {sum(1 for p in extra if not items.get(p,{}).get('already_in'))} 篇备选**\n",
         '\n## 必补（每基因保 1 篇覆盖 + KB 词条引用链在库外的 7 篇）\n',
         '| 勾选 | PMID | 年份 | OA | 全文化语境 | 收益基因 | 标题(截断) | 备注 |',
         '|---|---|---|---|---|---|---|---|']
def fmt(p):
    r = items.get(p, {})
    if r.get('already_in'):
        return None
    return (f"| ☐ | {p} | {r.get('year','')} | {r.get('oa','')} | {r.get('ctx','')} | {pm_benefit[p]} | "
            f"{r.get('title','')[:58]} | {'词条引用链(R1)' if p in chain_pm else '基因扫描(R2)'} "
            f"{('；覆盖基因:' + ','.join(pm_genes[p][:4])) if len(pm_genes[p])>1 else ''} |")
for p in sorted(must, key=lambda x: (x not in chain_pm, -pm_benefit[x], x)):
    row = fmt(p)
    if row: lines.append(row)
lines.append('\n## 备选（同基因第 2-3 候选，加厚检索面；不批不补）\n')
lines.append('| 勾选 | PMID | 年份 | OA | 收益基因 | 标题(截断) |\n|---|---|---|---|---|---|')
for p in sorted(extra, key=lambda x: -pm_benefit[x]):
    r = items.get(p, {})
    if r.get('already_in'): continue
    lines.append(f"| ☐ | {p} | {r.get('year','')} | {r.get('oa','')} | {','.join(pm_genes[p][:4])} | {r.get('title','')[:60]} |")
lines.append('\n> ⚠ 候选=检索词族 top 命中（元数据级），个别相关性存疑（如 40971959 实为斑马鱼论文——词族不严格的实例，PI 勾选时复核）。\n'
             '> ⚠ 引用链 7 篇 PMID 若 PI 亦判不补，则相应词条（LACRT/PRR27/SCGB1D1/GAPDHS/LILRB2）维持"链在库外"现状——功能上 query_marker/search_literature 双通道已可用，仅"库内一手溯源"缺。\n')
open(f'{DST}/TIER_A_approval_list.md', 'w').write('\n'.join(lines))

# ---------- B 档登记 ----------
Brows = [f for f in final if f['tier'].startswith('B')]
bg = sorted({(f['gene'], f['ctx_family']) for f in Brows})
bl = ['# RAGGAP — B 档登记（文献面固有稀缺，禁算可补虚报缺口 — HC-LITRE 教训条款）\n',
      '| 基因 | 语境 | EPMC 眼语境命中 | 受影响词条 | 判据 |', '|---|---|---|---|---|']
for g, ctx in bg:
    chk = gene_check.get((g, ctx), {})
    ents = sorted({f"{f['library'].replace(':prov','')}/{f['entry']}" for f in Brows if f['gene'] == g and f['ctx_family'] == ctx})
    bl.append(f"| {g} | {ctx} | {chk.get('n_eye_hits','?')} ({chk.get('verdict','')}) | {', '.join(ents)} | R3 命中1-5=稀缺登记，不列补 |")
open(f'{DST}/TIER_B_rarity_register.md', 'w').write('\n'.join(bl) + '\n')

# ---------- C 档旁挂工程清单 ----------
Crows = [f for f in final if f['tier'] == 'C']
cc = collections.Counter(f['tier_note'].split(';')[0].split(' ')[0] for f in Crows)
cl = ['# RAGGAP — C 档索引旁挂工程清单（不需重建、不需新语料）\n',
      f'C 档共 **{len(Crows)}** 词条行：基因在 v2.1 库内确有 chunk 提及，但词条证据链未链接库内 PMID（链在库外或纯 canonical）。\n',
      '修复路径（全部旁挂，零重建）：\n'
      '1. **链回填**：`tier_C_backlog.tsv` 的 `link_candidate_pmids` 即库内支撑论文——词条 JSON 的 evidence 追加 `{"type":"pmid","id":"PMID:...","in_corpus":true}`（照 KB1v2d 先例，改词条不动 chunks/embedding）。\n'
      '2. **面板字段**：chunk 级 `marker_genes` 列仅 40 基因（v2.1 只建 QA 面板）——若要让 search_literature 的 marker 共现面覆盖词条基因，扩 `panels_v5.json` 后**只需重算该列元数据**（embedding 零重算，v2.2 先例）。\n'
      '3. **附属器语境缺口另算**：泪腺语境在库内 0 标签（V4 只查量不入库）——lacrimal 词条的语境支撑属 A 档扩容问题，不在本清单。\n',
      '| 分级 | 行数 | 含义 |\n|---|---|---|',
      f"| C_strong | {cc['C_strong']} | 语境匹配库内论文 ≥3 篇（回填即得强链） |",
      f"| C_mid | {cc['C_mid']} | 语境匹配 1-2 篇（回填为弱链，可接受） |",
      f"| C_ctx_mismatch→A | 74 | 提及但语境错配 → 已按 EPMC 语境判据转入 A/B 档（无一判 B） |\n"]
open(f'{DST}/TIER_C_index_backlog.md', 'w').write('\n'.join(cl))
# C backlog tsv 明细
with open(f'{DST}/tier_C_backlog_detail.tsv', 'w', newline='') as w:
    wr = csv.writer(w, delimiter='\t')
    wr.writerow(['gene', 'library', 'entry', 'ctx_grade', 'ctx_papers', 'link_candidate_pmids'])
    s2ctx = {(r['library'], r['entry'], r['gene']): r for r in csv.DictReader(open(f'{OUT}/s2_ctx_rows.tsv'), delimiter='\t')}
    for f in Crows:
        s = s2ctx.get((f['library'], f['entry'], f['gene']), {})
        wr.writerow([f['gene'], f['library'], f['entry'], s.get('c_grade', ''), s.get('ctx_papers', ''), s.get('ctx_top', '')])
print('A/B/C 交付件写出')
