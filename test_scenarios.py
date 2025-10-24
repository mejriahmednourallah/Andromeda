#!/usr/bin/env python
"""
Scénarios de test complets pour Andromeda
Teste toutes les fonctionnalités de l'application en conditions réelles
"""

import os
import sys
import django
from datetime import timedelta

# Configuration Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from django.contrib.auth import authenticate, login
from django.test import Client, TestCase
from django.utils import timezone
from core.models import User, Souvenir, AnalyseIASouvenir, CapsuleTemporelle, AlbumSouvenir
from core.ai_services import AIAnalysisService, AIRecommendationService


class AndromedaTestScenarios:
    """Scénarios de test complets pour Andromeda"""

    def __init__(self):
        self.client = Client()
        self.test_user = None
        self.test_souvenirs = []

    def setup_test_user(self):
        """Créer un utilisateur de test"""
        print("🔧 Configuration de l'utilisateur de test...")

        # Supprimer l'utilisateur existant s'il y en a un
        User.objects.filter(username='test_scenario').delete()

        # Créer un nouvel utilisateur
        self.test_user = User.objects.create_user(
            username='test_scenario',
            email='test.scenario@example.com',
            password='testpass123',
            first_name='Test',
            last_name='Scenario'
        )

        print(f"✓ Utilisateur créé: {self.test_user.username}")
        return self.test_user

    def scenario_creation_souvenirs(self):
        """Scénario 1: Création de souvenirs avec analyse IA automatique"""
        print("\n🎯 SCÉNARIO 1: Création de souvenirs avec IA")
        print("=" * 50)

        # Se connecter
        self.client.login(username='test_scenario', password='testpass123')

        souvenirs_data = [
            {
                'titre': 'Vacances à Paris',
                'description': 'Un merveilleux séjour dans la Ville Lumière. Nous avons visité la Tour Eiffel, marché le long de la Seine, et dégusté des croissants frais tous les matins.',
                'emotion': 'joy',
                'theme': 'travel',
                'date_evenement': '2024-07-15',
                'lieu': 'Paris, France',
                'personnes_presentes': 'Famille et amis'
            },
            {
                'titre': 'Mon premier concert',
                'description': 'Incroyable expérience au concert de jazz. L\'atmosphère était électrique, la musique m\'a transporté dans un autre monde.',
                'emotion': 'excitement',
                'theme': 'achievement',
                'date_evenement': '2024-08-20',
                'lieu': 'Salle Pleyel, Paris',
                'personnes_presentes': 'Seul'
            },
            {
                'titre': 'Randonnée en montagne',
                'description': 'Belle journée de randonnée dans les Alpes. Le paysage était à couper le souffle, l\'air pur et frais.',
                'emotion': 'peace',
                'theme': 'nature',
                'date_evenement': '2024-09-10',
                'lieu': 'Alpes françaises',
                'personnes_presentes': 'Avec mon frère'
            }
        ]

        for i, data in enumerate(souvenirs_data, 1):
            print(f"\n📝 Création du souvenir {i}/3: {data['titre']}")

            # Créer le souvenir via POST
            response = self.client.post('/ajouter-souvenir/', data)
            print(f"  Status: {response.status_code}")

            if response.status_code == 302:  # Redirection = succès
                # Récupérer le souvenir créé
                souvenir = Souvenir.objects.filter(
                    utilisateur=self.test_user,
                    titre=data['titre']
                ).first()

                if souvenir:
                    print(f"  ✓ Souvenir créé: ID {souvenir.id}")
                    print(f"  🤖 IA analysée: {souvenir.ai_analyzed}")
                    if souvenir.ai_analyzed:
                        print(f"  📊 Résumé IA: {souvenir.ai_summary[:50]}...")
                        print(f"  🏷️ Mots-clés: {souvenir.ai_tags}")
                        print(f"  😊 Émotion détectée: {souvenir.ai_emotion_detected}")
                    self.test_souvenirs.append(souvenir)
                else:
                    print("  ✗ Souvenir non trouvé après création")
            else:
                print(f"  ✗ Échec création: {response.content.decode()[:200]}")

        print(f"\n✅ Scénario 1 terminé: {len(self.test_souvenirs)} souvenirs créés")

    def scenario_gestion_favoris(self):
        """Scénario 2: Gestion des favoris"""
        print("\n🎯 SCÉNARIO 2: Gestion des favoris")
        print("=" * 40)

        if not self.test_souvenirs:
            print("❌ Aucun souvenir disponible")
            return

        # Marquer le premier souvenir comme favori
        souvenir = self.test_souvenirs[0]
        print(f"⭐ Marquage favori: {souvenir.titre}")

        response = self.client.post(f'/souvenir/{souvenir.id}/toggle-favori/')
        print(f"  Status: {response.status_code}")

        # Vérifier le statut
        souvenir.refresh_from_db()
        print(f"  Favori: {souvenir.is_favorite}")

        # Retirer des favoris
        response = self.client.post(f'/souvenir/{souvenir.id}/toggle-favori/')
        souvenir.refresh_from_db()
        print(f"  Favori après retrait: {souvenir.is_favorite}")

        print("✅ Scénario 2 terminé")

    def scenario_analyse_ia_manuelle(self):
        """Scénario 3: Analyse IA manuelle"""
        print("\n🎯 SCÉNARIO 3: Analyse IA manuelle")
        print("=" * 40)

        if not self.test_souvenirs:
            print("❌ Aucun souvenir disponible")
            return

        # Prendre un souvenir non analysé ou le réanalyser
        souvenir = self.test_souvenirs[1]
        print(f"🤖 Analyse manuelle: {souvenir.titre}")

        response = self.client.post(f'/souvenir/{souvenir.id}/analyser-ia/')
        print(f"  Status: {response.status_code}")

        # Vérifier les résultats
        souvenir.refresh_from_db()
        if souvenir.ai_analyzed:
            print("  ✓ Analyse réussie")
            print(f"  📊 Résumé: {souvenir.ai_summary[:50]}...")
            print(f"  🏷️ Mots-clés: {souvenir.ai_tags}")
        else:
            print("  ⚠️ Analyse non effectuée")

        print("✅ Scénario 3 terminé")

    def scenario_galerie_ia(self):
        """Scénario 4: Galerie IA et insights"""
        print("\n🎯 SCÉNARIO 4: Galerie IA et insights")
        print("=" * 40)

        response = self.client.get('/galerie-ia/')
        print(f"  Status: {response.status_code}")

        if response.status_code == 200:
            print("  ✓ Page Galerie IA accessible")

            # Vérifier les insights
            insights = AIRecommendationService.get_memory_insights(self.test_user)
            print(f"  📊 Total souvenirs: {insights['total_memories']}")
            print(f"  😊 Émotion dominante: {insights['dominant_emotion']}")
            print(f"  🤖 Analysés: {insights['analyzed_count']}")

            # Vérifier les suggestions d'albums
            suggestions = AIAnalysisService.generate_album_suggestions(self.test_user)
            print(f"  📚 Suggestions d'albums: {len(suggestions)}")

            # Vérifier les prompts de réflexion
            prompts = AIRecommendationService.suggest_reflection_prompts(self.test_user)
            print(f"  💭 Prompts de réflexion: {len(prompts)}")

        print("✅ Scénario 4 terminé")

    def scenario_capsule_temporelle(self):
        """Scénario 5: Création et gestion des capsules temporelles"""
        print("\n🎯 SCÉNARIO 5: Capsules temporelles")
        print("=" * 40)

        if not self.test_souvenirs:
            print("❌ Aucun souvenir disponible")
            return

        # Créer une capsule temporelle
        future_date = timezone.now().date() + timedelta(days=30)

        capsule_data = {
            'titre': 'Message pour mon futur moi',
            'description': 'Ce souvenir te rappellera les bons moments de 2024',
            'date_ouverture': future_date.strftime('%Y-%m-%d'),
            'message_futur': 'N\'oublie pas de profiter de chaque instant!'
        }

        response = self.client.post('/creer-capsule/', capsule_data)
        print(f"  Status création capsule: {response.status_code}")

        if response.status_code == 302:
            # Récupérer la capsule créée
            capsule = CapsuleTemporelle.objects.filter(
                utilisateur=self.test_user
            ).order_by('-created_at').first()

            if capsule:
                print(f"  ✓ Capsule créée: {capsule.titre}")
                print(f"  📅 Date ouverture: {capsule.date_ouverture}")
                print(f"  ⏰ Jours restants: {capsule.jours_restants()}")

                # Prédiction émotion IA
                prediction = AIAnalysisService.predict_future_emotion(self.test_souvenirs[0])
                print(f"  🔮 Émotion prédite: {prediction['emotion']}")
                print(f"  📊 Confiance: {prediction['confidence']}")

        print("✅ Scénario 5 terminé")

    def scenario_albums(self):
        """Scénario 6: Création et gestion d'albums"""
        print("\n🎯 SCÉNARIO 6: Gestion des albums")
        print("=" * 35)

        if len(self.test_souvenirs) < 2:
            print("❌ Pas assez de souvenirs pour créer un album")
            return

        # Créer un album
        album_data = {
            'titre': 'Mes meilleurs souvenirs 2024',
            'description': 'Une collection de mes moments préférés cette année',
            'souvenirs': [s.id for s in self.test_souvenirs[:2]]
        }

        response = self.client.post('/creer-album/', album_data)
        print(f"  Status création album: {response.status_code}")

        if response.status_code == 302:
            # Vérifier l'album créé
            album = AlbumSouvenir.objects.filter(
                utilisateur=self.test_user
            ).order_by('-created_at').first()

            if album:
                print(f"  ✓ Album créé: {album.titre}")
                print(f"  📸 Nombre de souvenirs: {album.souvenirs.count()}")

        print("✅ Scénario 6 terminé")

    def scenario_filtrage_recherche(self):
        """Scénario 7: Filtrage et recherche de souvenirs"""
        print("\n🎯 SCÉNARIO 7: Filtrage et recherche")
        print("=" * 40)

        # Test de filtrage par émotion
        response = self.client.get('/liste-souvenirs/?emotion=joy')
        print(f"  Filtrage émotion 'joy': {response.status_code}")

        # Test de filtrage par thème
        response = self.client.get('/liste-souvenirs/?theme=travel')
        print(f"  Filtrage thème 'travel': {response.status_code}")

        # Test de recherche textuelle
        response = self.client.get('/liste-souvenirs/?q=Paris')
        print(f"  Recherche 'Paris': {response.status_code}")

        # Test de filtrage favoris
        response = self.client.get('/liste-souvenirs/?favoris=on')
        print(f"  Filtrage favoris: {response.status_code}")

        print("✅ Scénario 7 terminé")

    def run_all_scenarios(self):
        """Exécuter tous les scénarios"""
        print("🚀 DÉBUT DES TESTS DE SCÉNARIOS ANDROMEDA")
        print("=" * 60)

        try:
            # Configuration
            self.setup_test_user()

            # Exécution des scénarios
            self.scenario_creation_souvenirs()
            self.scenario_gestion_favoris()
            self.scenario_analyse_ia_manuelle()
            self.scenario_galerie_ia()
            self.scenario_capsule_temporelle()
            self.scenario_albums()
            self.scenario_filtrage_recherche()

            print("\n🎉 TOUS LES SCÉNARIOS TERMINÉS AVEC SUCCÈS!")
            print("=" * 60)

            # Résumé final
            total_souvenirs = Souvenir.objects.filter(utilisateur=self.test_user).count()
            analyzed_count = Souvenir.objects.filter(utilisateur=self.test_user, ai_analyzed=True).count()
            capsules_count = CapsuleTemporelle.objects.filter(utilisateur=self.test_user).count()
            albums_count = AlbumSouvenir.objects.filter(utilisateur=self.test_user).count()

            print("📊 RÉSUMÉ FINAL:")
            print(f"  👤 Utilisateur: {self.test_user.username}")
            print(f"  📝 Souvenirs créés: {total_souvenirs}")
            print(f"  🤖 Souvenirs analysés IA: {analyzed_count}")
            print(f"  ⏰ Capsules temporelles: {capsules_count}")
            print(f"  📚 Albums: {albums_count}")

        except Exception as e:
            print(f"\n❌ ERREUR LORS DES TESTS: {e}")
            import traceback
            traceback.print_exc()

    def cleanup(self):
        """Nettoyer les données de test"""
        print("\n🧹 Nettoyage des données de test...")

        if self.test_user:
            # Supprimer tous les objets liés à l'utilisateur de test
            Souvenir.objects.filter(utilisateur=self.test_user).delete()
            CapsuleTemporelle.objects.filter(utilisateur=self.test_user).delete()
            AlbumSouvenir.objects.filter(utilisateur=self.test_user).delete()
            AnalyseIASouvenir.objects.filter(souvenir__utilisateur=self.test_user).delete()

            # Supprimer l'utilisateur
            self.test_user.delete()

            print("✓ Données de test supprimées")

def main():
    """Point d'entrée principal"""
    print("🧪 SCÉNARIOS DE TEST COMPLETS ANDROMEDA")
    print("Teste toutes les fonctionnalités en conditions réelles")
    print()

    # Créer et exécuter les scénarios
    tester = AndromedaTestScenarios()
    tester.run_all_scenarios()

    # Demander si on nettoie
    cleanup = input("\n🧹 Voulez-vous nettoyer les données de test ? (y/n): ").lower().strip()
    if cleanup == 'y':
        tester.cleanup()
    else:
        print("📝 Données de test conservées pour inspection")

if __name__ == '__main__':
    main()