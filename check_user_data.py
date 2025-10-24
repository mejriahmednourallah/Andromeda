import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import Souvenir, User

# Trouver l'utilisateur 'noura'
try:
    user = User.objects.get(username='noura')
    print(f'Utilisateur trouvé: {user.username}')

    # Lister tous ses souvenirs analysés
    souvenirs = Souvenir.objects.filter(utilisateur=user, ai_analyzed=True)
    print(f'Nombre de souvenirs analysés: {souvenirs.count()}')

    for souvenir in souvenirs:
        print(f'\n📝 Souvenir: {souvenir.titre}')
        print(f'   Description: {souvenir.description[:100]}...')
        print(f'   Emotion actuelle: {souvenir.emotion}')
        print(f'   Thème actuel: {souvenir.theme}')
        print(f'   Mots-clés IA: {souvenir.ai_tags}')
        print(f'   Émotion IA: {souvenir.ai_emotion_detected}')

        # Tester la suggestion de thème avec ces mots-clés
        from core.ai_services import AIAnalysisService
        suggested_theme = AIAnalysisService._suggest_theme_from_keywords(souvenir.ai_tags or [])
        print(f'   Thème suggéré: {suggested_theme}')

        # Vérifier si la suggestion est différente du thème actuel
        if suggested_theme != souvenir.theme and suggested_theme != 'other':
            print(f'   ⚠️  Le thème devrait être mis à jour de \"{souvenir.theme}\" à \"{suggested_theme}\"')

except User.DoesNotExist:
    print('Utilisateur "noura" non trouvé')
except Exception as e:
    print(f'Erreur: {e}')
    import traceback
    traceback.print_exc()