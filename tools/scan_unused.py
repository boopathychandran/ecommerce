#!/usr/bin/env python3
"""
Scan repository for files that are not referenced by other text files.
Heuristic: Check for basename occurrences in other files' contents.

Outputs a JSON with candidates grouped by extension.
"""
import os
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEXT_EXTS = {'.py', '.html', '.htm', '.css', '.js', '.md', '.txt', '.json', '.yml', '.yaml', '.ini', '.cfg', '.rst'}
SCAN_EXTS = {'.py', '.html', '.css', '.js', '.md'}

ignore_dirs = {'venv', '.venv', '__pycache__', 'node_modules', '.git', 'media', 'staticfiles'}

all_files = []
for p in ROOT.rglob('*'):
    if any(part in ignore_dirs for part in p.parts):
        continue
    if p.is_file():
        all_files.append(p)

# Build content map for text files
content_map = {}
for f in all_files:
    if f.suffix.lower() in TEXT_EXTS:
        try:
            content_map[str(f)] = f.read_text(encoding='utf-8', errors='ignore')
        except Exception:
            content_map[str(f)] = ''

# Build basename -> paths map
basename_map = {}
for f in all_files:
    basename = f.name
    basename_map.setdefault(basename, []).append(str(f))

candidates = {}

# For each file with extension in SCAN_EXTS, check if its basename appears anywhere else
for f in all_files:
    if f.suffix.lower() in SCAN_EXTS:
        b = f.name
        referenced = False
        for path, text in content_map.items():
            # skip self
            if os.path.samefile(path, f):
                continue
            if b in text:
                referenced = True
                break
            # also check URL-encoded and simple variants
            if b.replace(' ', '%20') in text:
                referenced = True
                break
            if b.replace(' ', '_') in text:
                referenced = True
                break
        if not referenced:
            candidates.setdefault(f.suffix.lower(), []).append(str(f))

# Also list .md files not referenced
# Save results
out = {
    'root': str(ROOT),
    'scanned': len(all_files),
    'candidates': candidates,
}
print(json.dumps(out, indent=2))

# Also write to file for interactive review
out_path = ROOT / 'tools' / 'unused_report.json'
with open(out_path, 'w', encoding='utf-8') as fh:
    json.dump(out, fh, indent=2)
print('\nReport written to', out_path)
