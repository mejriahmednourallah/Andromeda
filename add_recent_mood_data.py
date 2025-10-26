#!/usr/bin/env python
"""
Script pour ajouter des données mood récentes (derniers jours)
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from core.models import MoodAnalysis, User

def add_recent_data(username):
    """
    Ajoute des données pour les 7 derniers jours incluant aujourd'hui
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return
    
    print(f"✅ Adding recent mood data for user: {user.username}")
    print(f"📅 Current time: {timezone.now().strftime('%Y-%m-%d %H:%M')}")
    print("=" * 60)
    
    test_moods = [
        {'top': 'positif', 'scores': {'positif': 0.8, 'neutre': 0.1, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}, 'text': 'Je me sens bien aujourd\'hui!'},
        {'top': 'positif', 'scores': {'positif': 0.9, 'neutre': 0.05, 'negatif': 0.02, 'colere': 0.02, 'tristesse': 0.01}, 'text': 'Super journée productive'},
        {'top': 'neutre', 'scores': {'positif': 0.3, 'neutre': 0.5, 'negatif': 0.1, 'colere': 0.05, 'tristesse': 0.05}, 'text': 'Une journée normale'},
        {'top': 'positif', 'scores': {'positif': 0.85, 'neutre': 0.1, 'negatif': 0.03, 'colere': 0.01, 'tristesse': 0.01}, 'text': 'Excellente humeur!'},
        {'top': 'positif', 'scores': {'positif': 0.75, 'neutre': 0.15, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}, 'text': 'Bonne journée globalement'},
        {'top': 'neutre', 'scores': {'positif': 0.4, 'neutre': 0.4, 'negatif': 0.1, 'colere': 0.05, 'tristesse': 0.05}, 'text': 'Journée tranquille'},
        {'top': 'positif', 'scores': {'positif': 0.95, 'neutre': 0.03, 'negatif': 0.01, 'colere': 0.005, 'tristesse': 0.005}, 'text': 'Je suis au top!'},
    ]
    
    created_count = 0
    
    # Create data for the last 7 days including today
    for i in range(7):
        # Days ago (0 = today, 1 = yesterday, etc.)
        days_ago = 6 - i
        target_datetime = timezone.now() - timedelta(days=days_ago)
        
        # Use different mood patterns
        mood_data = test_moods[i % len(test_moods)]
        
        # Check if data already exists for this day
        day_start = target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        existing = MoodAnalysis.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).count()
        
        if existing > 0:
            print(f"⏭️  {target_datetime.strftime('%Y-%m-%d')} | Already has {existing} analysis(es) - skipping")
            continue
        
        analysis = MoodAnalysis.objects.create(
            user=user,
            text=mood_data['text'],
            top=mood_data['top'],
            scores=mood_data['scores'],
            source='test',
            model='test_generator',
            created_at=target_datetime
        )
        
        created_count += 1
        
        # Calculate positivity score
        positivity = mood_data['scores']['positif'] - (
            mood_data['scores']['negatif'] + 
            mood_data['scores']['colere'] + 
            mood_data['scores']['tristesse']
        )
        
        print(f"✅ {target_datetime.strftime('%Y-%m-%d %H:%M')} | {mood_data['top']:8s} | positivity={positivity:+.2f}")
    
    print("=" * 60)
    print(f"✅ Created {created_count} new mood analyses")
    
    # Show total count
    total = MoodAnalysis.objects.filter(user=user).count()
    print(f"📊 Total analyses for {user.username}: {total}")
    print(f"\n🌐 Now refresh: http://127.0.0.1:8000/mood/")
    print(f"   Login as: {user.username}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
    else:
        # Show available users
        print("Available users:")
        for user in User.objects.all():
            count = MoodAnalysis.objects.filter(user=user).count()
            print(f"  - {user.username} ({count} existing analyses)")
        
        print("\nUsage: python add_recent_mood_data.py <username>")
        print("Example: python add_recent_mood_data.py mejriwajih")
        sys.exit(1)
    
    add_recent_data(username)
