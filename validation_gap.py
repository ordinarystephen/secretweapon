python3 - <<'PY'
import json, glob, os
for ep in glob.glob("/mnt/private/next-sentinel/doc_store/*/extractions/*/extraction.json"):
    secs = (json.load(open(ep)).get("sections") or {})
    if "SPARTA" not in json.dumps(secs) and "Standalone" not in json.dumps(secs):
        continue
    md = os.path.dirname(ep)
    print("== extraction['sections'] KEYS ==")
    for k in secs: print("   ", repr(k))
    si = os.path.join(md, "section_images")
    print("\n== section_images/*.png ==\n   ", sorted(os.listdir(si)) if os.path.isdir(si) else "(none)")
    cj = os.path.join(md, "crops.json")
    print("\n== crops.json records ==")
    if os.path.exists(cj):
        for c in json.load(open(cj)).get("crops", []):
            print(f"   crop_id={c.get('crop_id')!r} concept_label={c.get('concept_label')!r} "
                  f"parent_section={c.get('parent_section')!r} page={c.get('page')} "
                  f"conf={c.get('match_confidence')} via={c.get('resolved_via')}")
    else: print("   (none)")
    print("="*90)
PY
