#!/usr/bin/env python
"""
Debug template context
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIAnalysisService, AIRecommendationService
from core.models import Souvenir
from django.contrib.auth import get_user_model
from django.core.paginator import Paginator

User = get_user_model()
user = User.objects.get(username='noura')

print(f"🔍 Debug Template Context for user: {user.username}")
print()

# Simulate the view logic
souvenirs = Souvenir.objects.filter(utilisateur=user)

# Get AI insights
insights = AIRecommendationService.get_memory_insights(user)

# Album suggestions
album_suggestions = AIAnalysisService.generate_album_suggestions(user)

# Reflection prompts
reflection_prompts = AIRecommendationService.suggest_reflection_prompts(user)

print(f"album_suggestions: {album_suggestions}")
print(f"reflection_prompts: {reflection_prompts}")
print()

# Check the condition
condition = album_suggestions or reflection_prompts
print(f"Condition (album_suggestions or reflection_prompts): {condition}")
print(f"album_suggestions is truthy: {bool(album_suggestions)}")
print(f"reflection_prompts is truthy: {bool(reflection_prompts)}")
print()

# Check types and lengths
print(f"album_suggestions type: {type(album_suggestions)}")
print(f"reflection_prompts type: {type(reflection_prompts)}")
print(f"album_suggestions length: {len(album_suggestions) if album_suggestions else 0}")
print(f"reflection_prompts length: {len(reflection_prompts) if reflection_prompts else 0}")