#!/usr/bin/env python3
"""Debug script: exercise the payment view via Django test client.

Creates a test user (if missing), ensures at least one Product exists,
sets a session cart and address, and performs a GET on `/payment/`.
Prints status code and a trimmed response or prints the exception traceback.
"""
import os
import sys
from decimal import Decimal

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'pro1.settings')
import django
django.setup()

import traceback
from django.test import Client
from django.contrib.auth.models import User
from login.models import Product


def main():
    try:
        username = 'debug_pay_user'
        password = 'debug-pass-123'
        user, created = User.objects.get_or_create(username=username, defaults={'email': 'debug@example.com'})
        if created:
            user.set_password(password)
            user.save()

        # Ensure at least one product exists
        product = Product.objects.first()
        if not product:
            product = Product.objects.create(name='Debug Product', price=Decimal('123.45'), stock=10)

        client = Client()
        logged = client.login(username=username, password=password)
        print('Logged in:', logged)

        # Prepare session: cart with one quantity and a basic address
        session = client.session
        session['cart'] = {str(product.id): 1}
        session['address'] = {
            'name': 'Debug User',
            'address': '123 Debug Lane',
            'city': 'DebugCity',
            'pincode': '000000',
            'phone': '0000000000',
        }
        session.save()

        print('Requesting /payment/ ...')
        resp = client.get('/payment/')
        print('Status code:', resp.status_code)
        content = resp.content.decode('utf-8', errors='replace')
        print('Response (first 1000 chars):')
        print(content[:1000])

    except Exception:
        print('Exception during debug run:')
        traceback.print_exc()


if __name__ == '__main__':
    main()
