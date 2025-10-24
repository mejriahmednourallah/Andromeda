import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import Souvenir, User
from core.ai_services import AIAnalysisService

# Trouver l'utilisateur et un souvenir
user = User.objects.get(username='noura')
souvenir = Souvenir.objects.filter(utilisateur=user, titre='Roller Coaster Ride').first()

if souvenir:
    print(f'Avant réanalyse:')
    print(f'  Thème: {souvenir.theme}')
    print(f'  Emotion: {souvenir.emotion}')
    print(f'  Mots-clés: {souvenir.ai_tags}')

    # Réanalyser
    print(f'\nRéanalyse en cours...')
    analysis = AIAnalysisService.analyze_memory(souvenir)

    # Recharger
    souvenir.refresh_from_db()

    print(f'\nAprès réanalyse:')
    print(f'  Thème: {souvenir.theme}')
    print(f'  Emotion: {souvenir.emotion}')
    print(f'  Mots-clés: {souvenir.ai_tags}')
else:
    print('Souvenir non trouvé')