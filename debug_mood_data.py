#!/usr/bin/env python
"""
Script de débogage pour vérifier les données MoodAnalysis
"""
import os
import django
from datetime import datetime, timedelta

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.utils import timezone
from core.models import MoodAnalysis, User

def debug_mood_data():
    print("=" * 60)
    print("DEBUG: MoodAnalysis Data")
    print("=" * 60)
    
    # Get all users
    users = User.objects.all()
    print(f"\n📊 Total users: {users.count()}")
    
    for user in users:
        print(f"\n👤 User: {user.username}")
        
        # Get all mood analyses
        all_analyses = MoodAnalysis.objects.filter(user=user)
        print(f"   Total analyses: {all_analyses.count()}")
        
        if all_analyses.exists():
            # Show date range
            oldest = all_analyses.order_by('created_at').first()
            newest = all_analyses.order_by('-created_at').first()
            print(f"   Date range: {oldest.created_at.strftime('%Y-%m-%d')} to {newest.created_at.strftime('%Y-%m-%d')}")
            
            # Last 14 days
            fourteen_days_ago = timezone.now() - timedelta(days=14)
            recent = MoodAnalysis.objects.filter(
                user=user,
                created_at__gte=fourteen_days_ago
            )
            print(f"   📅 Last 14 days: {recent.count()} analyses")
            
            # Last 30 days
            thirty_days_ago = timezone.now() - timedelta(days=30)
            recent_30 = MoodAnalysis.objects.filter(
                user=user,
                created_at__gte=thirty_days_ago
            )
            print(f"   📅 Last 30 days: {recent_30.count()} analyses")
            
            # Show recent analyses
            print("\n   Recent analyses:")
            for analysis in all_analyses.order_by('-created_at')[:5]:
                print(f"      - {analysis.created_at.strftime('%Y-%m-%d %H:%M')} | {analysis.top} | Scores: {analysis.scores}")
    
    print("\n" + "=" * 60)

if __name__ == '__main__':
    debug_mood_data()
