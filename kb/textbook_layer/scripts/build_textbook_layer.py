#!/usr/bin/env python3
"""Build the textbook layer from the textbook extraction.

Output : TEXTBOOK_ITEMS_v1.jsonl      - one row per item, English, no host paths
         LAYER_REGION_VOCAB_v1.json   - the layer / region / membrane vocabulary, by kind
         INDEX.md                     - the reader-facing page, grouped by topic
         MANIFEST.sha256              - hashes of the three files above

Two modes:
  * default  - regenerate the vocabulary and the index from the item list published next to this
               script; no extra input needed, so anyone who clones the repository can rebuild them.
  * rebuild  - set EYEKB_TEXTBOOK_SRC to the extraction table of the textbook-inventory card to
               rebuild the item list itself from the books.

Why a separate layer: the curated marker libraries are organised by cell class, while a textbook
gives layers, membranes and regions - "inner limiting membrane", "ora serrata", "Sattler layer".
The two are orthogonal: the cell-class vocabulary identifies what a cluster is, the structural
vocabulary says where it sits. Keeping them in one file would blur which claim is which.

Discipline: textbook entries are definition and anatomy sources. They must never be quoted as
marker-expression evidence, and marker panels must never be quoted as the definition of a layer.
"""
import hashlib
import json
import os
import re
from pathlib import Path

HERE = Path(__file__).resolve().parent
OUT = HERE.parent
ITEMS_JSONL = OUT / "TEXTBOOK_ITEMS_v1.jsonl"
SRC = Path(os.environ["EYEKB_TEXTBOOK_SRC"]) if os.environ.get("EYEKB_TEXTBOOK_SRC") else None

# English labels and the structural kind of each item. Written out rather than inferred: the
# classification is a judgement, and a judgement that cannot be read off the file cannot be
# reviewed.
ITEMS = {
    "BK001": ("Retinal layers, inner to outer", "layer"),
    "BK002": ("Internal limiting membrane (ILM)", "membrane"),
    "BK003": ("Nerve fibre layer (NFL)", "layer"),
    "BK004": ("Ganglion cell layer (GCL)", "layer"),
    "BK005": ("Inner plexiform layer (IPL)", "layer"),
    "BK006": ("Inner nuclear layer (INL)", "layer"),
    "BK007": ("Outer plexiform layer (OPL)", "layer"),
    "BK008": ("Henle fibre layer / middle limiting membrane", "membrane"),
    "BK009": ("Outer nuclear layer (ONL)", "layer"),
    "BK010": ("External limiting membrane (ELM)", "membrane"),
    "BK011": ("Photoreceptor inner and outer segments", "layer"),
    "BK012": ("Retinal pigment epithelium (RPE)", "layer"),
    "BK013": ("Photoreceptor graded potential", "circuitry"),
    "BK014": ("Cone-to-midget-bipolar 1:1 synapse", "circuitry"),
    "BK015": ("Rod convergence onto bipolar cells", "circuitry"),
    "BK016": ("Bipolar-to-ganglion-cell synapse", "circuitry"),
    "BK017": ("Ganglion cell summation and action potentials", "circuitry"),
    "BK018": ("Horizontal cell modulation of photoreceptors", "circuitry"),
    "BK019": ("Mueller cell sheaths enveloping cones", "circuitry"),
    "BK020": ("Retina derives from the optic vesicle", "development"),
    "BK021": ("Bilayered neuroepithelium reflects optic cup topology", "development"),
    "BK022": ("Vitreous and choroid derive from mesenchyme", "development"),
    "BK023": ("RPE shares its neural-tube origin with the neural retina", "development"),
    "BK024": ("Vasa hyaloidea propria fill the embryonic vitreous", "development"),
    "BK025": ("Regression of the hyaloid vascular system", "development"),
    "BK026": ("Persistent hyaloid artery", "development"),
    "BK027": ("Vanguard of mesenchymal cells grows out in the NFL", "development"),
    "BK028": ("Retinal vascularisation completes at 36 / 40 weeks", "development"),
    "BK029": ("RPE repairs locally, unlike the neural retina", "development"),
    "BK030": ("Corneal endothelium is neural-crest derived", "development"),
    "BK031": ("Blood-retinal barrier, definition", "barrier"),
    "BK032": ("Blood-retinal barrier, epithelial (RPE) component", "barrier"),
    "BK033": ("Inner and outer barriers carry junctional complexes", "barrier"),
    "BK034": ("RPE tight junctions (zonulae occludentes)", "barrier"),
    "BK035": ("Inner blood-retina barrier (BCSC wording)", "barrier"),
    "BK036": ("Two blood supplies, each with a blood-retinal barrier", "barrier"),
    "BK037": ("Inner barrier: endothelial tight junctions", "barrier"),
    "BK038": ("Outer barrier: between adjacent RPE cells", "barrier"),
    "BK039": ("Anatomical macula (posterior pole)", "region"),
    "BK040": ("Parafoveal ring (0.5 mm)", "region"),
    "BK041": ("Ora serrata", "region"),
    "BK042": ("Dentate processes", "region"),
    "BK043": ("Meridional fold", "region"),
    "BK044": ("Fovea, definition", "region"),
    "BK045": ("Foveola", "region"),
    "BK046": ("Umbo", "region"),
    "BK047": ("Clivus", "region"),
    "BK048": ("Foveal avascular zone (500 um)", "region"),
    "BK049": ("Cone packing in the foveola", "region"),
    "BK050": ("Fovea externa", "region"),
    "BK051": ("Equatorial and anterior (peripheral) retina", "region"),
    "BK052": ("Vitreous body, definition", "structure"),
    "BK053": ("Core and cortical vitreous", "structure"),
    "BK054": ("Anterior hyaloid membrane and patellar fossa", "membrane"),
    "BK055": ("Posterior vitreous cortex thickness", "structure"),
    "BK056": ("Vitreous base", "structure"),
    "BK057": ("Uveal tract, definition", "structure"),
    "BK058": ("Choroid, five histological layers", "layer"),
    "BK059": ("Bruch membrane", "membrane"),
    "BK060": ("Choriocapillaris", "layer"),
    "BK061": ("Sattler layer", "layer"),
    "BK062": ("Haller layer", "layer"),
    "BK063": ("Ciliary body", "structure"),
    "BK064": ("Ciliary muscle, three fibre groups", "structure"),
    "BK065": ("Iris, pupillary zone and sphincter muscle", "structure"),
    "BK066": ("Retinal venous outflow resistance at the lamina cribrosa", "structure"),
    "BK067": ("Cornea, definition", "structure"),
    "BK068": ("Corneal refraction", "structure"),
    "BK069": ("Bowman membrane", "membrane"),
    "BK070": ("Corneal stroma, about 85% of the thickness", "layer"),
    "BK071": ("Descemet membrane", "membrane"),
    "BK072": ("Corneal endothelium, honeycomb mosaic", "layer"),
    "BK073": ("Schwalbe line", "region"),
    "BK074": ("Corneal epithelium", "layer"),
    "BK075": ("Lens, three parts", "structure"),
    "BK076": ("Lens capsule lamellae", "structure"),
    "BK077": ("Lens epithelium", "layer"),
    "BK078": ("Crystallins, up to 60% of lens wet weight", "structure"),
    "BK079": ("Trabecular pathway components", "pathway"),
    "BK080": ("Aqueous outflow resistance site", "pathway"),
    "BK081": ("Aqueous humour secretion", "pathway"),
}

TOPIC_ORDER = [
    "retinal layers and circuitry", "development", "blood-retinal barrier",
    "macula and regional anatomy", "vitreous", "uvea and choroid", "cornea", "lens",
    "aqueous humour and trabecular meshwork",
]

# item id ranges -> topic. The extraction table carries the topic in Chinese; the published layer
# is English, so the topic is derived from the item id instead of copied from the table.
TOPIC_RANGES = [(1, 19, 0), (20, 30, 1), (31, 38, 2), (39, 51, 3), (52, 56, 4), (57, 66, 5),
                (67, 74, 6), (75, 78, 7), (79, 81, 8)]


def topic_of(item_id):
    n = int(str(item_id)[2:])
    for lo, hi, idx in TOPIC_RANGES:
        if lo <= n <= hi:
            return TOPIC_ORDER[idx]
    raise ValueError(f"no topic range covers {item_id}")


BOOK_SHORT = {
    "BCSC Retina and Vitreous 2011-2012 (AAO Basic&Clinical Science Course)":
        "BCSC Retina and Vitreous 2011-2012 (AAO Basic and Clinical Science Course)",
    "Yanoff & Duker, Ophthalmology, Fourth Edition (Elsevier)":
        "Yanoff and Duker, Ophthalmology, Fourth Edition (Elsevier)",
}


def page_number(anchor):
    m = re.search(r"p(\d+)", anchor or "")
    return int(m.group(1)) if m else None


def parse_extraction(src):
    """Rebuild the item list from the inventory card's extraction table."""
    rows = []
    with src.open(encoding="utf-8") as fh:
        head = fh.readline().rstrip("\n").split("\t")
        for line in fh:
            parts = line.rstrip("\n").split("\t")
            if len(parts) < len(head):
                continue
            r = dict(zip(head, parts))
            iid = r["item_id"]
            label, kind = ITEMS[iid]
            rows.append({
                "item_id": iid,
                "term": label,
                "kind": kind,
                "topic": topic_of(iid),
                "book": BOOK_SHORT.get(r["book_edition"], r["book_edition"]),
                "page": page_number(r["chapter_page_anchor"]),
                "page_anchor": r["chapter_page_anchor"],
                "quote": r["quote_excerpt_verbatim"],
                "quote_chars": int(r["quote_chars"] or 0),
                "kb_status": r["kb_status"],
                "kb_classes": [x for x in (r["kb_term"] or "").split(";") if x],
            })
    return rows


def load_published():
    return [json.loads(l) for l in ITEMS_JSONL.read_text(encoding="utf-8").splitlines() if l.strip()]


def main():
    if SRC and SRC.is_file():
        rows = parse_extraction(SRC)
        print(f"[source] rebuilt {len(rows)} items from the extraction table")
    else:
        rows = load_published()
        print(f"[source] regenerating vocabulary and index from {ITEMS_JSONL.name} ({len(rows)} items); "
              f"set EYEKB_TEXTBOOK_SRC to rebuild the item list from the books instead")
    if not rows:
        raise SystemExit("no textbook items found")
    assert len(rows) == 81, len(rows)

    ITEMS_JSONL.write_text("\n".join(json.dumps(r, ensure_ascii=False) for r in rows) + "\n",
                           encoding="utf-8")

    # The vocabulary is the subset the marker libraries have no equivalent for: layers, membranes
    # and regions carry no cell class, so they need their own list.
    book_only = [r for r in rows if r["kb_status"] == "book_only"]
    vocab = {
        "version": "v1-2026-10-21",
        "scope": "structural vocabulary read from two ophthalmology textbooks: layers, membranes, "
                 "regions, pathways. Complements the cell-class marker libraries, which cannot "
                 "express them.",
        "kinds": {},
        "counts": {"total": len(rows), "book_only": len(book_only),
                   "already_covered": sum(1 for r in rows if r["kb_status"] == "already_covered"),
                   "term_mismatch": sum(1 for r in rows if r["kb_status"] == "term_mismatch")},
        "discipline": "definition and anatomy source only; never marker-expression evidence",
    }
    for r in book_only:
        vocab["kinds"].setdefault(r["kind"], []).append({
            "term": r["term"], "item_id": r["item_id"], "topic": r["topic"],
            "book": r["book"], "page": r["page"],
        })
    for k in vocab["kinds"]:
        vocab["kinds"][k].sort(key=lambda x: x["term"])
    (OUT / "LAYER_REGION_VOCAB_v1.json").write_text(
        json.dumps(vocab, ensure_ascii=False, indent=1) + "\n", encoding="utf-8")

    lines = ["# Textbook layer - structural vocabulary",
             "",
             "Layers, membranes, regions and pathways read from two ophthalmology textbooks. Each entry "
             "carries the book, the PDF page and the sentence it was read from, so any row can be "
             "checked against the page it came from.",
             "",
             f"- items: **{len(rows)}** ({len(book_only)} of them have no equivalent in the cell-class "
             f"marker libraries; {vocab['counts']['already_covered']} restate a cell class the libraries "
             f"already carry; {vocab['counts']['term_mismatch']} disagree on wording)",
             f"- sources: **{len({r['book'] for r in rows})} textbooks** "
             f"({'; '.join(sorted({r['book'] for r in rows}))})",
             "",
             "Read this layer for *where a structure sits*; read the marker libraries for *what a cluster "
             "is*. A textbook row is never marker-expression evidence, and a marker panel is never the "
             "definition of a layer.",
             "",
             "| kind | terms |", "|---|---|"]
    for kind in sorted(vocab["kinds"]):
        terms = ", ".join(t["term"] for t in vocab["kinds"][kind])
        lines.append(f"| {kind} | {terms} |")
    lines.append("")

    for topic in TOPIC_ORDER:
        items = [r for r in rows if r["topic"] == topic]
        if not items:
            continue
        lines += [f"## {topic} - {len(items)} items", "",
                  "| term | kind | source | page | quote | coverage |", "|---|---|---|---|---|---|"]
        for r in items:
            q = r["quote"].replace("|", "/")
            lines.append(f"| {r['term']} | {r['kind']} | {r['book']} | p{r['page']} | \"{q}\" | "
                         f"{r['kb_status']} |")
        lines.append("")
    (OUT / "INDEX.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    man = []
    for f in ("TEXTBOOK_ITEMS_v1.jsonl", "LAYER_REGION_VOCAB_v1.json", "INDEX.md"):
        b = (OUT / f).read_bytes()
        man.append(f"{hashlib.sha256(b).hexdigest()}  {f}")
    (OUT / "MANIFEST.sha256").write_text("\n".join(man) + "\n", encoding="utf-8")

    print(f"items={len(rows)} book_only={len(book_only)} "
          f"kinds={ {k: len(v) for k, v in sorted(vocab['kinds'].items())} }")


if __name__ == "__main__":
    main()