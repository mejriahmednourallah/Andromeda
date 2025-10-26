#!/usr/bin/env python
"""
Script pour tester et vérifier les utilisateurs disponibles
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.contrib.auth import authenticate
from core.models import User

def test_login():
    print("=" * 70)
    print("🔐 TEST: Login System")
    print("=" * 70)
    
    # List all users
    users = User.objects.all()
    print(f"\n📊 Total users in database: {users.count()}")
    
    if users.count() == 0:
        print("\n❌ No users found! Creating a test user...")
        user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        print(f"✅ Test user created: {user.username}")
    
    print("\n" + "-" * 70)
    print("Available users:")
    print("-" * 70)
    
    for user in User.objects.all():
        print(f"\n👤 Username: {user.username}")
        print(f"   Email: {user.email or 'N/A'}")
        print(f"   Active: {user.is_active}")
        print(f"   Staff: {user.is_staff}")
        print(f"   Superuser: {user.is_superuser}")
        print(f"   Last login: {user.last_login or 'Never'}")
        print(f"   Date joined: {user.date_joined}")
    
    # Test authentication
    print("\n" + "=" * 70)
    print("🧪 Testing Authentication")
    print("=" * 70)
    
    test_cases = [
        ('mejriwajih', 'admin'),
        ('nour', 'admin'),
        ('demo', 'demo123'),
        ('testuser', 'testpass123'),
    ]
    
    for username, password in test_cases:
        if User.objects.filter(username=username).exists():
            print(f"\n🔍 Testing: {username} / {password}")
            user = authenticate(username=username, password=password)
            if user:
                print(f"   ✅ Authentication successful!")
                print(f"   User: {user.username} | Active: {user.is_active}")
            else:
                print(f"   ❌ Authentication failed!")
                # Try to check if user exists but password is wrong
                if User.objects.filter(username=username).exists():
                    print(f"   ⚠️  User exists but password might be incorrect")
        else:
            print(f"\n⏭️  Skipping {username} (user doesn't exist)")
    
    print("\n" + "=" * 70)
    print("📝 Recommendations:")
    print("=" * 70)
    print("\n1. Try logging in with one of the usernames above")
    print("2. If you don't know the password, use 'Forgot Password' link")
    print("3. Or create a new account using the signup page")
    print("\n🌐 Login URL: http://127.0.0.1:8000/accounts/login/")
    print("🌐 Signup URL: http://127.0.0.1:8000/accounts/signup/")
    print("=" * 70)

if __name__ == '__main__':
    test_login()
