#!/usr/bin/env python
"""
Test du service de recommandation musicale
"""
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.music_recommendation_service import MusicRecommendationService

def test_music_recommendations():
    print("=" * 70)
    print("🎵 TEST: Music Recommendation Service")
    print("=" * 70)
    
    test_cases = [
        {
            'text': "Je me sens super bien aujourd'hui, j'ai réussi tous mes objectifs!",
            'mood': 'positif',
            'description': 'Mood positif - succès et joie'
        },
        {
            'text': "Je suis un peu triste, j'ai besoin de réconfort",
            'mood': 'tristesse',
            'description': 'Mood triste - besoin de réconfort'
        },
        {
            'text': "Je suis tellement en colère, rien ne va comme prévu",
            'mood': 'colere',
            'description': 'Mood colère - frustration'
        },
        {
            'text': "Journée normale, rien de spécial",
            'mood': 'neutre',
            'description': 'Mood neutre - routine'
        },
        {
            'text': "Je me sens mal, tout va de travers dans ma vie",
            'mood': 'negatif',
            'description': 'Mood négatif - déprime'
        }
    ]
    
    for i, test in enumerate(test_cases, 1):
        print(f"\n{'─' * 70}")
        print(f"Test {i}: {test['description']}")
        print(f"{'─' * 70}")
        print(f"📝 Input text: {test['text']}")
        print(f"🎭 Detected mood: {test['mood']}")
        
        try:
            recommendation = MusicRecommendationService.get_music_recommendation(
                test['text'], 
                test['mood']
            )
            
            print(f"\n🎵 Music Recommendation:")
            print(f"   Emotion: {recommendation['emotion']}")
            print(f"   Song: {recommendation['suggestion']}")
            print(f"   Description: {recommendation['description']}")
            print(f"\n   🔗 YouTube: https://www.youtube.com/results?search_query={recommendation['suggestion']}")
            print(f"   🔗 Spotify: https://open.spotify.com/search/{recommendation['suggestion']}")
            
        except Exception as e:
            print(f"❌ Error: {e}")
    
    print(f"\n{'=' * 70}")
    print("✅ All tests completed!")
    print("=" * 70)

if __name__ == '__main__':
    test_music_recommendations()
