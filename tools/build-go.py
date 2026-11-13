#!/usr/bin/env python3
"""Writes go/<slug>/index.html for every short link in go/links.json.

GitHub Pages can't send server redirects, so each short link is a tiny page that forwards at
at once. Before forwarding, the script sends one count for /go/<slug> to GoatCounter (t-168, no
cookies, no IP stored; see /privacy/) and waits for it to go out, at most WAIT_MS, because in-app
browsers (TikTok) drop a request still in flight when the page leaves. Without JavaScript a meta
refresh forwards at once, uncounted. Pages for slugs no longer in links.json are removed.

    python3 tools/build-go.py
"""
import html
import json
import shutil
from pathlib import Path

COUNT = "https://m77apps.goatcounter.com/count"
WAIT_MS = 700

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
<noscript><meta http-equiv="refresh" content="0; url={attr}"></noscript>
<link rel="canonical" href="{attr}">
<title>Punfortunate · M77 Apps</title>
<script>(function(){{var done=0,go=function(){{if(!done){{done=1;location.replace({js})}}}};try{{fetch({count}+"&rnd="+Math.random().toString(36).slice(2),{{mode:"no-cors",keepalive:true,credentials:"omit",referrerPolicy:"no-referrer"}}).then(go,go)}}catch(e){{go()}}setTimeout(go,{wait})}})();</script>
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
    (folder / "index.html").write_text(PAGE.format(attr=html.escape(target), js=json.dumps(target), count=json.dumps(f"{COUNT}?p=/go/{slug}"), wait=WAIT_MS))

for folder in go.iterdir():
    if folder.is_dir() and folder.name not in links:
        shutil.rmtree(folder)

print(f"{len(links)} short links: " + ", ".join(f"/go/{s}" for s in links))
