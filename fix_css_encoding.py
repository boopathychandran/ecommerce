import shutil
import os

source = 'static/css/ecommerce-home.css'
dest = 'static/css/modern-gradient.css'

# The file seems to have a BOM for UTF-16 LE
# We will read it as utf-16 and write as utf-8
try:
    with open(source, 'r', encoding='utf-16') as f:
        content = f.read()
    
    with open(dest, 'w', encoding='utf-8') as f:
        f.write(content)
        
    print(f"Success: Converted {source} (UTF-16) to {dest} (UTF-8)")
except Exception as e:
    print(f"Error: {e}")
