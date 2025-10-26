#!/usr/bin/env python
"""
Test pour voir exactement ce que le template mood.html reçoit
"""
import os
import django
from datetime import datetime, timedelta
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from django.db.models import Count
from core.models import MoodAnalysis, User

def test_mood_template_data(username):
    """
    Simule exactement ce que la vue mood() fait et affiche les données
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User not found: {username}")
        return
    
    print(f"{'='*70}")
    print(f"Testing mood template data for: {user.username}")
    print(f"{'='*70}\n")
    
    # === MOOD STATS (Last 30 days) ===
    print("📊 MOOD STATS (Last 30 days)")
    print("-" * 70)
    thirty_days_ago = timezone.now() - timedelta(days=30)
    mood_stats = MoodAnalysis.objects.filter(
        user=user,
        created_at__gte=thirty_days_ago
    ).values('top').annotate(count=Count('top')).order_by('-count')
    
    mood_stats_list = list(mood_stats)
    print(f"mood_stats type: {type(mood_stats_list)}")
    print(f"mood_stats length: {len(mood_stats_list)}")
    print(f"mood_stats content:\n{json.dumps(mood_stats_list, indent=2)}")
    
    # === DAILY MOODS (Last 14 days) ===
    print(f"\n📈 DAILY MOODS (Last 14 days)")
    print("-" * 70)
    fourteen_days_ago = timezone.now() - timedelta(days=14)
    daily_moods = []
    
    print(f"Period: {fourteen_days_ago.strftime('%Y-%m-%d')} to {timezone.now().strftime('%Y-%m-%d')}\n")
    
    for i in range(14):
        day = fourteen_days_ago + timedelta(days=i)
        day_start = day.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        
        day_analyses = MoodAnalysis.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        )
        
        if day_analyses.exists():
            avg_positif = sum(a.scores.get('positif', 0) for a in day_analyses) / day_analyses.count()
            avg_negatif = sum(a.scores.get('negatif', 0) + a.scores.get('colere', 0) + a.scores.get('tristesse', 0) for a in day_analyses) / day_analyses.count()
            positivity = avg_positif - avg_negatif
            
            daily_moods.append({
                'date': day.strftime('%a'),
                'positivity': round(positivity, 2)
            })
            print(f"  {day.strftime('%a %Y-%m-%d')}: {day_analyses.count()} analyses → {round(positivity, 2)}")
        else:
            daily_moods.append({
                'date': day.strftime('%a'),
                'positivity': None
            })
            print(f"  {day.strftime('%a %Y-%m-%d')}: No data → null")
    
    print(f"\ndaily_moods type: {type(daily_moods)}")
    print(f"daily_moods length: {len(daily_moods)}")
    print(f"\ndaily_moods as JSON (what template receives):")
    print(json.dumps(daily_moods, indent=2))
    
    has_data = any(item['positivity'] is not None for item in daily_moods)
    print(f"\n✅ Has data: {has_data}")
    
    if has_data:
        non_null = [item for item in daily_moods if item['positivity'] is not None]
        print(f"📊 Days with data: {len(non_null)}/14")
        
        # Show what JavaScript will see
        print(f"\n🟨 JavaScript will extract:")
        print(f"   Labels: {[item['date'] for item in daily_moods]}")
        print(f"   Data:   {[item['positivity'] for item in daily_moods]}")
    
    # Test context dict
    print(f"\n{'='*70}")
    print("📦 FULL CONTEXT DICT (what render() receives)")
    print("-" * 70)
    context = {
        'mood_stats': mood_stats_list,
        'daily_moods': daily_moods,
    }
    
    for key, value in context.items():
        print(f"{key}:")
        if isinstance(value, list):
            print(f"  Type: list, Length: {len(value)}")
            if len(value) > 0:
                print(f"  First item: {value[0]}")
        else:
            print(f"  Type: {type(value)}, Value: {value}")
    
    print(f"\n{'='*70}")
    print("✅ Template data simulation complete!")
    print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        username = 'mejriwajih'  # Default
    
    test_mood_template_data(username)
