#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""KB9REG-A06: R1 逐条 条目ID—组织适用范围表（由实跑遮蔽表+词条库机械生成，零 LLM）。
输入只读: out/kb9_shared_gene_shield.tsv (R1 行=条目ID权威清单) + kb/markers_*.json (类清单) + mcp_server MARKER_LIBS 映射。
输出: register/A06_R1_ITEM_SCOPE_TABLE.tsv
"""
import json, csv

ROOT = '/mnt/D/EyeKB/plans/kb9_ocs_20260927'
import sys
sys.path.insert(0, '/mnt/D/EyeKB/mcp_server')
import eyekb_core as C

FILE_OF_LIB = {n: str(p).split('/')[-1] for n, p in C.MARKER_LIBS.items()}
RETINA_ONLY_FILES = {'markers_v4.1_clean.json', 'markers_v5_retina_interneuron.json', 'markers_v6_retina_repair.json'}
LIB_ORDER = ['retina', 'membrane', 'retina_interneuron', 'retina_v6', 'face_v6', 'lacrimal_v6']

# 类→出现文件 倒排
cls_files = {}
for n in LIB_ORDER:
    db = json.load(open(str(C.MARKER_LIBS[n]), encoding='utf-8'))
    markers = db.get('markers') or {}
    if not markers and 'stromal_repair' in db:  # face_v6 derived
        for src in ('stromal_repair', 'face_increment'):
            for cls, e in (db.get(src) or {}).items():
                markers.setdefault(cls, e.get('core') or [])
    for cls in markers:
        cls_files.setdefault(cls, []).append(FILE_OF_LIB[n])

def owner_of(cls_key):
    """消歧键 → owner 文件（首载=bare 名，后到=lib::class）"""
    if '::' in cls_key:
        lib, cls = cls_key.split('::', 1)
        return FILE_OF_LIB.get(lib, cls_key)
    fs = cls_files.get(cls_key, [])
    return fs[0] if fs else 'UNKNOWN'

# 生物学依据（逐条理由 = 组织解剖学 + 细胞身份口径；禁以"D002 标签缺席"充当排除依据）
REASON = {
    'Rod': '视杆光感受器：组织解剖学上仅存在于视网膜神经层（marker 身份锚 RHO/NRL/NR2E3），角膜/limbus/巩膜/结膜无此细胞层，该条 scope=retina_only：眼表面材料证据装配不计入其 kb_marker_ranking（对命中来源不作穷尽断言）',
    'Cone': '同 Rod（视锥光感受器，仅视网膜外神经层）',
    'BC': '双极细胞：视网膜内神经元，仅存在于视网膜内神经层，眼表面组织无该层',
    'AC': '无长突细胞：视网膜内神经元，同上',
    'HC': '水平细胞：视网膜内神经元，同上',
    'RGC': '神经节细胞：视网膜输出神经元，胞体位于视网膜神经节细胞层（眼球后极），角膜/limbus/巩膜/结膜 portal 取材范围不含该层',
    'MG': '细胞身份=Müller 胶质（v4.1 基因锚 RLBP1/GLUL/SOX9/S100B；冻结 crosswalk 别名注=Müller glia 视网膜特有）：视网膜专属巨胶质，眼表面组织无 Müller 细胞',
    'Astro': '细胞身份=星形胶质（v4.1 基因锚 GFAP/AQP4/SLC1A3；冻结 crosswalk 别名注=astrocyte 视网膜/中枢）：视网膜内星形胶质，与眼表面组织学细胞群不同实体；RUN5 实证 Q6::13/22/16 被 MG|Astro 接管即此二类',
    'Micro': '细胞身份=microglia（v4.1 基因锚 C1QB 等小胶质标志）：CNS 常驻巨噬谱系词条；眼表面髓系信号由 Macrophages/Monocytes 词条承载（其 kept 行为见遮蔽表），本条在眼表面装配中不计入排名',
    'RPE': '视网膜色素上皮（基因锚 BEST1/RPE65 类/LRAT/RDH5/MITF）：单层色素上皮位于视网膜侧，与角膜/结膜上皮不同胚胎起源（神经外胚层诱导 vs 表面外胚层），组织解剖学上不在眼表面 portal 取材层',
}

# 遮蔽表 R1 行 = 实跑条目 ID 权威清单
ids = []
with open(f'{ROOT}/out/kb9_shared_gene_shield.tsv') as f:
    hdr = f.readline().rstrip('\n').split('\t')
    for line in f:
        p = line.rstrip('\n').split('\t')
        if len(p) >= 3 and p[2] == 'R1_drop_retina_specific' and p[1] == '*':
            ids.append(p[0])

rows = []
for eid in ids:
    cls = eid.split('::', 1)[1] if '::' in eid else eid
    own = owner_of(eid)
    files = cls_files.get(cls, [])
    dup_note = ('跨文件重复条目 %d 份 (%s)，本表逐条目独立登记；生物学 scope 同源一致，处置=整组同退（无保留份）'
                % (len(files), '|'.join(files))) if len(files) > 1 else '单文件条目'
    rows.append({
        'entry_id': eid, 'class': cls, 'owner_file_firstload': own, 'all_files_carrying_class': '|'.join(files),
        'scope': 'retina_only → 眼表面(ocular_surface)证据装配不计入 kb_marker_ranking',
        'bio_reason': REASON.get(cls, '未登记'), 'dup_handling': dup_note,
        'impl_note': '排除依据=条目生物学分型（REVIEWER_LLM §2 R1 改法落地：文件仅为实现索引，不单独充当生物学依据）',
    })

OUT = f'{ROOT}/register/A06_R1_ITEM_SCOPE_TABLE.tsv'
with open(OUT, 'w') as f:
    w = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t')
    w.writeheader(); w.writerows(rows)

# 反向适用性（KB9 新条）——同表追加区块说明行
rev = [
    {'entry_id': 'Melanocyte (KB9 build)', 'class': 'Melanocyte', 'owner_file_firstload': 'markers_k9_ocs_increment.json (build)',
     'all_files_carrying_class': 'build only（未注册）',
     'scope': 'ocular_surface_only → 视网膜材料不计入（R1 镜像；火灾审计格二规则臂实证泄漏 0）',
     'bio_reason': '眼表黑色素细胞词条 marker（TRPM1 等）在视网膜双极/杆体语境有真表达（火灾审计无规则臂实测 2/22 簇泄漏），须适用性隔离',
     'dup_handling': '单文件条目', 'impl_note': '注册后禁全库默认态混用（BUILD_REPORT §4 口径）'},
    {'entry_id': 'Schwann (KB9 build)', 'class': 'Schwann', 'owner_file_firstload': 'markers_k9_ocs_increment.json (build)',
     'all_files_carrying_class': 'build only（未注册）',
     'scope': 'ocular_surface_only → 视网膜材料不计入',
     'bio_reason': 'MPZ/SCN7A 等在有髓神经相关组织共享；视网膜节细胞轴突段（视神经头）语境存在误入风险',
     'dup_handling': '单文件条目', 'impl_note': '同上'},
    {'entry_id': 'Conj_epithelium_suprabasal (KB9 build)', 'class': 'Conj_epithelium_suprabasal',
     'owner_file_firstload': 'markers_k9_ocs_increment.json (build)', 'all_files_carrying_class': 'build only（未注册）',
     'scope': 'ocular_surface_only → 视网膜材料不计入',
     'bio_reason': 'S100A8/9 髓系共享表达（见 recheck/判件），适用性隔离为前提',
     'dup_handling': '单文件条目', 'impl_note': '去留待 PI（A15 子项判件 register/SUPRABASAL_RECHECK.md）'},
    {'entry_id': 'Limbus_Sclera_fibroblast_C1 (KB9 build)', 'class': 'Limbus_Sclera_fibroblast_C1',
     'owner_file_firstload': 'markers_k9_ocs_increment.json (build)', 'all_files_carrying_class': 'build only（未注册）',
     'scope': 'ocular_surface_only → 视网膜材料不计入',
     'bio_reason': 'DPT/LEPR/LAMA2 为眼表间质域；防泛间质回渗视网膜簇',
     'dup_handling': '单文件条目', 'impl_note': '同上'},
]
with open(OUT, 'a') as f:
    w2 = csv.DictWriter(f, fieldnames=list(rows[0].keys()), delimiter='\t')
    w2.writerows(rev)
print('WROTE', OUT, 'rows:', len(rows) + len(rev))
