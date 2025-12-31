import os

def fix_template():
    file_path = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login\ecommerce_modern.html'
    with open(file_path, 'r', encoding='utf-8') as f:
        lines = f.readlines()

    new_lines = []
    i = 0
    while i < len(lines):
        line = lines[i]
        # Check for broken tag across two lines
        if '{% if' in line and not '%}' in line and i + 1 < len(lines):
            next_line = lines[i+1]
            if '%}' in next_line:
                # Merge them
                joined = line.strip() + " " + next_line.lstrip()
                new_lines.append(joined)
                i += 2
                continue
        
        # Specific fix for the category checkbox issue
        if 'checked{%' in line and i + 1 < len(lines) and 'endif %}' in lines[i+1]:
            joined = line.strip() + " " + lines[i+1].lstrip()
            new_lines.append(joined)
            i += 2
            continue
            
        new_lines.append(line)
        i += 1

    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Template fixed via script!")

if __name__ == "__main__":
    fix_template()
