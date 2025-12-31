#!/usr/bin/env python3
"""
Scan static/ and media/ for assets not referenced in templates, css, or js.
Exclude admin/vendor/django_extensions directories.
"""
import os
from pathlib import Path
import json

ROOT = Path(__file__).resolve().parents[1]
STATIC = ROOT / 'static'
MEDIA = ROOT / 'media'
ignore_dirs = {'admin', 'django_extensions', 'vendor'}

# Collect all asset files under static (excluding ignore_dirs)
assets = []
for p in (STATIC.rglob('*') if STATIC.exists() else []):
    if p.is_file():
        parts = set(p.parts)
        if parts & ignore_dirs:
            continue
        if p.suffix.lower() in {'.png', '.jpg', '.jpeg', '.gif', '.svg', '.webp', '.css', '.js'}:
            assets.append(p)

# Build corpus of files to search in (templates, css, js, py, html)
search_files = []
for p in ROOT.rglob('*'):
    if p.is_file() and p.suffix.lower() in {'.html', '.htm', '.css', '.js', '.py', '.md'}:
        # skip files in static/admin vendor
        if 'static' in p.parts and ('admin' in p.parts or 'django_extensions' in p.parts):
            continue
        search_files.append(p)

# Read contents
contents = []
for f in search_files:
    try:
        contents.append(f.read_text(encoding='utf-8', errors='ignore'))
    except Exception:
        contents.append('')

unused = []
for a in assets:
    name = a.name
    found = False
    for text in contents:
        if name in text:
            found = True
            break
        if str(a.relative_to(ROOT)).replace('\\','/') in text:
            found = True
            break
    if not found:
        unused.append(str(a))

out = {'assets_scanned': len(assets), 'unused_assets': unused}
print(json.dumps(out, indent=2))
with open(ROOT / 'tools' / 'unused_static_report.json', 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=2)
print('\nReport written to tools/unused_static_report.json')
