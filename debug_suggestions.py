#!/usr/bin/env python
"""
Debug album suggestions
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
from collections import Counter

User = get_user_model()
user = User.objects.get(username='noura')
souvenirs = Souvenir.objects.filter(utilisateur=user)

print(f"🔍 Debug Album Suggestions for user: {user.username}")
print(f"Total souvenirs: {souvenirs.count()}")
print()

# Check themes
themes = [s.theme for s in souvenirs if s.theme != 'other']
theme_counts = Counter(themes)
print(f"Themes distribution: {dict(theme_counts)}")

# Check years
years = [s.date_evenement.year for s in souvenirs]
year_counts = Counter(years)
print(f"Years distribution: {dict(year_counts)}")

# Check favorites
favorites = souvenirs.filter(is_favorite=True).count()
print(f"Favorites count: {favorites}")

# Check AI analyzed
analyzed = souvenirs.filter(ai_analyzed=True).count()
print(f"AI analyzed count: {analyzed}")
print()

# Generate suggestions
suggestions = AIAnalysisService.generate_album_suggestions(user)
print(f"🎯 Generated suggestions: {len(suggestions)}")

if suggestions:
    for i, s in enumerate(suggestions, 1):
        print(f"{i}. {s['title']} ({s['count']} items) - Type: {s['type']}")
else:
    print("❌ No suggestions generated")
    print("Checking why...")

    # Debug conditions
    print(f"- Theme suggestions (>=2 same theme): {any(count >= 2 for count in theme_counts.values())}")
    print(f"- Year suggestions (>=3 same year): {any(count >= 3 for count in year_counts.values())}")
    print(f"- Favorite suggestions (>=2 favorites): {favorites >= 2}")
    print(f"- AI analyzed suggestions (>=2 analyzed): {analyzed >= 2}")

print()
print("Sample souvenirs:")
for s in souvenirs[:3]:
    print(f"- {s.titre} (theme: {s.theme}, year: {s.date_evenement.year}, favorite: {s.is_favorite}, ai: {s.ai_analyzed})")