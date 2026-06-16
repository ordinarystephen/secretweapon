#!/usr/bin/env python3
"""
Inspect a Document Intelligence prebuilt-layout `as_dict()` (di_layout.json)
to determine whether section hierarchy is recoverable from typographic signals.

Targets the specific heading levels from the Academy quarterly review:
  - gray-banner masters:   "Recent Developments", "1st Line of Defense Assessment"
  - bold sub-headings:     "Near-term considerations"
  - underlined sub-subs:   "Geo Political and Tariff Impact", "AI Impact"
  - dated content entries: "Aug-2025", "Apr-2025", "Oct-2024"
  - the section in question: "Company Overview"
  - plus a body-text baseline (auto-sampled)

Usage:
    python inspect_di_layout.py /path/to/di_layout.json

Reports, per matched paragraph: page, bbox height (font-size proxy, in inches),
bbox width, x-origin, DI role, and any font styles (bold/underline/etc.) that
DI attached to that text span.
"""

import json
import sys


# ---- the exact strings to find, grouped by their visual level in the PDF ----
TARGETS = {
    "MASTER (gray banner)": [
        "Recent Developments",
        "1st Line of Defense Assessment",
    ],
    "SUB (bold)": [
        "Near-term considerations",
    ],
    "SUB-SUB (underlined)": [
        "Geo Political and Tariff Impact",
        "AI Impact",
    ],
    "DATE ENTRY (bold, suspected content not heading)": [
        "Aug-2025",
        "Apr-2025",
        "Oct-2024",
    ],
    "THE SECTION IN QUESTION": [
        "Company Overview",
    ],
}


def poly_metrics(polygon):
    """DI polygon = [x0,y0, x1,y1, x2,y2, x3,y3] (clockwise from top-left), inches.
    Returns (height, width, x_origin, y_top) — height is the font-size proxy."""
    if not polygon or len(polygon) < 8:
        return None, None, None, None
    xs = polygon[0::2]
    ys = polygon[1::2]
    height = max(ys) - min(ys)
    width = max(xs) - min(xs)
    return round(height, 4), round(width, 4), round(min(xs), 4), round(min(ys), 4)


def get_page(par):
    regions = par.get("boundingRegions") or []
    if regions:
        return regions[0].get("pageNumber")
    return None


def get_polygon(par):
    regions = par.get("boundingRegions") or []
    if regions:
        return regions[0].get("polygon") or []
    return []


def build_style_index(data):
    """DI `styles[]` entries describe formatting (e.g. fontWeight, but DI's layout
    model varies) and which character spans they apply to. Build offset->styles
    so we can report formatting for each matched paragraph's span.

    Each style may carry keys like: fontWeight ('bold'), fontStyle, color,
    backgroundColor, isHandwritten, plus `spans:[{offset,length}]`. We index by
    covering ranges and also just collect ALL distinct style keys present so you
    can see what DI captured at all (bold? underline? shading?)."""
    styles = data.get("styles") or []
    ranges = []  # (start, end, style_dict_without_spans)
    all_keys = set()
    for s in styles:
        stripped = {k: v for k, v in s.items() if k != "spans"}
        for k in stripped:
            all_keys.add(k)
        for sp in (s.get("spans") or []):
            off = sp.get("offset", 0)
            length = sp.get("length", 0)
            ranges.append((off, off + length, stripped))
    return ranges, all_keys


def styles_for_span(span_offset, span_len, ranges):
    """Return any style dicts whose range overlaps this paragraph's span."""
    out = []
    s_start, s_end = span_offset, span_offset + span_len
    for (r_start, r_end, sd) in ranges:
        if r_start < s_end and r_end > s_start:  # overlap
            out.append(sd)
    return out


def first_span(par):
    spans = par.get("spans") or []
    if spans:
        return spans[0].get("offset", 0), spans[0].get("length", 0)
    return 0, 0


def main():
    if len(sys.argv) < 2:
        print("usage: python inspect_di_layout.py /path/to/di_layout.json")
        sys.exit(1)

    path = sys.argv[1]
    with open(path) as f:
        data = json.load(f)

    # DI as_dict() sometimes nests under "analyzeResult"; handle both.
    if "paragraphs" not in data and "analyzeResult" in data:
        data = data["analyzeResult"]

    paragraphs = data.get("paragraphs") or []
    pages = data.get("pages") or []
    style_ranges, all_style_keys = build_style_index(data)

    print("=" * 78)
    print(f"FILE: {path}")
    print(f"paragraphs: {len(paragraphs)}   pages: {len(pages)}   "
          f"styles entries: {len(data.get('styles') or [])}")
    print(f"distinct style keys DI captured: {sorted(all_style_keys) or '(none)'}")
    print("  -> if 'fontWeight'/'fontStyle'/'color'/'backgroundColor' appear,")
    print("     you have weight/underline/shading signals; if empty, size only.")
    print("=" * 78)

    # ---- report each target heading ----
    matched_heights = {}  # level -> list of heights, to summarize steps
    for level, needles in TARGETS.items():
        print(f"\n### {level}")
        for needle in needles:
            hits = [p for p in paragraphs
                    if needle.lower() in (p.get("content", "") or "").lower()]
            if not hits:
                print(f"  [NOT FOUND] {needle!r}")
                continue
            for par in hits:
                content = (par.get("content", "") or "")[:60]
                h, w, x0, ytop = poly_metrics(get_polygon(par))
                off, length = first_span(par)
                sp_styles = styles_for_span(off, length, style_ranges)
                style_note = sp_styles if sp_styles else "(no style on this span)"
                print(f"  text:   {content!r}")
                print(f"    page: {get_page(par)}   height(in): {h}   "
                      f"width(in): {w}   x-origin: {x0}")
                print(f"    role:  {par.get('role')}")
                print(f"    style: {style_note}")
                if h is not None:
                    matched_heights.setdefault(level, []).append(h)

    # ---- body-text baseline: sample some paragraphs with no role and long text ----
    print("\n### BODY-TEXT BASELINE (auto-sampled, role=None, long content)")
    body_heights = []
    shown = 0
    for par in paragraphs:
        if par.get("role"):
            continue
        content = par.get("content", "") or ""
        if len(content) < 80:  # likely real body text, not a stray label
            continue
        h, w, x0, ytop = poly_metrics(get_polygon(par))
        if h is None:
            continue
        body_heights.append(h)
        if shown < 4:
            print(f"  text:   {content[:60]!r}")
            print(f"    page: {get_page(par)}   height(in): {h}")
            shown += 1
    if body_heights:
        avg_body = round(sum(body_heights) / len(body_heights), 4)
        print(f"  --> sampled {len(body_heights)} body paragraphs, "
              f"avg height: {avg_body} in")

    # ---- the punchline: do the levels step down? ----
    print("\n" + "=" * 78)
    print("HEIGHT SUMMARY (font-size proxy by level) — do these STEP DOWN?")
    print("=" * 78)
    for level in TARGETS:
        hs = matched_heights.get(level, [])
        if hs:
            print(f"  {level:48s} {[round(x,3) for x in hs]}  "
                  f"(avg {round(sum(hs)/len(hs),3)})")
        else:
            print(f"  {level:48s} (none found)")
    if body_heights:
        print(f"  {'BODY TEXT':48s} avg {round(sum(body_heights)/len(body_heights),3)}")
    print("\nREAD THIS:")
    print(" - If MASTER > SUB > SUB-SUB > BODY in height, font size alone gives")
    print("   you the hierarchy -> level inference is buildable on size clustering.")
    print(" - If DATE ENTRY height ~= BODY height, the dates are visually NOT")
    print("   headings -> easy to exclude from section detection.")
    print(" - If levels do NOT separate by height, check the 'distinct style keys'")
    print("   above: you'll need weight/underline/shading from styles[] instead,")
    print("   and if those are absent too, DI is too lossy -> visual analysis needed.")
    print(" - Compare 'Company Overview' height to MASTER: if equal, it's a master")
    print("   (its whole-PDF image span = boundary logic not stopping at next master);")
    print("   if shorter, it's a sub and its boundary is plain wrong.")


if __name__ == "__main__":
    main()