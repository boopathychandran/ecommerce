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

def debug_template():
    template_path = r'c:\Users\LENOVO\Desktop\gurutech\encahnceed django-ecommerce\login\templates\login\ecommerce_modern.html'
    try:
        with open(template_path, 'r', encoding='utf-8') as f:
            template_content = f.read()
        
        # We need to simulate the environment
        # The error is likely a SyntaxError during parsing
        Template(template_content)
        print("Template parsed successfully!")
    except Exception as e:
        print(f"Error parsing template: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    debug_template()
