#!/usr/bin/env python
"""
Nettoyer et recréer les données mood avec des dates correctes sur plusieurs jours
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from core.models import MoodAnalysis, User

def fix_mood_dates(username, clean_first=False):
    """
    Crée des données mood sur plusieurs jours
    """
    try:
        user = User.objects.get(username=username)
    except User.DoesNotExist:
        print(f"❌ User '{username}' not found")
        return
    
    print(f"{'='*70}")
    print(f"Fixing mood data dates for: {user.username}")
    print(f"Current time: {timezone.now()}")
    print(f"{'='*70}")
    
    if clean_first:
        # Delete test data
        test_analyses = MoodAnalysis.objects.filter(user=user, source='test')
        count = test_analyses.count()
        if count > 0:
            test_analyses.delete()
            print(f"🗑️  Deleted {count} test analyses\n")
    
    # Define mood patterns for each day
    daily_patterns = [
        {'day': -6, 'top': 'positif', 'scores': {'positif': 0.8, 'neutre': 0.1, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}, 'text': 'Journée productive'},
        {'day': -5, 'top': 'positif', 'scores': {'positif': 0.9, 'neutre': 0.05, 'negatif': 0.02, 'colere': 0.02, 'tristesse': 0.01}, 'text': 'Excellente journée!'},
        {'day': -4, 'top': 'neutre', 'scores': {'positif': 0.3, 'neutre': 0.5, 'negatif': 0.1, 'colere': 0.05, 'tristesse': 0.05}, 'text': 'Journée tranquille'},
        {'day': -3, 'top': 'negatif', 'scores': {'positif': 0.1, 'neutre': 0.2, 'negatif': 0.4, 'colere': 0.15, 'tristesse': 0.15}, 'text': 'Journée difficile'},
        {'day': -2, 'top': 'positif', 'scores': {'positif': 0.85, 'neutre': 0.1, 'negatif': 0.03, 'colere': 0.01, 'tristesse': 0.01}, 'text': 'Retour en forme'},
        {'day': -1, 'top': 'positif', 'scores': {'positif': 0.75, 'neutre': 0.15, 'negatif': 0.05, 'colere': 0.03, 'tristesse': 0.02}, 'text': 'Bonne humeur'},
        {'day': 0, 'top': 'positif', 'scores': {'positif': 0.95, 'neutre': 0.03, 'negatif': 0.01, 'colere': 0.005, 'tristesse': 0.005}, 'text': 'Au top aujourd\'hui!'},
    ]
    
    created_count = 0
    now = timezone.now()
    
    for pattern in daily_patterns:
        # Calculate target date (at 14:00 to avoid timezone issues)
        target_date = now + timedelta(days=pattern['day'])
        target_datetime = target_date.replace(hour=14, minute=0, second=0, microsecond=0)
        
        # Check if already exists
        day_start = target_datetime.replace(hour=0, minute=0, second=0, microsecond=0)
        day_end = day_start + timedelta(days=1)
        existing_count = MoodAnalysis.objects.filter(
            user=user,
            created_at__gte=day_start,
            created_at__lt=day_end
        ).exclude(source='test').count()
        
        if existing_count > 0:
            print(f"⏭️  {target_datetime.strftime('%Y-%m-%d')}: Has {existing_count} real analysis(es) - skipping")
            continue
        
        # Create the analysis using raw SQL to ensure created_at is set correctly
        analysis = MoodAnalysis(
            user=user,
            text=pattern['text'],
            top=pattern['top'],
            scores=pattern['scores'],
            source='test',
            model='test_generator'
        )
        analysis.save()
        
        # Force update the created_at field
        MoodAnalysis.objects.filter(id=analysis.id).update(created_at=target_datetime)
        
        # Calculate positivity
        positivity = pattern['scores']['positif'] - (
            pattern['scores']['negatif'] + 
            pattern['scores']['colere'] + 
            pattern['scores']['tristesse']
        )
        
        # Reload to get the updated timestamp
        analysis.refresh_from_db()
        print(f"✅ {analysis.created_at.strftime('%Y-%m-%d %H:%M')} | {pattern['top']:8s} | positivity={positivity:+.2f}")
        created_count += 1
    
    print(f"\n{'-'*70}")
    print(f"✅ Created {created_count} mood analyses across different days")
    
    # Verify the data
    fourteen_days_ago = now - timedelta(days=14)
    in_window = MoodAnalysis.objects.filter(
        user=user,
        created_at__gte=fourteen_days_ago
    ).count()
    
    print(f"📊 Total analyses in 14-day window: {in_window}")
    print(f"\n🌐 Now visit: http://127.0.0.1:8000/mood/")
    print(f"   Login as: {user.username}")
    print(f"{'='*70}")

if __name__ == '__main__':
    import sys
    
    if len(sys.argv) > 1:
        username = sys.argv[1]
        clean = '--clean' in sys.argv
        fix_mood_dates(username, clean_first=clean)
    else:
        print("Usage: python fix_mood_data_dates.py <username> [--clean]")
        print("Example: python fix_mood_data_dates.py mejriwajih --clean")
        print("\n--clean flag will delete existing test data first")
        sys.exit(1)
