#!/usr/bin/env python
"""
Script pour réinitialiser le mot de passe d'un utilisateur
"""
import os
import django
import sys

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import User

def reset_password(username, new_password):
    """Réinitialise le mot de passe d'un utilisateur"""
    try:
        user = User.objects.get(username=username)
        user.set_password(new_password)
        user.save()
        print(f"✅ Password reset successful for user: {username}")
        print(f"   New password: {new_password}")
        print(f"\n🌐 You can now login at: http://127.0.0.1:8000/accounts/login/")
        return True
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found!")
        return False

def list_users():
    """Liste tous les utilisateurs"""
    print("\n📊 Available users:")
    print("-" * 50)
    for user in User.objects.all():
        print(f"  - {user.username} ({user.email or 'no email'})")
    print("-" * 50)

if __name__ == '__main__':
    print("=" * 70)
    print("🔐 USER PASSWORD RESET")
    print("=" * 70)
    
    if len(sys.argv) < 2:
        list_users()
        print("\nUsage: python reset_user_password.py <username> [password]")
        print("Example: python reset_user_password.py nour admin123")
        print("\nIf no password provided, default is 'admin123'")
        sys.exit(1)
    
    username = sys.argv[1]
    password = sys.argv[2] if len(sys.argv) > 2 else 'admin123'
    
    reset_password(username, password)
