#!/usr/bin/env python3
"""D0 evidence claims extractor — verbatim MUST be exact substrings of chunk text.
Probe (exact substring) locates the chunk; extraction takes the sentence(s)
containing the probe. Output: d0_claims_draft.json for review before finalizing."""
import json, re, sys

d0 = json.load(open('d0_chunks.json'))
by_pmid = {}
for c in d0:
    by_pmid.setdefault(c['paper_id'], []).append(c)

def find_chunk(pmid, probe):
    hits = [c for c in by_pmid[pmid] if probe in c['text']]
    if len(hits) == 0:
        raise SystemExit(f"[PROBE-NOT-FOUND] pmid={pmid} probe={probe!r}")
    return hits[0]

def sentences(text):
    # split on sentence-final punctuation followed by space; keep delimiters
    parts = re.split(r'(?<=[.!?])\s+', text)
    return parts

def extract_sentence(pmid, probe, n_sent=1, sent_offset=0):
    """Return exact contiguous slice: the n_sent sentence(s) starting at sent_offset
    before? No: sentence containing probe, extended forward by n_sent-1."""
    ch = find_chunk(pmid, probe)
    sents = sentences(ch['text'])
    idx = [i for i, s in enumerate(sents) if probe in s]
    if not idx:
        raise SystemExit(f"[SENT-NOT-FOUND] {probe!r}")
    i = idx[0] + sent_offset
    out = ' '.join(sents[i:i+n_sent])
    # verify exact substring of chunk (join with single space may differ from source)
    if out not in ch['text']:
        # fallback: locate start and end via first/last sentence fragments
        start = ch['text'].find(sents[i])
        end = ch['text'].find(sents[i+n_sent-1], start) + len(sents[i+n_sent-1])
        out = ch['text'][start:end]
    assert out in ch['text'], f"[SLICE-FAIL] {probe!r}"
    wc = len(out.split())
    return {'section': ch['section'], 'chunk_type': ch['chunk_type'], 'verbatim': out, 'words': wc}

# ---- claim definitions (pmid, probe, n_sent, sent_offset) ----
CLAIMS = [
 # 35061025 Hu et al. Diabetes 2022 (GSE165784 original paper, abstract only)
 dict(id='D0C-001', pmid='35061025', inclusion_reason='data_anchor', claim_relation='supports',
      kb_target='GSE165784V2', probe='we used single-cell RNA sequencing on surgically harvested PDR-FVMs',
      limitation='Abstract-only evidence (full_text_available=0, OA_fail/no PMCID): claims limited to what the abstract states; sample n and exact cell counts not auditable at claim level.'),
 dict(id='D0C-002', pmid='35061025', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#myeloid', probe='Eight cellular compositions were identified',
      limitation='"Major cell population" is per this paper\'s own annotation of FVM dissociates; independent datasets disagree on microglial vs macrophage identity (cf. D0C-011 refutes-annotation); PDR-only denominator not given in abstract.'),
 dict(id='D0C-003', pmid='35061025', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#myeloid_states.foam_DAM_LAM', probe='We identified a GPNMB+ subpopulation of microglia',
      limitation='Abstract-level statement; GPNMB+ state attribution to "microglia" (vs monocyte-derived macrophage) is this paper\'s annotation choice, contested by other D0 papers.'),
 dict(id='D0C-004', pmid='35061025', inclusion_reason='background', claim_relation='qualifies',
      kb_target='human_pdr_membrane#myeloid_states', probe='Pseudotime analysis further revealed the profibrotic microglia was uniquely differentiated',
      limitation='Pseudotime inference from scRNA-seq only — no lineage tracing; trajectory direction not provable from snapshot data; abstract-only source.'),
 dict(id='D0C-005', pmid='35061025', inclusion_reason='background', claim_relation='context_only',
      kb_target='PDR__fibrovascular_membrane', probe='Ligand-receptor interactions between the profibrotic microglia and cytokines',
      limitation='Pathway list (CCR5/IFNGR1/CD44) is inferred ligand-receptor analysis on vitreous cytokines, not experimentally validated in the abstract; abstract-only source.'),
 # 41578023 HRCA (abstract only)
 dict(id='D0C-006', pmid='41578023', inclusion_reason='data_anchor', claim_relation='supports',
      kb_target='baseline_human_retina', probe='We compiled around 3.9 million cells from 125 donors',
      limitation='Abstract-only evidence; atlas is multistudy (8 published + unpublished 2.7M cells) so per-donor composition of any query cluster is not uniform; OA_fail deviation registered in d0_admission.json.'),
 dict(id='D0C-007', pmid='41578023', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='baseline_human_retina', probe='We annotated each cluster, identified marker genes',
      limitation='Marker/regulatory annotation is atlas-level consensus; low-support cell types (e.g. rare immune states) inherit batch/annotation uncertainty; abstract-only source.'),
 dict(id='D0C-008', pmid='41578023', inclusion_reason='background', claim_relation='context_only',
      kb_target='baseline_human_retina', probe='We modeled changes in gene expression and chromatin accessibility across age',
      limitation='Covariate modeling stated in abstract without effect sizes; "tissue region" is macula/peripheral-like axis, not disease state; abstract-only source.'),
 # 37917183 JCI Insight AEBP1
 dict(id='D0C-009', pmid='37917183', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#major_compartments', probe='we identified 6 different clusters',
      limitation='n=4 patient samples, single surgical series (GSE245561); cluster count differs from GSE165784 re-analyses (16-17 clusters) — resolution/division-of-work differences.'),
 dict(id='D0C-010', pmid='37917183', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#stromal_pericyte+stromal_myofibro', probe='intermediate cluster between pericytes',
      limitation='Transdifferentiation inferred from clustering/trajectory, not lineage tracing; AEBP1 functional validation is in vitro HRP cells, not membrane tissue.'),
 dict(id='D0C-011', pmid='37917183', inclusion_reason='contradicting_evidence', claim_relation='refutes',
      kb_target='human_pdr_membrane#myeloid', probe='none of the inflammatory cells expressed microglia markers', head_trim=5,
      limitation='Absence-of-evidence on TMEM119/P2RY12 in their own 4-sample dataset (homeostatic microglia markers can be lost upon activation/dissociation); refutes the microglial *identity* label, not the myeloid-dominant composition itself.'),
 dict(id='D0C-012', pmid='37917183', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#myeloid_states.foam_DAM_LAM', probe='we identified a cluster of macrophages,',
      limitation='SPP1+ macrophage subcluster quantified per their own annotation; "proangiogenetic" is gene-expression-inferred, no functional angiogenesis assay for this exact cluster in the cited passage.'),
 dict(id='D0C-013', pmid='37917183', inclusion_reason='data_anchor', claim_relation='context_only',
      kb_target='human_pdr_membrane', probe='scRNA-Seq data are uploaded to NCBI GEO', frag='scRNA-Seq data are uploaded to NCBI GEO database under accession no.  GSE245561',
      limitation='Data anchor provenance record only (GSE245561); this card\'s A-grade composition numbers do NOT use GSE245561.'),
 # 39220810 Ophthalmology Science vitreous T cells
 dict(id='D0C-014', pmid='39220810', inclusion_reason='core_reference', claim_relation='qualifies',
      kb_target='human_pdr_membrane', probe='Most vitreous cells were T cells (91.6%)',
      limitation='Compartment = cell suspension from cassette washings of vitreous LIQUID (n=5 patients/6 eyes), not digested fibrovascular membrane — T-cell dominance qualifies but does not contradict FVM myeloid-dominance (different compartments).'),
 dict(id='D0C-015', pmid='39220810', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='Clustering revealed 4 cell states', frag='Clustering revealed 4 cell states: T cells, B cells, myeloid, and neutrophils',
      limitation='Only 4 broad states after QC (13,675 cells); B/neutrophil subclusters too sparse for subtype analysis in some eyes, per the paper.'),
 dict(id='D0C-016', pmid='39220810', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='interactions between myeloid cells and T cells or dendritic',
      limitation='Ligand-receptor inference (Dimer Signal Receptor Analysis), not experimental perturbation; vitreous-vs-PBMC comparison constrained by n=5 patients.'),
 dict(id='D0C-017', pmid='39220810', inclusion_reason='background', claim_relation='context_only',
      kb_target='proliferative_DR', probe='In the first single-cell transcriptomic characterization of human vitreous', head_trim=1,
      limitation='Conclusion-section framing statement; "liquid biopsy" refers to cassette washings, protocol not standardized across centers at time of publication.'),
 dict(id='D0C-018', pmid='39220810', inclusion_reason='core_reference', claim_relation='qualifies',
      kb_target='PDR__fibrovascular_membrane', probe='A total of 5 of the 6 eyes had received',
      limitation='Prior anti-VEGF/PRP treatment may reshape immune composition — composition numbers are treatment-confounded (paper\'s own cohort table).'),
 # 40069725 MKI67+ microglia (re-analyzes GSE165784)
 dict(id='D0C-019', pmid='40069725', inclusion_reason='data_anchor', claim_relation='supports',
      kb_target='GSE165784V2', probe='Gene expression matrix data',
      limitation='Independent re-analysis of GSE165784 confirms 5 FVM samples from PDR patients as the dataset scope; their QC (UMI 200-3000, MT>10%) and cell yield (7,764) differ from our Track B (10,069 cells) — anchor to dataset identity, not to numbers.'),
 dict(id='D0C-020', pmid='40069725', inclusion_reason='method_anchor', claim_relation='context_only',
      kb_target='GSE165784V2', probe='Stringent quality control measures were applied to exclude low-quality cells',
      limitation='Third-party QC recipe for GSE165784 (UMI bounds + MT filter) — method anchor for sensitivity checks only; not adopted by Track B.'),
 dict(id='D0C-021', pmid='40069725', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#myeloid_states', probe='delineate a novel microglial subset, designated as', frag='this investigation is the first to delineate a novel microglial subset, designated as MKI67 +  microglia, distinguished by robust upregulation of genes implicated in lactate metabolic processes and proliferation, such as MKI67, PARK7 and LDHA',
      limitation='"Microglia" label here is marker-based on GSE165784 re-analysis; subset defined post-hoc via LMG intersection; proliferation (MKI67) signature could also reflect infiltrating myeloid cycling cells.'),
 dict(id='D0C-022', pmid='40069725', inclusion_reason='background', claim_relation='qualifies',
      kb_target='human_pdr_membrane#myeloid_states', probe='microglial cells (markers: CENPF', frag='microglial cells (markers: CENPF, CX3CR1, SELENOP, HIST1H1B, GPNMB, FABP5, MRC1, and LIPA)',
      limitation='Their microglia marker panel (SELENOP/MRC1/GPNMB...) overlaps heavily with states our Track B annotates as macrophage — evidences that MG-vs-Mac annotation in FVM is panel-dependent, not data-determined.'),
 dict(id='D0C-023', pmid='40069725', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='This unique cell type promotes angiogenesis by interacting with endothelial cells',
      limitation='SPP1-ITGA4 pair from CellPhoneDB inference + conditioned-medium co-culture (in vitro); mouse OIR arm supports drug effect, not the human cell state directly.'),
 dict(id='D0C-024', pmid='40069725', inclusion_reason='background', claim_relation='context_only',
      kb_target='proliferative_DR', probe='treatment with abemaciclib, a FDA-approved proliferation inhibitor, significantly reduced neovascularization',
      limitation='Mouse OIR model (P12-P17 i.p. abemaciclib), not PDR human tissue; translational gap acknowledged — no human efficacy data in this paper.'),
 # 40562775 Sirt3 FAO niche
 dict(id='D0C-025', pmid='40562775', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='proliferative_DR', probe='we observed an accumulation of acylcarnitines', frag='we observed an accumulation of acylcarnitines in human neovascular PR samples compared to control subjects with epiretinal membranes',
      limitation='Human evidence = vitreous metabolomics (PDR vs ERM controls, pre-2017 collection, n per Suppl Table 1); acylcarnitine accumulation is niche-level, not cell-type-resolved.'),
 dict(id='D0C-026', pmid='40562775', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='Neovascular tufts with a distinct single-cell transcriptional signature highly expressed FAO enzymes',
      limitation='Tuft EC signature from mouse OIR CD31-enriched Drop-seq (GSE216676), not human FVM endothelium — cross-species transfer is this paper\'s hypothesis, supported only by the metabolite match (D0C-028).'),
 dict(id='D0C-027', pmid='40562775', inclusion_reason='core_reference', claim_relation='qualifies',
      kb_target='PDR__fibrovascular_membrane', probe='shifted the neovascular niche metabolism from FAO to glycolysis',
      limitation='Global Sirt3-/- mouse (also AAV-GFAP-Cre conditional arm); mechanism is niche-level metabolic reprogramming — tuft suppression shown in OIR, not in diabetic human retina.'),
 dict(id='D0C-028', pmid='40562775', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='proliferative_DR', probe='we observed comparable FAO metabolite signatures in both human diabetic PR and murine OIR samples',
      limitation='Discussion-level comparison of metabolite classes; "shared metabolic dysregulation" remains associative (different etiologies, different readouts: human vitreous vs mouse retinal acylcarnitines).'),
 dict(id='D0C-029', pmid='40562775', inclusion_reason='background', claim_relation='qualifies',
      kb_target='proliferative_DR', probe='Poor glucose control in diabetics and extreme prematurity in neonates correlate with neovascular retinal disease in humans but not in mice',
      limitation='Paper\'s own model-limitation admission — applies to all OIR-derived claims used for human PDR inference (incl. D0C-026/027).'),
 # 42601615 SOX15 atlas
 dict(id='D0C-030', pmid='42601615', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='generating a single-cell transcriptomic atlas of the human PDR retina', head_trim=1,
      limitation='Atlas scope = post-mortem donor RETINA tissue (2 PDR donors/4 retinas + 3 controls/6 retinas), a different compartment from surgically harvested FVM; FVM only used in IF validation arms.'),
 dict(id='D0C-031', pmid='42601615', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='human_pdr_membrane#stromal_myofibro', probe='We identified a stromal cell population that was enriched in PDR retinas, localized in FVMs',
      limitation='SOX15-high stromal subpopulation defined in their own PDR retinal atlas (n=2 PDR donors; 80.6% of stromal cells from one donor PDR2 per their Fig.); FVM localization by IF on 3 samples.'),
 dict(id='D0C-032', pmid='42601615', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='PDR__fibrovascular_membrane', probe='SOX15 regulates EDN1 transcription through binding to its promoter',
      limitation='Mechanism chain: ChIP-seq/qPCR + luciferase (in vitro/overexpression) + Sox15-dFIB mouse laser-fibrosis model; human evidence is correlative at tissue level.'),
 dict(id='D0C-033', pmid='42601615', inclusion_reason='background', claim_relation='qualifies',
      kb_target='human_pdr_membrane', probe='prior scRNA-seq studies of PDR have focused on FVM tissues surgically retrieved during vitrectomy',
      limitation='Explicit compartment distinction from Discussion — supports treating FVM-derived composition priors as membrane-scope, not retina-scope.'),
 dict(id='D0C-034', pmid='42601615', inclusion_reason='background', claim_relation='supports',
      kb_target='human_pdr_membrane', probe='One landmark study identified eight cellular populations in FVMs with microglia as the dominant cell type',
      limitation='Third-party recount of Hu 2022 (GSE165784): "microglia dominant" and mesenchymal 8.2% are as-annotated by that study — quoted here as provenance context, not independently re-derived.'),
 dict(id='D0C-035', pmid='42601615', inclusion_reason='core_reference', claim_relation='supports',
      kb_target='proliferative_DR', probe='the absence of non-proliferative diabetic retinopathy (NPDR) samples in our scRNA-seq cohort',
      limitation='Self-declared limitation: disease-stage gradient (NPDR->PDR) not covered by their atlas; photoreceptor subpopulation claims (MT-enriched rods, S-cones loss) rest on n=2 PDR donors.'),
]

out=[]
for cl in CLAIMS:
    probe = cl.get('probe_hint', cl['probe'])
    if 'frag' in cl:
        ch = find_chunk(cl['pmid'], cl['frag'])
        r = {'section': ch['section'], 'chunk_type': ch['chunk_type'], 'verbatim': cl['frag'], 'words': len(cl['frag'].split())}
    else:
        n_sent = 1
        r = extract_sentence(cl['pmid'], probe, n_sent)
    cl2 = dict(cl)
    cl2.pop('probe_hint', None)
    ht = cl.get('head_trim', 0)
    if ht:
        words = r['verbatim'].split(' ')
        r['verbatim'] = ' '.join(words[ht:])
        r['words'] = len(r['verbatim'].split())
        # re-verify literal
        ch = find_chunk(cl['pmid'], r['verbatim'])
    cl2.pop('head_trim', None)
    cl2['extracted'] = r
    out.append(cl2)
    print(f"{cl['id']} [{cl['pmid']}] w={r['words']:3d} sec={r['section'][:40]:40s} | {r['verbatim'][:80]}...")
    if r['words'] > 50:
        print("   *** OVER 50 WORDS ***")

json.dump(out, open('d0_claims_draft.json','w'), ensure_ascii=False, indent=1)
print("\nsaved", len(out), "draft claims -> d0_claims_draft.json")
