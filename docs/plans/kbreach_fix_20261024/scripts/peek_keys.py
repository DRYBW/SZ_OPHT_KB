# -*- coding: utf-8 -*-
import json
p = "/home/ubuntu/EYEKB_REPO/kb/markers/markers_v14_subtype_second_increment.json"
d = json.load(open(p, encoding="utf-8"))
print("true key order:", list(d.keys()))
print("has version:", "version" in d, "| version:", d.get("version"))
print("indent guess: first 3 raw lines")
for i, line in enumerate(open(p, encoding="utf-8")):
    if i >= 3:
        break
    print(repr(line))
