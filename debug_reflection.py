#!/usr/bin/env python
"""
Debug reflection prompts
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIRecommendationService
from core.models import Souvenir
from django.contrib.auth import get_user_model

User = get_user_model()
user = User.objects.get(username='noura')

print(f"🔍 Debug Reflection Prompts for user: {user.username}")
print()

# Get insights first
insights = AIRecommendationService.get_memory_insights(user)
print(f"Insights: {insights}")
print()

# Generate reflection prompts
reflection_prompts = AIRecommendationService.suggest_reflection_prompts(user)
print(f"🎯 Generated reflection prompts: {len(reflection_prompts)}")

if reflection_prompts:
    for i, prompt in enumerate(reflection_prompts, 1):
        print(f"{i}. {prompt}")
else:
    print("❌ No reflection prompts generated")

print()
print("Album suggestions (for comparison):")
from core.ai_services import AIAnalysisService
album_suggestions = AIAnalysisService.generate_album_suggestions(user)
print(f"Album suggestions: {len(album_suggestions)}")
if album_suggestions:
    for i, s in enumerate(album_suggestions, 1):
        print(f"{i}. {s['title']} ({s['count']} items) - Type: {s['type']}")