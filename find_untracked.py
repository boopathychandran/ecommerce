import os
import subprocess

def get_tracked_files():
    res = subprocess.run(['git', 'ls-files'], capture_output=True, text=True)
    return set(os.path.normpath(f) for f in res.stdout.splitlines())

tracked = get_tracked_files()
for root, dirs, files in os.walk('.'):
    if any(p in root for p in ['.git', 'venv', '__pycache__', 'staticfiles']):
        continue
    for file in files:
        p = os.path.normpath(os.path.join(root, file))
        if p not in tracked:
            print(p)
