python3 - <<'PY'
import json, glob
for ep in glob.glob("/mnt/private/next-sentinel/doc_store/*/extractions/*/extraction.json"):
    d = json.load(open(ep)); secs = d.get("sections") or {}
    for name, sec in secs.items():
        t = (sec.get("text") or "") if isinstance(sec, dict) else ""
        if "S&P" in t or "S&amp;P" in t or "Standalone" in t or "static" in name.lower():
            print("FILE:", ep, "\nSECTION:", repr(name))
            print("---- TEXT (verbatim) ----\n" + t[:6000])
            print("---- STATIC_FIELDS ----\n" + json.dumps(sec.get("static_fields"), indent=1)[:1500])
            print("="*90)
PY
