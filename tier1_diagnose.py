python3 - <<'PY'
import json, glob
for ep in glob.glob("/mnt/private/next-sentinel/doc_store/*/extractions/*/extraction.json"):
    secs = (json.load(open(ep)).get("sections") or {})
    if "SPARTA" not in json.dumps(secs) and "Standalone" not in json.dumps(secs):
        continue
    print("SECTION KEYS:")
    for k in secs:
        print("   ", repr(k))
    # any key holding transaction/deal narrative?
    for k, v in secs.items():
        t = (v.get("text") or "") if isinstance(v, dict) else ""
        if any(w in k.lower() for w in ("transaction", "deal")) or "transaction" in t.lower()[:200]:
            print("\nCANDIDATE:", repr(k), "->", repr(t[:300]))
    break
PY
