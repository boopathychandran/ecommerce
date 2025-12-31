import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro1.settings')
import django
django.setup()
from django.template.loader import get_template

try:
    tmpl = get_template('login/ecommerce_modern.html')
    print('Template parsed OK')
except Exception as e:
    print('Template parse error:')
    raise
