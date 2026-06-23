python3 - <<'PY'
import json, glob
for ep in glob.glob("/mnt/private/next-sentinel/doc_store/*/extractions/*/extraction.json"):
    secs = (json.load(open(ep)).get("sections") or {})
    if "SPARTA" not in json.dumps(secs) and "Standalone" not in json.dumps(secs):
        continue
    print("FILE:", ep)
    def show(label, predicate):
        for name, sec in secs.items():
            if predicate(str(name).lower()) and isinstance(sec, dict):
                print(f"\n===== {label} | KEY={name!r} =====")
                print(repr(sec.get("text") or "(empty)")[:6000])
    # 1) the section that HOLDS the labeled narrative paragraphs (verbatim, repr to see newlines):
    show("2nd LoD", lambda n: "line of defense" in n)
    # 2) confirm the top-level keys the text elements mis-matched are the image/table sections:
    show("MIS-MATCH", lambda n: n in (
        "historical financial performance", "liquidity summary",
        "performance vs. updated ubs expected case"))
    print("="*100); break
PY
