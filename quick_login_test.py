#!/usr/bin/env python
"""
Test rapide du login
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.contrib.auth import authenticate

username = 'mejriwajih'
password = 'admin123'

print(f"🔍 Testing login for: {username}")
user = authenticate(username=username, password=password)

if user:
    print(f"✅ LOGIN SUCCESSFUL!")
    print(f"   User: {user.username}")
    print(f"   Email: {user.email}")
    print(f"   Active: {user.is_active}")
    print(f"\n🎉 You can now login with:")
    print(f"   Username: {username}")
    print(f"   Password: {password}")
    print(f"\n🌐 URL: http://127.0.0.1:8000/accounts/login/")
else:
    print(f"❌ LOGIN FAILED!")
