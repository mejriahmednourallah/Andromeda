#!/usr/bin/env python
"""
Vérifier les timestamps exacts des analyses mood
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from datetime import timedelta
from core.models import MoodAnalysis, User

username = 'mejriwajih'
user = User.objects.get(username=username)

print(f"📊 MoodAnalysis timestamps for {username}")
print(f"Current time (timezone.now()): {timezone.now()}")
print("=" * 70)

analyses = MoodAnalysis.objects.filter(user=user).order_by('-created_at')[:20]

for analysis in analyses:
    age = timezone.now() - analysis.created_at
    age_days = age.total_seconds() / 86400
    
    print(f"{analysis.created_at} | {analysis.top:8s} | Age: {age_days:.2f} days")

print("=" * 70)

# Check what would be in the 14-day window
fourteen_days_ago = timezone.now() - timedelta(days=14)
print(f"\n14-day window starts at: {fourteen_days_ago}")
print(f"14-day window ends at:   {timezone.now()}")

in_window = MoodAnalysis.objects.filter(
    user=user,
    created_at__gte=fourteen_days_ago
)

print(f"\n✅ Analyses in 14-day window: {in_window.count()}")

if in_window.exists():
    print("\nAnalyses in window:")
    for analysis in in_window.order_by('created_at'):
        print(f"  {analysis.created_at} | {analysis.top}")
