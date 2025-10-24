#!/usr/bin/env python
"""
Test script for AI message generation endpoint
"""
import os
import django
import requests
from django.test import Client
from django.contrib.auth.models import User

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

def test_ai_message_generation():
    """Test the AI message generation endpoint"""
    print("Testing AI message generation...")

    # Create a test client
    client = Client()

    # Create or get a test user
    user, created = User.objects.get_or_create(
        username='testuser',
        defaults={
            'email': 'test@example.com',
            'first_name': 'Test',
            'last_name': 'User'
        }
    )
    if created:
        user.set_password('testpass123')
        user.save()
        print("Created test user")

    # Login the user
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login successful: {login_success}")

    # Test the AI message generation endpoint
    response = client.post('/capsules/generate-message/', {
        'titre': 'Mon premier voyage à Tokyo',
        'description': 'J\'ai exploré Shibuya, goûté des sushis frais et rencontré des personnes formidables. Une expérience inoubliable.',
        'csrfmiddlewaretoken': 'dummy'  # Django will handle this
    }, HTTP_X_REQUESTED_WITH='XMLHttpRequest')

    print(f"Response status: {response.status_code}")
    print(f"Response content: {response.content.decode()}")

    if response.status_code == 200:
        try:
            data = response.json()
            print("Success! AI generated message:")
            print(f"Message: {data.get('message', 'N/A')}")
            print(f"Emotion: {data.get('emotion', 'N/A')}")
        except:
            print("Response is not valid JSON")
    else:
        print(f"Error: {response.status_code}")

if __name__ == '__main__':
    test_ai_message_generation()