#!/usr/bin/env python3
"""
Fetch citation stats from Google Scholar and update index.html.
Exits 0 in all cases so the GitHub Action never fails noisily —
if Scholar blocks the request, the stats just stay as-is until next run.
"""
import re
import sys

SCHOLAR_ID = "ioDaRtYAAAAJ"
INDEX = "index.html"

try:
    from scholarly import scholarly
except ImportError:
    print("scholarly not installed")
    sys.exit(1)

try:
    print(f"Fetching Scholar profile {SCHOLAR_ID} ...")
    author = scholarly.search_author_id(SCHOLAR_ID)
    scholarly.fill(author, sections=["basics"])
    citations = int(author.get("citedby", 0))
    h_index = int(author.get("hindex", 0))
    if not citations or not h_index:
        print("Empty stats returned — Scholar may have blocked the request. Skipping.")
        sys.exit(0)
    print(f"Citations: {citations}  h-index: {h_index}")
except Exception as exc:
    print(f"Could not fetch Scholar data: {exc}")
    sys.exit(0)

with open(INDEX, encoding="utf-8") as f:
    original = f.read()

updated = re.sub(
    r'(<span class="number">)\d+(</span>\s*\n\s*<span class="label">Citations</span>)',
    rf"\g<1>{citations}\g<2>",
    original,
)
updated = re.sub(
    r'(<span class="number">)\d+(</span>\s*\n\s*<span class="label">h-index</span>)',
    rf"\g<1>{h_index}\g<2>",
    updated,
)

if updated == original:
    print("Stats unchanged — nothing to commit.")
    sys.exit(0)

with open(INDEX, "w", encoding="utf-8") as f:
    f.write(updated)

print("index.html updated.")
