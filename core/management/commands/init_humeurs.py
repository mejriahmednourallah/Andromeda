"""
Commande pour initialiser les humeurs par défaut
"""
from django.core.management.base import BaseCommand
from core.models import Humeur


class Command(BaseCommand):
    help = 'Initialise les humeurs par défaut dans la base de données'

    def handle(self, *args, **kwargs):
        humeurs_defaut = [
            {'nom': 'Joyeux', 'emoji': '😊', 'couleur': '#FFD700', 'description': 'Sentiment de joie et de bonheur'},
            {'nom': 'Triste', 'emoji': '😢', 'couleur': '#4169E1', 'description': 'Sentiment de tristesse'},
            {'nom': 'En colère', 'emoji': '😠', 'couleur': '#DC143C', 'description': 'Sentiment de colère ou frustration'},
            {'nom': 'Anxieux', 'emoji': '😰', 'couleur': '#9370DB', 'description': 'Sentiment d\'anxiété ou d\'inquiétude'},
            {'nom': 'Excité', 'emoji': '🤩', 'couleur': '#FF69B4', 'description': 'Sentiment d\'excitation'},
            {'nom': 'Calme', 'emoji': '😌', 'couleur': '#87CEEB', 'description': 'Sentiment de calme et de sérénité'},
            {'nom': 'Fatigué', 'emoji': '😴', 'couleur': '#696969', 'description': 'Sentiment de fatigue'},
            {'nom': 'Motivé', 'emoji': '💪', 'couleur': '#32CD32', 'description': 'Sentiment de motivation'},
            {'nom': 'Confus', 'emoji': '😕', 'couleur': '#DAA520', 'description': 'Sentiment de confusion'},
            {'nom': 'Reconnaissant', 'emoji': '🙏', 'couleur': '#FF8C00', 'description': 'Sentiment de gratitude'},
            {'nom': 'Amoureux', 'emoji': '😍', 'couleur': '#FF1493', 'description': 'Sentiment d\'amour'},
            {'nom': 'Nostalgique', 'emoji': '🥺', 'couleur': '#B0C4DE', 'description': 'Sentiment de nostalgie'},
            {'nom': 'Stressé', 'emoji': '😫', 'couleur': '#8B0000', 'description': 'Sentiment de stress'},
            {'nom': 'Paisible', 'emoji': '🕊️', 'couleur': '#E0FFFF', 'description': 'Sentiment de paix intérieure'},
            {'nom': 'Créatif', 'emoji': '🎨', 'couleur': '#FF6347', 'description': 'Sentiment de créativité'},
        ]

        created_count = 0
        updated_count = 0

        for humeur_data in humeurs_defaut:
            humeur, created = Humeur.objects.get_or_create(
                nom=humeur_data['nom'],
                defaults={
                    'emoji': humeur_data['emoji'],
                    'couleur': humeur_data['couleur'],
                    'description': humeur_data['description']
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(
                    self.style.SUCCESS(f'✓ Humeur créée: {humeur.emoji} {humeur.nom}')
                )
            else:
                updated_count += 1
                self.stdout.write(
                    self.style.WARNING(f'→ Humeur existante: {humeur.emoji} {humeur.nom}')
                )

        self.stdout.write(
            self.style.SUCCESS(
                f'\n✅ Terminé! {created_count} humeurs créées, {updated_count} existantes.'
            )
        )
