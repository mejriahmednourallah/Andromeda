#!/usr/bin/env python
"""Smoke test script to confirm login and signup pages load without errors."""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.test import Client

def test_pages():
    """Test that authentication pages load successfully"""
    client = Client()
    pages = ['/accounts/login/', '/accounts/signup/']
    
    for page in pages:
        try:
            response = client.get(page)
            status = "✓" if response.status_code == 200 else "✗"
            print(f"{status} {page} - Status {response.status_code}")
        except Exception as e:
            print(f"✗ {page} - Error: {e}")

if __name__ == '__main__':
    test_pages()