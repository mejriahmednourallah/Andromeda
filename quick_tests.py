#!/usr/bin/env python
"""
Tests rapides individuels pour Andromeda
Permet de tester des fonctionnalités spécifiques rapidement
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.test import Client
from core.models import User, Souvenir
from core.ai_services import AIAnalysisService


def test_ia_analysis():
    """Test rapide de l'analyse IA"""
    print("🤖 Test Analyse IA")

    # Créer un souvenir de test
    user = User.objects.create_user('test_ia', 'test@example.com', 'pass')
    souvenir = Souvenir.objects.create(
        utilisateur=user,
        titre="Test IA",
        description="Ceci est un test de l'analyse IA automatique.",
        emotion='joy',
        theme='personal'
    )

    # Analyser
    try:
        analysis = AIAnalysisService.analyze_memory(souvenir)
        print("✅ Analyse réussie")
        print(f"   Résumé: {analysis.resume_genere[:50]}...")
        print(f"   Émotion: {analysis.emotion_texte}")
        print(f"   Mots-clés: {analysis.mots_cles}")
    except Exception as e:
        print(f"❌ Erreur: {e}")

    # Nettoyer
    souvenir.delete()
    user.delete()


def test_souvenir_creation():
    """Test création souvenir via interface web"""
    print("📝 Test Création Souvenir Web")

    client = Client()

    # Créer utilisateur
    user = User.objects.create_user('test_web', 'web@example.com', 'pass')
    client.login(username='test_web', password='pass')

    # Créer souvenir
    data = {
        'titre': 'Test Web',
        'description': 'Test via interface web',
        'emotion': 'joy',
        'theme': 'personal',
        'date_evenement': '2024-01-01'
    }

    response = client.post('/ajouter-souvenir/', data)
    print(f"Status: {response.status_code}")

    if response.status_code == 302:
        souvenir = Souvenir.objects.filter(utilisateur=user, titre='Test Web').first()
        if souvenir:
            print("✅ Souvenir créé avec succès")
            print(f"   IA analysé: {souvenir.ai_analyzed}")
        else:
            print("❌ Souvenir non trouvé")
    else:
        print("❌ Échec création")

    # Nettoyer
    Souvenir.objects.filter(utilisateur=user).delete()
    user.delete()


def test_galerie_ia():
    """Test de la galerie IA"""
    print("🎨 Test Galerie IA")

    client = Client()

    # Créer utilisateur avec souvenirs
    user = User.objects.create_user('test_galerie', 'galerie@example.com', 'pass')

    # Créer quelques souvenirs
    for i in range(3):
        Souvenir.objects.create(
            utilisateur=user,
            titre=f"Souvenir {i+1}",
            description=f"Description du souvenir {i+1}",
            emotion='joy',
            theme='personal'
        )

    client.login(username='test_galerie', password='pass')
    response = client.get('/galerie-ia/')

    print(f"Status: {response.status_code}")
    if 'AI Insights' in response.content.decode():
        print("✅ Galerie IA accessible")
    else:
        print("❌ Contenu galerie incorrect")

    # Nettoyer
    Souvenir.objects.filter(utilisateur=user).delete()
    user.delete()


def show_menu():
    """Afficher le menu des tests rapides"""
    print("\n" + "="*50)
    print("🧪 TESTS RAPIDES ANDROMEDA")
    print("="*50)
    print("1. Test Analyse IA")
    print("2. Test Création Souvenir Web")
    print("3. Test Galerie IA")
    print("4. Test Tous")
    print("0. Quitter")
    print("="*50)


def main():
    """Menu principal des tests rapides"""
    while True:
        show_menu()
        choice = input("Choisissez un test (0-4): ").strip()

        if choice == '0':
            print("👋 Au revoir!")
            break
        elif choice == '1':
            test_ia_analysis()
        elif choice == '2':
            test_souvenir_creation()
        elif choice == '3':
            test_galerie_ia()
        elif choice == '4':
            print("🚀 Exécution de tous les tests...")
            test_ia_analysis()
            print()
            test_souvenir_creation()
            print()
            test_galerie_ia()
        else:
            print("❌ Choix invalide")

        input("\nAppuyez sur Entrée pour continuer...")


if __name__ == '__main__':
    main()