#!/usr/bin/env python
"""
Debug album suggestions with IDs
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIAnalysisService
from core.models import Souvenir
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='noura')

print(f"🔍 Debug Album Suggestions with IDs for user: {user.username}")
print()

# Get album suggestions with IDs
suggestions = AIAnalysisService.generate_album_suggestions(user)

# Add souvenir IDs to suggestions
for suggestion in suggestions:
    suggestion['souvenir_ids'] = AIAnalysisService.get_souvenir_ids_for_suggestion(
        user, 
        suggestion['type'], 
        suggestion.get('theme'), 
        suggestion.get('year')
    )

print(f"Generated suggestions with IDs: {len(suggestions)}")
print()

for i, suggestion in enumerate(suggestions, 1):
    print(f"{i}. {suggestion['title']} ({suggestion['count']} items) - Type: {suggestion['type']}")
    print(f"   Souvenir IDs: {suggestion['souvenir_ids']}")
    print(f"   URL params: souvenirs={'&souvenirs='.join(map(str, suggestion['souvenir_ids']))}")
    print()

# Verify IDs exist
all_souvenir_ids = Souvenir.objects.filter(utilisateur=user).values_list('id', flat=True)
print(f"All user souvenir IDs: {list(all_souvenir_ids)}")

for suggestion in suggestions:
    for sid in suggestion['souvenir_ids']:
        if sid not in all_souvenir_ids:
            print(f"❌ ERROR: Souvenir ID {sid} not found in user's souvenirs!")
        else:
            print(f"✅ Souvenir ID {sid} is valid")