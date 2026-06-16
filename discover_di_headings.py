#!/usr/bin/env python3
"""
DISCOVERY inspector for an UNKNOWN document type.

Unlike inspect_di_layout.py (which searches for the Academy review's known
headings), this dumps EVERY heading DI tagged, with geometry, so you can see
what the structure of a comfort memo / commitments committee memo / any new
format actually looks like — and whether the master-vs-sub discriminator
(left-margin x-origin + taller size band) holds for it.

Usage:
    python discover_di_headings.py /path/to/di_layout.json

Outputs:
  1. Every paragraph DI tagged as sectionHeading or title, in document order,
     with page / x-origin / height / a date-pattern flag.
  2. A clustering view: heading x-origins and heights grouped, so you can SEE
     whether masters (left margin, taller) separate from subs (indented, shorter)
     for THIS document — or whether this format breaks that assumption.
  3. A proposed master/sub split using the Academy-derived thresholds, so you
     can eyeball whether those thresholds transfer to this document type.
"""

import json
import re
import sys
from collections import Counter

# thresholds derived from the Academy quarterly review — testing whether they transfer
LEFT_MARGIN_MAX = 0.52     # masters started ~0.50-0.51; subs ~0.43
MASTER_HEIGHT_MIN = 0.150  # masters ~0.154-0.164; subs ~0.133

DATE_RE = re.compile(
    r"\b(\d{1,2}[-/ ])?"
    r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)"
    r"[a-z]*[-/ ]?\d{2,4}\b",
    re.IGNORECASE,
)


def poly_metrics(polygon):
    if not polygon or len(polygon) < 8:
        return None, None, None, None
    xs = polygon[0::2]
    ys = polygon[1::2]
    return (round(max(ys) - min(ys), 4), round(max(xs) - min(xs), 4),
            round(min(xs), 4), round(min(ys), 4))


def get_region(par):
    regions = par.get("boundingRegions") or []
    return regions[0] if regions else {}


def looks_like_date(text):
    return bool(DATE_RE.search(text or ""))


def main():
    if len(sys.argv) < 2:
        print("usage: python discover_di_headings.py /path/to/di_layout.json")
        sys.exit(1)

    with open(sys.argv[1]) as f:
        data = json.load(f)
    if "paragraphs" not in data and "analyzeResult" in data:
        data = data["analyzeResult"]

    paragraphs = data.get("paragraphs") or []
    pages = data.get("pages") or []

    # collect everything DI considers a heading
    headings = []
    role_counts = Counter()
    for idx, par in enumerate(paragraphs):
        role = par.get("role")
        role_counts[role] += 1
        if role not in ("sectionHeading", "title"):
            continue
        region = get_region(par)
        h, w, x0, ytop = poly_metrics(region.get("polygon"))
        content = (par.get("content", "") or "").strip()
        headings.append({
            "order": idx,
            "text": content,
            "role": role,
            "page": region.get("pageNumber"),
            "height": h,
            "x0": x0,
            "is_date": looks_like_date(content),
        })

    print("=" * 80)
    print(f"FILE: {sys.argv[1]}")
    print(f"paragraphs: {len(paragraphs)}   pages: {len(pages)}")
    print(f"role distribution: {dict(role_counts)}")
    print(f"headings (sectionHeading/title): {len(headings)}")
    print("=" * 80)

    # 1. every heading in document order
    print("\n### ALL HEADINGS IN DOCUMENT ORDER")
    print(f"{'pg':>3} {'x0':>6} {'ht':>6}  {'role':<14} {'date?':<6} text")
    print("-" * 80)
    for hd in headings:
        date_flag = "DATE" if hd["is_date"] else ""
        x0 = f"{hd['x0']:.3f}" if hd["x0"] is not None else "  -  "
        ht = f"{hd['height']:.3f}" if hd["height"] is not None else "  -  "
        print(f"{str(hd['page']):>3} {x0:>6} {ht:>6}  "
              f"{(hd['role'] or '')[:14]:<14} {date_flag:<6} {hd['text'][:50]}")

    # 2. clustering view — do x-origins / heights form groups?
    print("\n### X-ORIGIN DISTRIBUTION (do headings cluster by indent?)")
    x_vals = sorted(h["x0"] for h in headings if h["x0"] is not None)
    _histogram(x_vals, width=0.05, unit="in")

    print("\n### HEIGHT DISTRIBUTION (do headings cluster by size?)")
    h_vals = sorted(h["height"] for h in headings if h["height"] is not None)
    _histogram(h_vals, width=0.02, unit="in")

    # 3. proposed master/sub split using Academy thresholds
    print("\n### PROPOSED MASTER/SUB SPLIT (Academy thresholds — do they transfer?)")
    print(f"    rule: MASTER if x0 <= {LEFT_MARGIN_MAX} AND height >= "
          f"{MASTER_HEIGHT_MIN} (date-entries demoted)")
    masters, subs, demoted = [], [], []
    for hd in headings:
        if hd["is_date"]:
            demoted.append(hd)
        elif (hd["x0"] is not None and hd["height"] is not None
              and hd["x0"] <= LEFT_MARGIN_MAX and hd["height"] >= MASTER_HEIGHT_MIN):
            masters.append(hd)
        else:
            subs.append(hd)

    print(f"\n  MASTERS ({len(masters)}):")
    for hd in masters:
        print(f"    pg{hd['page']} x{hd['x0']:.3f} h{hd['height']:.3f}  {hd['text'][:55]}")
    print(f"\n  SUBS ({len(subs)}):")
    for hd in subs:
        x0 = f"{hd['x0']:.3f}" if hd['x0'] is not None else "-"
        h = f"{hd['height']:.3f}" if hd['height'] is not None else "-"
        print(f"    pg{hd['page']} x{x0} h{h}  {hd['text'][:55]}")
    print(f"\n  DEMOTED AS DATE-ENTRIES ({len(demoted)}):")
    for hd in demoted:
        print(f"    pg{hd['page']}  {hd['text'][:55]}")

    print("\n" + "=" * 80)
    print("READ THIS:")
    print(" - Look at ALL HEADINGS: are the real master sections (the major")
    print("   sections you'd want) tagged sectionHeading at all? If they're")
    print("   missing from this list, DI didn't tag them -> harder problem.")
    print(" - X-ORIGIN distribution: do you see TWO clusters (a left-margin")
    print("   group = masters, an indented group = subs)? If everything's at")
    print("   one x-origin, indent won't separate levels for this doc type.")
    print(" - HEIGHT distribution: two size bands? If headings are all one")
    print("   height, size won't separate levels either.")
    print(" - PROPOSED SPLIT: does the master list contain the sections you")
    print("   actually need, and only those? If subs/junk leaked into masters")
    print("   or real masters fell into subs, the Academy thresholds DON'T")
    print("   transfer to this doc type -> need per-document clustering, not")
    print("   fixed thresholds. THAT is the key finding for the noisy types.")


def _histogram(values, width, unit):
    """Simple text histogram to reveal clustering."""
    if not values:
        print("  (none)")
        return
    lo, hi = min(values), max(values)
    n_bins = max(1, int((hi - lo) / width) + 1)
    bins = [0] * n_bins
    for v in values:
        bins[min(n_bins - 1, int((v - lo) / width))] += 1
    for i, count in enumerate(bins):
        if count == 0:
            continue
        bin_lo = lo + i * width
        bar = "#" * count
        print(f"  {bin_lo:.3f}-{bin_lo + width:.3f} {unit}: {bar} ({count})")


if __name__ == "__main__":
    main()