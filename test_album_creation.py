#!/usr/bin/env python
"""
Test album creation with pre-selected souvenirs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.test import RequestFactory
from django.contrib.auth import get_user_model
from core.views import creer_album
from core.ai_services import AIAnalysisService

User = get_user_model()
user = User.objects.get(username='noura')

print("🧪 Testing album creation with pre-selected souvenirs")
print()

# Get suggestions
suggestions = AIAnalysisService.generate_album_suggestions(user)
for suggestion in suggestions:
    suggestion['souvenir_ids'] = AIAnalysisService.get_souvenir_ids_for_suggestion(
        user, suggestion['type'], suggestion.get('theme'), suggestion.get('year')
    )

# Test the AI-Enriched Memories suggestion
ai_suggestion = next(s for s in suggestions if s['type'] == 'ai_analyzed')
print(f"Testing suggestion: {ai_suggestion['title']}")
print(f"Souvenir IDs: {ai_suggestion['souvenir_ids']}")
print()

# Create a mock request to test the view
factory = RequestFactory()
request = factory.get(f'/albums/create/?souvenirs={"&souvenirs=".join(str(id) for id in ai_suggestion["souvenir_ids"])}&title={ai_suggestion["title"]}&description=AI-generated album')
request.user = user

# Call the view
response = creer_album(request)

# Check if the response contains the preselected IDs
if hasattr(response, 'context_data'):
    context = response.context_data
    print(f"Preselected IDs in context: {context.get('preselected_ids', [])}")
    print(f"Preselected title: {context.get('preselected_title', '')}")
    print(f"Preselected description: {context.get('preselected_description', '')}")
else:
    print("Response doesn't have context_data")

print("✅ Test completed")