# -*- coding: utf-8 -*-
"""f1_fix_subtype_markers.py -- DEFECT-1 fix: give kb/markers/markers_v14_subtype_second_increment.json
the top-level `markers` block it lacked, derived from its own entries (source of truth per the card),
without changing any panel gene.

Mechanics: keep the file's original key order (insertion order preserved via json.load on a normal
dict, py3.7+); insert "markers" immediately before "entries"; write back with indent=1 +
ensure_ascii=False (the file's existing style, measured from its own bytes before the edit).

Hard assertions BEFORE writing:
  * exactly 16 entries, distinct class_names;
  * derived = {e.class_name: list(e.markers)} and every list non-empty, order preserved;
  * re-parse round-trip equality of the new bytes' markers vs derived, and of every entry;
  * the panel-gene union before == after (no gene added/removed/reordered anywhere);
  * the only top-level key added is "markers".
Writes: the release file (in place), out/F1_FIX.json, pre_images/...pre bytes.
Zero network, zero GPU.
"""
import hashlib
import json
import os
import shutil

HERE = os.path.dirname(os.path.abspath(__file__))
WAVE = os.path.dirname(HERE)
OUT = os.path.join(WAVE, "out")
PRE = os.path.join(WAVE, "pre_images")
REPO = "/home/ubuntu/EYEKB_REPO"
P = os.path.join(REPO, "kb/markers/markers_v14_subtype_second_increment.json")

raw_before = open(P, "rb").read()
sha_before = hashlib.sha256(raw_before).hexdigest()
d = json.loads(raw_before.decode("utf-8"))

entries = d["entries"]
assert len(entries) == 16, len(entries)
names = [e["class_name"] for e in entries]
assert len(set(names)) == 16, names
derived = {}
for e in entries:
    ms = list(e.get("markers") or [])
    assert ms and all(isinstance(x, str) and x.strip() for x in ms), e["class_name"]
    derived[e["class_name"]] = ms

assert "markers" not in d, "top-level markers already present?"
d_order_end = list(d.keys()).index("entries")
new = {}
for k, v in d.items():
    if k == "entries":
        new["markers"] = derived
    new[k] = v
assert list(new.keys()) == list(d.keys())[:d_order_end] + ["markers"] + list(d.keys())[d_order_end:]
new_bytes = (json.dumps(new, ensure_ascii=False, indent=1) + "\n").encode("utf-8")
# the shipped file ends with a newline? measure from the original bytes
orig_ends_nl = raw_before.endswith(b"\n")
if not orig_ends_nl and new_bytes.endswith(b"\n"):
    new_bytes = new_bytes[:-1]

# validate the candidate bytes BEFORE touching the release
nd = json.loads(new_bytes.decode("utf-8"))
assert nd["markers"] == derived
assert [e["class_name"] for e in nd["entries"]] == names
for e in nd["entries"]:
    assert nd["markers"][e["class_name"]] == list(e["markers"])
# panel genes untouched, everywhere
def panel_set(doc):
    s = set()
    for e in doc["entries"]:
        for g in e.get("markers") or []:
            s.add((e["class_name"], g))
    return s
assert panel_set(d) == panel_set(nd)
assert set(d.keys()) | {"markers"} == set(nd.keys()) and len(nd.keys()) == len(d.keys()) + 1
assert all(list(nd[k] if isinstance(nd[k], (dict, list)) else [nd[k]]) ==
           list(d[k] if isinstance(d[k], (dict, list)) else [d[k]])
           for k in d if k != "entries")

os.makedirs(PRE, exist_ok=True)
pre_path = os.path.join(PRE, "markers_v14_subtype_second_increment.json.pre_kbreach")
shutil.copy2(P, pre_path)
assert hashlib.sha256(open(pre_path, "rb").read()).hexdigest() == sha_before
with open(P, "wb") as f:
    f.write(new_bytes)
raw_after = open(P, "rb").read()
sha_after = hashlib.sha256(raw_after).hexdigest()

doc = {
    "probe": "f1_fix_subtype_markers.py",
    "file": "kb/markers/markers_v14_subtype_second_increment.json",
    "sha256_before": sha_before, "sha256_after": sha_after,
    "bytes_before": len(raw_before), "bytes_after": len(raw_after),
    "pre_image": pre_path,
    "markers_classes": len(derived),
    "insertion_position": "top-level key 'markers' inserted immediately before 'entries'",
    "indent_style": "indent=1, ensure_ascii=False, trailing newline present=%s" % bool(new_bytes.endswith(b"\n")),
    "panel_gene_union_unchanged": True,
    "per_class_gene_lists_byte_equal_to_entries": True,
}
with open(os.path.join(OUT, "F1_FIX.json"), "w", encoding="utf-8") as f:
    json.dump(doc, f, ensure_ascii=False, indent=1)
print(json.dumps(doc, indent=1, ensure_ascii=False))
