#!/usr/bin/env python3
"""Writes the FAQPage structured data on each app page from the FAQ the page shows.

Search engines and AI assistants read the FAQ as schema.org FAQPage JSON-LD. Google requires it
to match the visible questions, so it is built from the page's <details class="faq"> items, never
written by hand. Run it after editing an FAQ; it replaces the <script id="faq-schema"> block, or
adds one before </head> the first time.

    python3 tools/build-faq-schema.py
"""
import html
import json
import re
from pathlib import Path

PAGES = ["punfortunate/index.html", "ringbox/index.html"]
FAQ = re.compile(r'<details class="faq"><summary>(.*?)</summary>(.*?)</details>', re.S)
BLOCK = re.compile(r'<script type="application/ld\+json" id="faq-schema">.*?</script>', re.S)

site = Path(__file__).resolve().parent.parent


def text(fragment):
    """Visible text of an HTML fragment, links kept as their words."""
    return html.unescape(re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", fragment))).strip().replace(" .", ".").replace(" ,", ",")


for rel in PAGES:
    path = site / rel
    page = path.read_text(encoding="utf-8")
    items = [{"@type": "Question", "name": text(q), "acceptedAnswer": {"@type": "Answer", "text": text(a)}}
             for q, a in FAQ.findall(page)]
    if not items:
        raise SystemExit(f"{rel}: no FAQ items found")
    data = json.dumps({"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": items},
                      ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
    block = f'<script type="application/ld+json" id="faq-schema">{data}</script>'
    page = BLOCK.sub(lambda _: block, page) if BLOCK.search(page) else page.replace("</head>", block + "\n</head>", 1)
    path.write_text(page, encoding="utf-8")
    print(f"{rel}: {len(items)} questions")
