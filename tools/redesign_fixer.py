import os

files = [
    r'login/templates/login/cart.html',
    r'login/templates/login/product_detail.html'
]

base_dir = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce'

for relative_path in files:
    file_path = os.path.join(base_dir, relative_path)
    if not os.path.exists(file_path):
        print(f"File not found: {file_path}")
        continue
    
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # 1. CSS Replacement
    if 'future-tech.css' in content and 'light-neon.css' not in content:
        content = content.replace("static 'css/future-tech.css'", "static 'css/light-neon.css'")
        print(f"Updated CSS in {relative_path}")
    
    # 2. Text Color Replacement (Hardcoded white to variable)
    # Be careful not to break hex codes like #ffffff if used in other contexts, but 'color: white' is safe.
    content = content.replace('color: white', 'color: var(--text-main)')
    content = content.replace('color: #fff;', 'color: var(--text-main);') # Semicolon to be safe
    content = content.replace('color: #ffffff;', 'color: var(--text-main);')

    # 3. Add Transitions Script
    if 'js/transitions.js' not in content:
        content = content.replace('</body>', '<script src="{% static \'js/transitions.js\' %}"></script>\n</body>')
        print(f"Added script to {relative_path}")

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

print("Redesign Fix Complete")
