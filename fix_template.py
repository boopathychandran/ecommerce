"""
Fix corrupted ecommerce_modern.html template file
"""

import re

file_path = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login\ecommerce_modern.html'

# Read the raw content
with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
    content = f.read()

# The file is corrupted. Let's reconstruct the problematic section (lines 107-112)
# We'll use string replacement to fix the specific corrupted section

# Find where the corruption starts - around "Welcome back"
welcome_section_corrupted_pattern = r'\u003ch2 class="welcome-title glitch-text"[^}]+Welcome back,.*?endif %\}\u003c/span\u003e!\s*\u003c/h2\u003e'

# The correct replacement content
correct_welcome_section = '''        \u003ch2 class="welcome-title glitch-text"
          style="font-size: 3rem; margin-bottom: 1rem; font-weight: 800; color: white;"\u003e
          Welcome back,
          \u003cspan class="username rainbow-text"\u003e{% if user.first_name %}{{ user.first_name }}{% else %}Tech Enthusiast{% endif %}\u003c/span\u003e!
        \u003c/h2\u003e'''

# Try to fix using regex
content_fixed = re.sub(welcome_section_corrupted_pattern, correct_welcome_section, content, flags=re.DOTALL)

# If that didn't work, we need to be more precise
# Let's split by lines and rebuild the section manually
lines = content.split('\n')

# Find the line starting with welcome content
fixed_lines = []
skip_until_line = -1

for i, line in enumerate(lines):
    if skip_until_line \u003e 0 and i \u003c= skip_until_line:
        continue  # Skip corrupted lines
    
    # Check if this is the start of the corrupted section
    if 'welcome-content' in line and 'text-align: center' in line:
        fixed_lines.append(line)
        # Next should be the h2 tag - replace the corrupted section
        # Skip the next corrupted lines and insert the correct content
        skip_until_line = i + 10  # Skip ahead
        fixed_lines.extend([
            '        \u003ch2 class="welcome-title glitch-text"',
            '          style="font-size: 3rem; margin-bottom: 1rem; font-weight: 800; color: white;"\u003e',
            '          Welcome back,',
            '          \u003cspan class="username rainbow-text"\u003e{% if user.first_name %}{{ user.first_name }}{% else %}Tech Enthusiast{% endif %}\u003c/span\u003e!',
            '        \u003c/h2\u003e',
            '        \u003cp class="welcome-subtitle"',
            '          style="color: var(--text-muted); font-size: 1.2rem; max-width: 600px; margin: 0 auto 3rem;"\u003e',
            '          Discover the latest tech innovations that shape tomorrow',
            '        \u003c/p\u003e'
        ])
        # Find where to continue (after the \u003c/p\u003e of welcome-subtitle)
        for j in range(i+1, min(i+20, len(lines))):
            if '\u003cdiv class="welcome-stats"' in lines[j]:
                skip_until_line = j - 1
                break
    else:
        fixed_lines.append(line)

# Write the fixed content
content_fixed = '\n'.join(fixed_lines)

# Create a backup first
with open(file_path + '.backup', 'w', encoding='utf-8') as f:
    f.write(content)
print("Backup created at:", file_path + '.backup')

# Write the fixed file
with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content_fixed)

print("File fixed successfully!")
print("Lines processed:", len(fixed_lines))
