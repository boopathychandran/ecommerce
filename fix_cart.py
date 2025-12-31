import os

def fix_cart_template():
    file_path = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login\cart.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Fix the missing space and invalid operator
    new_content = content.replace('item.product.stock> 0', 'item.product.stock > 0')
    new_content = new_content.replace('item.product.stock<= 5', 'item.product.stock <= 5')
    
    # Also join broken tags if any
    lines = new_content.splitlines()
    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        if '{% if' in line and not '%}' in line and i + 1 < len(lines):
            next_line = lines[i+1]
            if '%}' in next_line:
                joined = line.strip() + " " + next_line.lstrip()
                new_lines.append(joined)
                i += 2
                continue
        new_lines.append(line)
        i += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.write("\n".join(new_lines))
    print("Cart template fixed via script!")

if __name__ == "__main__":
    fix_cart_template()
