#!/usr/bin/env python
"""
Script pour ajouter des données de test pour le graphique mood
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from core.models import MoodAnalysis, User

def add_test_data(username, days=7):
    """
    Ajoute des données de test pour les X derniers jours
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        available_users = User.objects.all().values_list('username', flat=True)
        print(f"Available users: {', '.join(available_users)}")
        return
    
    print(f"✅ Adding test mood data for user: {user.username}")
    print(f"📅 Creating {days} days of test data")
    print("=" * 60)
    
    test_moods = [
        {'top': 'positif', 'scores': {'positif': 0.8, 'neutre': 0.1, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}},
        {'top': 'positif', 'scores': {'positif': 0.9, 'neutre': 0.05, 'negatif': 0.02, 'colere': 0.02, 'tristesse': 0.01}},
        {'top': 'neutre', 'scores': {'positif': 0.3, 'neutre': 0.5, 'negatif': 0.1, 'colere': 0.05, 'tristesse': 0.05}},
        {'top': 'negatif', 'scores': {'positif': 0.1, 'neutre': 0.2, 'negatif': 0.5, 'colere': 0.1, 'tristesse': 0.1}},
        {'top': 'positif', 'scores': {'positif': 0.85, 'neutre': 0.1, 'negatif': 0.03, 'colere': 0.01, 'tristesse': 0.01}},
        {'top': 'positif', 'scores': {'positif': 0.75, 'neutre': 0.15, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}},
        {'top': 'neutre', 'scores': {'positif': 0.4, 'neutre': 0.4, 'negatif': 0.1, 'colere': 0.05, 'tristesse': 0.05}},
    ]
    
    created_count = 0
    
    for i in range(days):
        # Create data for past days
        target_date = timezone.now() - timedelta(days=days-i-1)
        
        # Use different mood patterns
        mood_data = test_moods[i % len(test_moods)]
        
        analysis = MoodAnalysis.objects.create(
            user=user,
            text=f"Test mood entry for {target_date.strftime('%Y-%m-%d')}",
            top=mood_data['top'],
            scores=mood_data['scores'],
            source='test',
            model='test_generator',
            created_at=target_date
        )
        
        created_count += 1
        
        # Calculate positivity score
        positivity = mood_data['scores']['positif'] - (
            mood_data['scores']['negatif'] + 
            mood_data['scores']['colere'] + 
            mood_data['scores']['tristesse']
        )
        
        print(f"✅ {target_date.strftime('%Y-%m-%d %H:%M')} | {mood_data['top']:8s} | positivity={positivity:+.2f}")
    
    print("=" * 60)
    print(f"✅ Created {created_count} test mood analyses")
    print(f"\n🌐 Now visit: http://127.0.0.1:8000/mood/")
    print(f"   Login as: {user.username}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        days = int(sys.argv[2]) if len(sys.argv) > 2 else 7
    else:
        # Show available users
        print("Available users:")
        for user in User.objects.all():
            count = MoodAnalysis.objects.filter(user=user).count()
            print(f"  - {user.username} ({count} existing analyses)")
        
        print("\nUsage: python add_mood_test_data.py <username> [days]")
        print("Example: python add_mood_test_data.py mejriwajih 7")
        sys.exit(1)
    
    add_test_data(username, days)
