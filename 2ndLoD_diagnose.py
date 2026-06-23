python3 - <<'PY'
import json, glob
from server.graphs import ib_lending
for ep in glob.glob("/mnt/private/next-sentinel/doc_store/*/extractions/*/extraction.json"):
    secs = (json.load(open(ep)).get("sections") or {})
    if "SPARTA" not in json.dumps(secs) and "Standalone" not in json.dumps(secs):
        continue
    lod = (secs.get("2nd Line of Defense Assessment") or {}).get("text") or ""
    print("2nd LoD length:", len(lod))
    print("regex matches:", bool(ib_lending._lod_label_re("Updated UBS Expected Case").search(lod)))
    print("paragraph    :", repr(ib_lending._labeled_paragraph(lod, "Updated UBS Expected Case")))
    for line in lod.splitlines():
        if "updated" in line.lower() or "expected case" in line.lower():
            print("LINE   :", repr(line))
            print("CODEPTS:", [hex(ord(c)) for c in line[:50]])
    break
PY
