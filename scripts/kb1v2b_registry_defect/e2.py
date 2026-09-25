import json
fn = "/mnt/D/OcularKB/registry/E2_final_integrity_audit_precutoff_20260905.json"
d = json.load(open(fn))
print("type:", type(d).__name__, "keys:" , list(d.keys())[:20] if isinstance(d, dict) else None)
arr = None
if isinstance(d, dict):
    for k, v in d.items():
        if isinstance(v, list) and v and isinstance(v[0], dict):
            arr = v
            print("list key:", k, "len", len(v))
            break
elif isinstance(d, list):
    arr = d
if arr:
    from collections import Counter
    print("total entries:", len(arr))
    print("in_local:", Counter(str(e.get("in_local")) for e in arr))
    print("verdict:", Counter(str(e.get("verdict")) for e in arr).most_common(8))
    print("keys:", sorted(arr[0].keys()))
    # sample rows
    for e in arr[:3]:
        print("  ", json.dumps(e, ensure_ascii=False)[:250])
    # the HRA rows
    for e in arr:
        if "HRA" in str(e.get("accession", "")):
            print("  HRA>", json.dumps(e, ensure_ascii=False)[:300])
