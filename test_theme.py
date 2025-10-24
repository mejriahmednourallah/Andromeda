import os
import django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.ai_services import AIAnalysisService

# Test avec les données du souvenir
keywords = ['premier', 'voyage', 'rome', 'amis', 'visité', 'colisée', 'mangé', 'meilleure']
title = 'Mon premier voyage à Rome'
description = 'C\'était mon premier voyage à Rome avec mes amis. Nous avons visité le Colisée, mangé de la meilleure pizza et passé des moments de bonheur entourés de beauté antique.'

print('Test de suggestion de thème avec vos données...')
print(f'Mots-clés: {keywords}')
print()

# Test de la suggestion de thème
suggested_theme = AIAnalysisService._suggest_theme_from_keywords(keywords)
print(f'Thème suggéré: {suggested_theme}')

# Test complet de l'analyse
result = AIAnalysisService._analyze_text(title, description)
print(f'Analyse complète:')
print(f'  Résumé: {result["summary"][:100]}...')
print(f'  Mots-clés: {result["keywords"]}')
print(f'  Émotion: {result["emotion"]}')
print(f'  Thème suggéré: {AIAnalysisService._suggest_theme_from_keywords(result["keywords"])}')