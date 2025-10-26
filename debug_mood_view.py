#!/usr/bin/env python
"""
Script de débogage pour simuler la vue mood et voir les données générées
"""
import os
import django
from datetime import datetime, timedelta
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from core.models import MoodAnalysis, User

def simulate_mood_view(username):
    print("=" * 60)
    print(f"SIMULATION: mood view for user '{username}'")
    print("=" * 60)
    
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return
    
    print(f"\n👤 User: {user.username}")
    
    # Weekly trend (last 14 days) - Same logic as view
    fourteen_days_ago = timezone.now() - timedelta(days=14)
    daily_moods = []
    
    print(f"\n📅 Analyzing from {fourteen_days_ago.strftime('%Y-%m-%d %H:%M')} to {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    print("\n" + "-" * 60)
    
    for i in range(14):
        day = fourteen_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_analyses = MoodAnalysis.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        )
        
        day_str = day.strftime('%a %Y-%m-%d')
        
        if day_analyses.exists():
            # Calculate average positivity score
            avg_positif = sum(a.scores.get('positif', 0) for a in day_analyses) / day_analyses.count()
            avg_negatif = sum(a.scores.get('negatif', 0) + a.scores.get('colere', 0) + a.scores.get('tristesse', 0) for a in day_analyses) / day_analyses.count()
            positivity = avg_positif - avg_negatif
            
            print(f"{day_str}: {day_analyses.count()} analyses → positivity={round(positivity, 2)}")
            print(f"   avg_positif={avg_positif:.3f}, avg_negatif={avg_negatif:.3f}")
            
            daily_moods.append({
                'date': day.strftime('%a'),
                'positivity': round(positivity, 2)
            })
        else:
            print(f"{day_str}: No data → positivity=null")
            daily_moods.append({
                'date': day.strftime('%a'),
                'positivity': None
            })
    
    print("\n" + "-" * 60)
    print("\n📊 Generated daily_moods data:")
    print(json.dumps(daily_moods, indent=2))
    
    # Check if there's any data
    has_data = any(item['positivity'] is not None for item in daily_moods)
    print(f"\n✅ Has data: {has_data}")
    
    if has_data:
        non_null_count = sum(1 for item in daily_moods if item['positivity'] is not None)
        print(f"📈 Days with data: {non_null_count}/14")
    else:
        print("⚠️ No data in the last 14 days - 'No data' message should display")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    # Test all users with analyses
    users = User.objects.all()
    
    print("\n🔍 Testing all users:")
    print("-" * 60)
    
    for user in users:
        count = MoodAnalysis.objects.filter(user=user).count()
        if count > 0:
            print(f"\n{'='*60}")
            simulate_mood_view(user.username)
