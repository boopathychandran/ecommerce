import os
import django
from django.conf import settings
from django.template import Template, Context

# Setup Django minimal settings if not already configured
if not settings.configured:
    settings.configure(
        TEMPLATES=[{
            'BACKEND': 'django.template.backends.django.DjangoTemplates',
            'DIRS': [],
            'APP_DIRS': True,
        }],
        INSTALLED_APPS=['login', 'django.contrib.contenttypes', 'django.contrib.auth'],
        BASE_DIR=os.path.dirname(os.path.abspath(__file__)),
        DATABASES={'default': {'ENGINE': 'django.db.backends.sqlite3', 'NAME': ':memory:'}}
    )
    django.setup()

def check_templates():
    template_dir = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login'
    templates = [
        'ecommerce_modern.html',
        'wishlist.html',
        'cart.html',
        'product_detail.html',
        'login_modern.html',
        'address.html',
        'payment.html'
    ]
    
    for t_name in templates:
        t_path = os.path.join(template_dir, t_name)
        if not os.path.exists(t_path):
            continue
            
        try:
            with open(t_path, 'r', encoding='utf-8') as f:
                content = f.read()
            Template(content)
            print(f"SUCCESS: {t_name}")
        except Exception as e:
            print(f"ERROR: {t_name} - {e}")

if __name__ == "__main__":
    check_templates()
