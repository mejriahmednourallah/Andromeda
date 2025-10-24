import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIAnalysisService

# Tester avec les mots-clés de l'utilisateur
test_cases = [
    {
        'name': 'Pool Party',
        'keywords': ['great', 'friends', 'swimming', 'having', 'pool', 'party', 'test']
    },
    {
        'name': 'Diplôme',
        'keywords': ['diplôme', 'réussite', 'efforts', 'années', 'obtenu', 'parents', 'fiers', 'fierté']
    },
    {
        'name': 'Voyage Rome',
        'keywords': ['premier', 'voyage', 'rome', 'amis', 'visité', 'colisée', 'mangé', 'meilleure']
    }
]

for test_case in test_cases:
    print(f"\n🧪 Test pour: {test_case['name']}")
    print(f"Mots-clés: {test_case['keywords']}")

    suggested_theme = AIAnalysisService._suggest_theme_from_keywords(test_case['keywords'])
    print(f"Thème suggéré: {suggested_theme}")

    # Vérifier si le thème est valide
    from core.models import Souvenir
    valid_themes = dict(Souvenir.THEME_CHOICES)
    if suggested_theme in valid_themes:
        print(f"✅ Thème valide: {valid_themes[suggested_theme]}")
    else:
        print(f"❌ Thème invalide ou 'other'")