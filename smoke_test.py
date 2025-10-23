#!/usr/bin/env python
"""
Smoke test script to confirm login and signup pages load without errors.
"""

import os
import sys
import django
from django.test import Client
from django.conf import settings

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

def test_pages():
    client = Client()
    pages = [
        '/accounts/login/',
        '/accounts/signup/',
    ]
    for page in pages:
        try:
            response = client.get(page)
            if response.status_code == 200:
                print(f"✓ {page} loads successfully")
            else:
                print(f"✗ {page} returned status {response.status_code}")
        except Exception as e:
            print(f"✗ {page} failed with error: {e}")

if __name__ == '__main__':
    test_pages()