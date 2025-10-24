#!/usr/bin/env python
import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIAnalysisService
from django.contrib.auth import get_user_model
from collections import Counter

User = get_user_model()
user = User.objects.get(username='noura')

# Check theme distribution
from core.models import Souvenir
souvenirs = Souvenir.objects.filter(utilisateur=user)
themes = [s.theme for s in souvenirs if s.theme != 'other']
theme_counts = Counter(themes)
print('Theme counts:', dict(theme_counts))

# Check what suggestions are generated
suggestions = AIAnalysisService.generate_album_suggestions(user)
print(f'\nGenerated {len(suggestions)} suggestions:')
for i, s in enumerate(suggestions, 1):
    print(f'{i}. {s["title"]} ({s["count"]} items) - Type: {s["type"]}')
    if s['type'] == 'theme':
        print(f'   Should select theme: {s["theme"]}')
    elif s['type'] == 'year':
        print(f'   Should select year: {s["year"]}')
    elif s['type'] == 'ai_analyzed':
        print('   Should select AI-analyzed memories')

# Test the selection logic
print('\nTesting selection logic:')
for suggestion in suggestions:
    ids = AIAnalysisService.get_souvenir_ids_for_suggestion(
        user, suggestion['type'], suggestion.get('theme'), suggestion.get('year')
    )
    print(f'{suggestion["title"]}: {len(ids)} souvenirs selected')