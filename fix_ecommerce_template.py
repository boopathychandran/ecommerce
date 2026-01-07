file_path = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login\ecommerce_modern.html'

# Read file
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# Make backup
with open(file_path + '.bak', 'w', encoding='utf-8') as f:
    f.writelines(lines)

# Fix lines 110-111 (index 109-110)
# The problem is on line 110 where the if statement is broken across two lines
corrected_line = '          <span class="username rainbow-text">{% if user.first_name %}{{ user.first_name }}{% else %}Tech Enthusiast{% endif %}</span>!\r\n'
lines[109] = corrected_line
del lines[110]  # Remove the broken continuation line

# Write fixed file
with open(file_path, 'w', encoding='utf-8') as f:
    f.writelines(lines)

print('File fixed successfully!')
print('Backup saved to:', file_path + '.bak')
