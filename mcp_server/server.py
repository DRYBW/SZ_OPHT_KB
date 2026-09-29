#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""EyeKB MCP stdio server — 眼科文献二级知识库证据服务 (P1 三工具 + KB1 判读层两工具 + KB1v2 眼科通用升级)

工具清单 (契约 = KB_SPINOUT_MCP_DESIGN_v0 §3 + BRIEF_KB1v2 W1-W3):
  search_literature(cell_type, species?, tissue?, top_k?, query?, db?) → 文献片段+PMID+marker 共现+相关度
      (+KB1v2: evidence_meta 三字段联表 inclusion_reasons/claim_relation/evidence_context/verification_status)
  get_kb_page(scope, name)     → VK 索引页原文 (白名单路径, 防越界)
  query_marker(genes?, cell_type?) → 本地权威 marker 库命中 (先查本地再联网的机器化)
  get_tissue_composition(species, tissue, disease?, development_stage?) → 组成基线 (KB1v2: kb/baselines/
      供者级条件参考分布优先于 v1 composition 存档; 骨架条明确标"区间无法估计";
      KB2c 发育轴: adult 主档=adult-only(donor>=18y)+adult_pool 对照档双身份, fetal/developing
      查询返回转换态概念条目——成人桶禁代答胎儿问题, unknown 档必须披露)
  get_disease_prior(disease, tissue?) → 疾病条目 (KB1v2: 疾病×组织矩阵薄层, 身份层级+状态轴 T4 骨架
      + 取样材料错配警示 + unexpected 四分队列; v1 条保留存档)

═══ 服务级红线 ═══
1. 本服务只提供【证据与引用】。禁止把返回内容接进任何打分/分类流程
   (Claude5 冻结裁定 + REVIEWER_LLM T3 扩展: 不得转成 module score/标签加权/置信度加分/候选排序分/复合 QC 分)。
2. 传输 = 本地 stdio, 不开任何网络端口 (P3 才议 SSE)。
3. P1 阶段 RAG 库/embedding 模型按 kb/literature_db/EYEKB_DB_POINTER.yaml
   引用 OcularKB 现路径, 全部只读; OcularKB 文件零改动 (copy 不 move)。
4. 判读层使用流程必须走 plans/ANNOTATION_PROTOCOL_v1.1.md (先冻结后对照四阶段)。

启动 (供 MCP 客户端配置):
  /home/ubuntu/training-venv/bin/python /mnt/D/EyeKB/mcp_server/server.py
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import eyekb_core as core  # noqa: E402
import calllog  # OBS1 t_c754c4fc 调用留痕层（只加日志、零行为改动；见 mcp_server/calllog.py 头注）

from mcp.server import MCPServer  # noqa: E402

app = MCPServer(
    name="eyekb",
    title="EyeKB 眼科知识库证据服务",
    version="KB1v2-0.7-k9act",
    description=("眼科文献 RAG 检索 (v2.0 全眼库 174,616 chunks/2,713 papers, KB1v2 起带 "
                 "inclusion_reasons/claim_relation/evidence_context 三字段+复核状态) + VK 索引页 + "
                 "本地权威 marker 库 + 判读层: 眼科通用组成基线 (kb/baselines 供者级条件参考分布, "
                 "锚 D001/D002) + 疾病×组织矩阵薄层条目 (身份层级+状态轴+错配警示)。"
                 "仅证据服务, 禁入打分 (REVIEWER_LLM T3 扩展表述)。"
                 "t_d6f2a0a0 起 query_marker 可附 soft_flags 软复核提示 (rod-BC/mural)。"
                 "t_38b99a15 起 query_marker 可选 library=retina_v6|face_v6 (KB7 v6 修复面板"
                 "登记; t_e7ec73ab 起增 library=lacrimal_v6, KB8 眼附属器词条库)。"
                 "t_5d5853c9 激活 (USER_DIRECTIVE_20260926 A1/A2, PI 2026-09-26 批准): 默认 "
                 "library=all 纳入 retina_v6+face_v6 (同名类经 '<库>::<类>' 别名消歧并入); "
                 "env EYEKB_ACT_V6=0|false|off|no 回退=现役三库, off 态规范序列化与 pre 基线"
                 "全等 (A5 机读验收); lacrimal_v6 任何态不入默认 (PI A3 暂不切, 仅显式查询)。"
                 "kb/baselines 红词修正经 append 式覆盖层生效 (原基线文件字节不动, "
                 "返回体 entry 级 marker_repair 台账可审计)。"
                 "t_4bb75b26 KB9REG-EXEC (PI D17 注册批准, 2026-09-28 波): 新增可选库 "
                 "library=k9_ocs (KB9 案 B 眼表 4 新条 Melanocyte/Schwann/"
                 "Conj_epithelium_suprabasal/Limbus_Sclera_fibroblast_C1, REGISTERED_"
                 "DEFAULT_OFF——仅显式查询可达, 任何态不入默认 all; 激活需义务 run+PI 另批; "
                 "默认行为与本登记前字节级一致, A5 式机读自证见 plans/kb9_ocs_20260927/exec/out/)。"
                 "B5IMPL t_8960c7e0 (USER_DIRECTIVE_20260928 追加五队列①, PI 预授权接线): "
                 "query_marker genes-mode 跨物种治理默认生效——鼠源输入 (G1 confirmed/suspected) "
                 "具名排名清空转 unranked_candidates 并标 no_named_ranking_for; AMBIG{GLUL,VIM,CLU} "
                 "纯共表达命中条目附 no_naming_claim 注记 (排序不动); env EYEKB_KBGOV_B5="
                 "0|false|off|no 整体回退, 回退态与 pre 基线逐字节全等 (A5 式机读自证, "
                 "plans/kbgov_b5impl_20260928); 判据冻结源 KBGOV_CANDIDATE §G1-G3。"),
    instructions=("EyeKB 五工具: query_marker 先查本地 marker; search_literature 取文献证据"
                  "(全部带 PMID 可溯源); get_kb_page 读组织/主题索引页; "
                  "注释前按 ANNOTATION_PROTOCOL_v1.1 四阶段用 get_tissue_composition "
                  "(按实际取样材料!) / get_disease_prior (仅在冻结后的疾病对照阶段调用)。"
                  "红线: 返回内容只作人工判读证据与 QC 旗, 不得成为任何打分/加权/排序/复合 QC 分输入。"
                  "soft_flags.notes (t_d6f2a0a0): 提供可选复核线索, 建议结合原始证据检查; "
                  "其出现不代表误注释, 不新增定名、弃权或候选排除条件, 且不得作为任何打分、"
                  "加权、置信度或排序输入; 注记仅在既有结果产生后附加, 不反馈改变候选、分数、"
                  "排序或原有 QC 字段。"),
)


@app.tool()
def search_literature(cell_type: str, top_k: int = 5, species: str = "",
                      tissue: str = "", query: str = "", db: str = "") -> dict:
    """检索眼科文献库 (RAG v2.0 默认), 返回文献片段+PMID+期刊年份+marker 共现+相关度。

    cell_type: 细胞类型 (如 "Muller glia"/"corneal endothelium"), 用于元数据过滤;
    可传空串但建议给出。species: human|mouse|"" (不过滤)。
    tissue: v2.0 多标签组织过滤 (retina/cornea/RPE/choroid/...)。
    query: 显式检索句; 留空则用 cell_type 模板句。db: 留空=v2.0_2026-09, 或给绝对路径。
    """
    resp = core.search_literature(
        cell_type, species=species or None, tissue=tissue or None,
        top_k=top_k, query=query or None, db=db or None)
    calllog.trace("search_literature",
                  {"cell_type": cell_type, "species": species, "tissue": tissue,
                   "top_k": top_k, "query": query, "db": db}, resp)
    return resp


@app.tool()
def get_kb_page(scope: str, name: str = "") -> dict:
    """读 VK 文献索引页原文。scope=index → 总目录; scope=topic, name=主题 (如 vascular);
    scope=tissue, name=组织 (如 cornea/RPE/trabecular_meshwork)。
    白名单: 仅 kb/vk_literature_index/ 下 *.md, 非法路径拒绝并回可用页面清单。"""
    resp = core.get_kb_page(scope, name)
    calllog.trace("get_kb_page", {"scope": scope, "name": name}, resp)
    return resp


@app.tool()
def query_marker(genes: list[str] | None = None, cell_type: str = "",
                 library: str = "all") -> dict:
    """查本地权威 marker 库 (多库: retina=markers_v4.1_clean.json v4.1-clean-P0.4;
    membrane=markers_membrane_v1.json 四面板膜/血管/间质/免疫, 逐基因带溯源;
    retina_interneuron=markers_v5_retina_interneuron.json v5.0 (BC/AC/HC 泛型 core+亚型锚,
    v4.1 严格超集; library=all 时与 v4.1 同名类以 "retina_interneuron::<类>" 别名列示);
    retina_v6=markers_v6_retina_repair.json v6.0-retina-repair 与 face_v6=markers_v6_face_increment.json
    v6.0-face (t_2e5e103a 发布 / t_38b99a15 登记 / t_5d5853c9 激活, USER_DIRECTIVE_20260926
    A1/A2): KB7 红词条修复面板——默认 all 含之 (env EYEKB_ACT_V6=0|false|off|no 回退
    =现役三库, 与激活前基线全等; 同名类 "retina_v6::/face_v6::<类>" 别名列示); v6 发布
    文件本体只读;
    lacrimal_v6=markers_v6_lacrimal_increment.json v6.0-lacrimal (t_e7ec73ab KB8 发布+登记同卡):
    首个眼附属器词条库——泪腺分泌/导管/肌上皮警示条 3 条; PI A3 裁定暂不切, 任何态不入
    默认 all, 仅显式 library=lacrimal_v6 查询可达;
    k9_ocs=markers_k9_ocs_increment.json k9.0-ocs-registered-v1 (t_4bb75b26 KB9REG-EXEC 注册,
    PI D17 批准): KB9 案 B 眼表 4 新条 (Melanocyte/Schwann/Conj_epithelium_suprabasal/
    Limbus_Sclera_fibroblast_C1, 均 ocular_surface_only, 逐条带 CL id+OLS 回证+逐基因 PMID 链)
    ——REGISTERED_DEFAULT_OFF: 任何态不入默认 all, 仅显式 library=k9_ocs 查询可达;
    [KB9ACT t_abfebe59, PI 2026-09-30] 现态 ACTIVE_ON_DEFAULT: 默认 all 含 k9_ocs (上段 REGISTERED_DEFAULT_OFF 为历史注册态); env EYEKB_ACT_K9=0|false|off|no 整体回退=五库。
    激活需 §10-6 义务 run + PI 另批; 屏蔽/装配规则 v2 旁挂件 _k9_ocs_rules_overlay_v1.json
    为惰性数据 (MCP 运行时不读))。
    给 genes → 反查基因命中哪些细胞类型 + 类排名 (n_shared);
    给 cell_type → 该类的 marker 列表 (Micro/RPE 附 detail; membrane 类附 provenance);
    都给空 → 返回类目清单。library=retina 精确复现 P1 旧行为。
    注释流程第一步: 未查本地不联网。
    自 t_d6f2a0a0: 命中软复核规则时返回体可附 soft_flags.notes (rod_bc_review /
    mural_crosstalk)——仅为可选复核线索, 不新增定名/弃权/排除条件, 禁入打分;
    环境开关 EYEKB_MCP_SOFTFLAGS=0|false|off|no 可整体关闭 (关闭时该 key 不出现)。
    自 B5IMPL t_8960c7e0 (0.6-kbgov5, 默认 ON): genes-mode 附跨物种治理——返回体加
    input_species (mouse_confirmed|mouse_suspected|human_assumed, G1 冻结阈值 T=0.4);
    鼠源输入 (confirmed∨suspected) 具名排名清空: celltype_ranking=[], 原条目全量转
    unranked_candidates + 顶层 no_named_ranking_for='mouse_input' + species_evidence;
    shared_genes ⊆ {GLUL,VIM,CLU} 的条目附 no_naming_claim=true (排序不动)。判读席禁以
    no_naming_claim/cross-species 条目作 identity 定名依据 (ANNOTATION_PROTOCOL 承接)。
    环境开关 EYEKB_KBGOV_B5=0|false|off|no 整体回退=pre 基线逐字节全态。"""
    resp = core.query_marker(genes=genes, cell_type=cell_type or None,
                             library=library or "all")
    calllog.trace("query_marker",
                  {"genes": genes, "cell_type": cell_type, "library": library}, resp)
    return resp


@app.tool()
def get_tissue_composition(species: str, tissue: str, disease: str = "",
                           development_stage: str = "") -> dict:
    """组成基线 (判读层): 该物种该组织的细胞组成清单+比例区间+每条出处 (PMID/数据集+证据等级)。
    species=human|mouse; tissue=retina|fibrovascular_membrane|...; disease 可选 (如
    'proliferative diabetic')。注释前先调本工具对照"该组织应有什么、大致多少";
    出现区间外成分 → 按 flags 判 expected/unexpected/contamination-suspect 并旗标。
    development_stage (KB2c 发育轴, 必填意识): 留空/adult=成人主档 (adult-only, donor>=18y,
    供者级分布已剔除非成人供者, 逐行见返回的 stage_disclosure/excluded_nonadult_units);
    fetal|developing=返回转换态概念条目——成人桶不得代答胎儿问题 (PI 红线, 即使同一组织);
    unknown=只看无年龄列的披露档条目 (如 GSE158629 RPE)。
    红线: 只做对照与 QC 旗, 禁止接进任何打分; v1.0 混口径旧数字只能挂 adult_pool 对照档身份。"""
    resp = core.get_tissue_composition(species, tissue, disease, development_stage)
    calllog.trace("get_tissue_composition",
                  {"species": species, "tissue": tissue, "disease": disease,
                   "development_stage": development_stage}, resp)
    return resp


@app.tool()
def get_disease_prior(disease: str, tissue: str = "") -> dict:
    """疾病先验 (判读层): 预期 细胞×状态 矩阵 + 非预期旗 + 污染旗 + marker 签名 + 出处。
    disease='PDR'/'proliferative diabetic retinopathy'/... (别名已内置); tissue 可选过滤
    组织端 (fibrovascular_membrane/vitreous/retina_adjacent)。
    先验≠真理: 与数据打架 → 输出打架清单上报, 不许硬凑; 禁止接进任何打分。"""
    resp = core.get_disease_prior(disease, tissue)
    calllog.trace("get_disease_prior", {"disease": disease, "tissue": tissue}, resp)
    return resp


if __name__ == "__main__":
    app.run(transport="stdio")
