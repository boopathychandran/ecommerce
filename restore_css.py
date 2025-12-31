import shutil
import os

source = 'static/css/ecommerce-home.css'
dest = 'static/css/modern-gradient.css'

try:
    # Try reading as utf-8 first
    with open(source, 'r', encoding='utf-8') as f:
        content = f.read()
except UnicodeDecodeError:
    # Fallback to latin-1 or similar if utf-8 fails
    with open(source, 'r', encoding='latin-1') as f:
        content = f.read()

# Write to destination
with open(dest, 'w', encoding='utf-8') as f:
    f.write(content)

print(f"Successfully copied {len(content)} bytes from {source} to {dest}")
