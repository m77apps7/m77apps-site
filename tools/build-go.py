#!/usr/bin/env python3
"""Writes go/<slug>/index.html for every short link in go/links.json.

GitHub Pages can't send server redirects, so each short link is a tiny page that forwards at
once (meta refresh, plus a script for browsers that ignore it). The page keeps nothing about the
visitor. Pages for slugs no longer in links.json are removed.

    python3 tools/build-go.py
"""
import html
import json
import shutil
from pathlib import Path

site = Path(__file__).resolve().parent.parent
go = site / "go"
links = {k: v for k, v in json.loads((go / "links.json").read_text()).items() if not k.startswith("_")}

PAGE = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex">
<meta name="referrer" content="no-referrer">
<meta http-equiv="refresh" content="0; url={attr}">
<link rel="canonical" href="{attr}">
<title>Punfortunate · M77 Apps</title>
<script>location.replace({js});</script>
</head>
<body>
<p>Opening <a href="{attr}">Punfortunate</a>…</p>
</body>
</html>
"""

for slug, link in links.items():
    target = link["target"]
    if not target.startswith("https://"):
        raise SystemExit(f"{slug}: target must be an https URL")
    folder = go / slug
    folder.mkdir(exist_ok=True)
    (folder / "index.html").write_text(PAGE.format(attr=html.escape(target), js=json.dumps(target)))

for folder in go.iterdir():
    if folder.is_dir() and folder.name not in links:
        shutil.rmtree(folder)

print(f"{len(links)} short links: " + ", ".join(f"/go/{s}" for s in links))
