import os
import django

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro1.settings')
django.setup()

from login.models import Product

with open('product_list.txt', 'w', encoding='utf-8') as f:
    f.write("--- START PRODUCT LIST ---\n")
    products = Product.objects.all()
    if not products:
        f.write("No products found.\n")
    else:
        for p in products:
            # Sanitize strings to remove newlines
            name = str(p.name).replace('\n', ' ').strip()
            category = str(p.category).replace('\n', ' ').strip()
            f.write(f"ID: {p.id} | Name: {name} | Category: {category} | Price: {p.price}\n")
    f.write("--- END PRODUCT LIST ---\n")
