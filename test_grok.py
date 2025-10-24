#!/usr/bin/env python
"""
Test script to verify Grok API connection
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.conf import settings
import requests

def test_grok_api():
    print("🔍 Testing Grok API connection...")

    # Check if API key is set
    api_key = getattr(settings, 'GROK_API_KEY', None)
    if not api_key:
        print("❌ GROK_API_KEY not found in settings")
        print("💡 Get your free Grok API key at: https://console.x.ai")
        return False

    print(f"✅ API Key found: {api_key[:20]}...")

    try:
        url = "https://api.x.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }

        data = {
            "model": "grok-beta",
            "messages": [{"role": "user", "content": "Hello, this is a test message"}],
            "max_tokens": 10,
            "temperature": 0.1
        }

        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()

        result = response.json()['choices'][0]['message']['content'].strip()
        print(f"✅ Grok API call successful! Response: '{result}'")
        return True

    except requests.exceptions.HTTPError as e:
        if response.status_code == 401:
            print(f"❌ Authentication failed: {e}")
        elif response.status_code == 429:
            print(f"❌ Rate limit exceeded: {e}")
        else:
            print(f"❌ HTTP error: {e}")
        return False
    except Exception as e:
        print(f"❌ Unexpected error: {e}")
        return False

if __name__ == "__main__":
    success = test_grok_api()
    if success:
        print("\n🎉 Grok API is working correctly!")
        sys.exit(0)
    else:
        print("\n💥 Grok API test failed!")
        sys.exit(1)