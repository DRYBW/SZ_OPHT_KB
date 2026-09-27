#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG 二审送审件组装：注册包全文 verbatim + 14 接受项逐条闭合对照（REVIEWER_LLM 上轮原文摘录 + 闭合位置）。
信息差铁律：REVIEWER_LLM 不靠记忆——上轮意见原文与本轮闭合文本同呈。零 LLM（纯装配）。"""
import json, os, re

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
PKG = open(f'{ROOT}/register/REGISTER_PACKAGE_v2.md', encoding='utf-8').read()
SB  = open(f'{ROOT}/register/SUPRABASAL_RECHECK.md', encoding='utf-8').read()
NOTE = re.search(r'## EDITORIAL_NOTE.*', open(f'{ROOT}/KB9_BUILD_REPORT.md', encoding='utf-8').read(), re.S).group(0)

# (ID, REVIEWER_LLM 上轮意见关键原文摘录[verbatim from RECHECK_REPLY], 闭合位置)
C = [
("A01", "因此，KB9 可以定位为\u201c基于 RUN5 已知错误的开发集定向修复与回归检查\u201d。24/33 若达标，是该开发集上的工程验收结果，不能作为独立验证的性能增益。",
 "注册包 §0 标题页定位限定声明（含 D10 落定的 A02 红线操作定义引文）+ §10-1 残留限制"),
("A03", "新词条所用 agg 参考池也应登记与 D002 的 study/donor 重叠情况。",
 "注册包 §2（实算表，载体 register/A03_OVERLAP_REGISTRY.tsv，npz 池层与 h5ad obs 逐格对账）"),
("A05", "这里必须补上一条明确规则：**n_shared=0 的类别不得进入 top3；不足三个有效候选时保留不足三个，不能靠加载顺序补齐。新增词条的加载位置和平票规则也要冻结**，否则新条可能持续输给旧条。",
 "注册包 §4 AV2-1/2/3/4（加载位置=尾部追加冻结；平票=插入序冻结，其\u201c新条让位旧条\u201d后果显式呈报，改平票语义须新版本注册）"),
("A06", "建议将规则冻结为\u201c条目 ID—组织适用范围\u201d表，逐项说明排除依据，并处理同一类别在其他文件中的重复条目。来源文件可以作为实现索引，不能单独充当生物学排除依据。",
 "注册包 §3 + 载体 register/A06_R1_ITEM_SCOPE_TABLE.tsv（30 排除条目逐条生物学依据；重复条目逐条登记整组同退；REVIEWER_LLM 关切的\u201c通用免疫/血管类\u201d经查在三文件中不存在被整批排除项，已在 §3 列证）"),
("A07", "投票前应固定输出一张诊断表：各簇各候选的原始命中、删除命中、剩余命中、名次变化，以及 Q6::8/26 的免疫候选是否仍有有效支持、是否进入 top3。",
 "注册包 §6 诊断表输出规格（列全 + \u201c只呈现实证面不积分\u201d + 票面不一致=run 作废；Q6::8/26 逐簇单列；掏空型回退可指认）"),
("A09", "必须先冻结每个候选类别到九类评价词表的映射，再定义\u201c其它\u201d。……仅凭 KERA 出现在 Fibroblasts top60，不能推出 KERA 应被屏蔽，更不能推出 Keratocytes 的全部面贡献归零。",
 "注册包 §5（映射冻结声明：Keratocytes→Fibroblasts，alias 先例；\u201cKERA 必被屏蔽\u201d旧预期正式作废；实跑 KERA/NNMT 保留、ALDH3A1 屏蔽=折叠域定义的自然推论）"),
("A11", "混合票集可以用于缓存式自检，但不等同于一次新的全量复测，也不足以隔离 KB9 的增益",
 "注册包 §9 组批事实 + KB9_BUILD_REPORT 文末 EDITORIAL_NOTE 第 1 条（定性=缓存式系统验收输出；增益不独立归因；§10-3 残留限制）"),
("A12", "保真门应同时覆盖 OFF 历史状态和与 RUN5 存档票对应的 ON 状态。仅复刻 OFF ranking，不能证明 Arm1 已复现 RUN5 的证据输入。",
 "注册包 §4 AV2-5（双态强制；KB9 实测 G0 OFF 33/33 + G1 ON 33/33 为既有实证）"),
("A13", "\u201c输入不变\u201d还必须按模型实际接收到的完整请求判断……若\u201c5/批\u201d是五个簇共用一个提示或上下文，重新组批会改变未修改簇的输入环境……预注册需要写清楚。top_genes 可以原样保留；gene_hits 若包含旧库候选、匹配基因或类别信息，就不能未经依赖检查直接搬运……tissue_composition_ref 也应确认不含作者标签导出的答案信息。……lit 重建……应冻结实际返回的文献、片段和顺序，并排除同源答案证据。……新增 crosswalk 应在投票前冻结。",
 "注册包 §9 四款（组批语义=5 簇共享单 prompt 已写明；gene_hits 本面 33/33 全空；tc_ref=作者标签派生但未入判读 prompt（build_prompt 渲染面实证）；lit 重建入面冻结；crosswalk 投票前落盘。KB9 实跑按变化簇子集重组批=不改判，登记解释性局限，EDITORIAL_NOTE 第 2 条）"),
("A15(措辞)", "当前 §1.1 的\u201c换判据域，见 R2/R3 后新共享基因屏蔽域\u201d**不成立**……排名时忽略某些基因，不能让原先未通过准入的基因通过。",
 "注册包 §8-1（该措辞在注册文本中作废；PREREG 原文冻结不回改；suprabasal 条成立依据改写为\u201c§1.2 正确执行+外部文献通道\u201d并附判件——附件 1）"),
("A16", "设原先错误、修复后正确的簇数为 G，原先正确、修复后错误的簇数为 L，则：新 P1 命中数 = 21 + G − L；达标要求 G − L ≥ 3。……必须逐簇分开填写 RUN5 的 P1 状态和 P2 状态，不能把两类残余混算。……\u201c至少净修复三个\u201d可以作为目标，尚不能作为有依据的预测。……P2 同样没有余量……\u201c属于预期\u201d不能成为超过 1/33 的豁免。",
 "注册包 §7 可达性算术模板（KB9 实况演算 21+4−3=22 自洽；逐簇 P1/P2 双列强制；目标非预测；P2 无余量）"),
("A17", "较准确的表述是：\u201c在当前数据、特征选择、证据装配和判读协议下未能稳定区分。\u201d……七个弃权/tie 位也应登记为待检验的失败机制假设",
 "注册包 §8-2/§8-3 + EDITORIAL_NOTE 第 3 条（\u201c生物学不可分\u201d表述收回）"),
("A18", "混合面审计中的\u201c视网膜簇中新条零进入\u201d，首先验证的是 applicability 的实现。……不能证明新条的 marker 具有独立的组织特异性。建议对这 22 个视网膜簇进一步要求 Arm2 与 Arm1 的完整 ranking 一致……同时将该审计明确称为适用性规则与回归检查。",
 "注册包 §8-4（正名+完整 ranking 一致性补查登记为下一波强制输出项，本包未跑，如实声明）"),
("A19", "OLS 回证验证的是细胞术语及 CL 身份，通常不能验证某个基因是该细胞的 marker。因此它应属于词条级命名证据……不能把 OLS、PMID、同源数据简单解释成三个独立支持来源。……冻结前还需明确：每条词条最少需要多少个合格核心基因、少于要求时如何处置；§1.2\u201c其余9互斥组\u201d究竟对应哪套参考分组；以及所有低于 MINPOOL 而未参与否决的比较组。TOPN=12 只是上限，免于否决的比较组也不能被记作已通过特异性验证。",
 "注册包 §8-5/§8-6（MINCORE=3+不足不成条；9 互斥组枚举+排除父组定义；免否决组=CornealEndo(432)组级+fire 审计 small-record 行全列；TOPN 上限语义+免否决组禁称已验证）"),
]

head = """【任务】KB9 眼表词条注册申请包 v2 —— REVIEWER_LLM 二审（逐条闭合判定 + 签发文本）。你是独立审稿人，无工具无文件访问；全部材料在本消息内。
【背景一句话】你（REVIEWER_LLM xhigh）上轮对 KB9 执行前设计裁定\u201c修订后再冻结\u201d，产出 19 条意见（接受 14 / 待 PI 5）。本轮这些接受项已重装为注册申请包 v2（其下 verbatim 全文），并对接受项逐条给出闭合位置与文本。KB9 build 已在原预注册下跑完（P1 FAIL 22/33 / P2 PASS 0/33，该结论不因审稿改判）；注册/接线/激活均等 PI，本包零执行。
【请裁定】对 14 个接受项逐条输出【闭合】或【未闭合：缺什么+最小修订】。随后给签发文本，三态其一：ACCEPTED（可送 PI 批注册）/ REVISE（列条目号+可执行修订）/ REJECTED（列根本原因）。另请裁两件事：(1) 附件 1 suprabasal 判件（§1.2 复算=逐字节复现过准入；KB7\u201c0 基因全过\u201d经原样重放+插桩定位为脚本父组归属实现缺陷的结构性假阴性）——判件结论是否可作 PI 去留决策的证据基础；(2) 若注册文档必须强制携带的\u201c残留限制\u201d措辞与你预期有出入，直接给出你要求的话术（不要转述）。
【信息差声明】下表摘录你的上轮意见原文（verbatim），随后 verbatim 全文为本包正文与判件。请对照原文判闭合，不接受自我声明。

"""

table = "## 闭合对照表（14 项）\n\n"
for cid, quote, pos in C:
    table += f"### {cid}\n- 上轮意见摘录：{quote}\n- 本轮闭合位置：{pos}\n\n"

body = table + """---
# 附件 0：注册包 v2 全文（verbatim）

""" + PKG + """

---
# 附件 1：suprabasal §1.2 复算判件（verbatim）

""" + SB + """

---
# 附件 2：KB9_BUILD_REPORT.md 文末 EDITORIAL_NOTE（verbatim；正文其余部分未动）

""" + NOTE + """

【输出格式】
一、逐条裁定：| # | 闭合/未闭合 | 一句话理由（未闭合须含最小修订）|
二、判件可采性裁定（一段）
三、残留限制措辞若有强制增补，逐条引号给出
四、签发文本：ACCEPTED / REVISE / REJECTED + 依据行
"""

OUT = f'{ROOT}/register/round2/REVIEWER_LLMROUND2_PROMPT.txt'
os.makedirs(os.path.dirname(OUT), exist_ok=True)
open(OUT, 'w', encoding='utf-8').write(head + body)
import hashlib
h = hashlib.sha256((head+body).encode()).hexdigest()
open(f'{ROOT}/register/round2/PROMPT_SHA256.txt','w').write(h + '\n')
print('PROMPT chars=', len(head+body), 'sha256=', h)
