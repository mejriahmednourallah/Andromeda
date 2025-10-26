from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.models import Note, Link
import uuid


class Command(BaseCommand):
    help = 'Seed a demo graph (notes + links) for a user. Creates user if missing.'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to create/demo the graph for (optional)')

    def handle(self, *args, **options):
        username = options.get('user') or 'graph_demo'
        User = get_user_model()

        user, created = User.objects.get_or_create(username=username, defaults={'email': f'{username}@example.com'})
        if created:
            user.set_password('graphpass')
            user.save()
            self.stdout.write(self.style.SUCCESS(f'Created demo user: {username} (password: graphpass)'))
        else:
            self.stdout.write(f'Using existing user: {username}')

        # Clear existing notes for the demo user to avoid duplicates
        existing_notes = Note.objects.filter(owner=user)
        existing_notes_count = existing_notes.count()
        if existing_notes_count:
            existing_notes.delete()
            self.stdout.write(f'Removed {existing_notes_count} existing notes for {username}')

        titles = ['Alpha', 'Beta', 'Gamma', 'Delta', 'Epsilon', 'Zeta', 'Eta', 'Theta']
        notes = {}
        for t in titles:
            n = Note.objects.create(owner=user, title=t, body=f'This is note {t}.')
            notes[t] = n

        # Create links to form an interesting graph
        links = [
            ('Alpha', 'Beta'),
            ('Alpha', 'Gamma'),
            ('Beta', 'Delta'),
            ('Gamma', 'Delta'),
            ('Delta', 'Epsilon'),
            ('Epsilon', 'Zeta'),
            ('Gamma', 'Eta'),
            ('Zeta', 'Theta'),
        ]

        created_links = 0
        for src, dst in links:
            Link.objects.get_or_create(src=notes[src], dst=notes[dst])
            created_links += 1

        self.stdout.write(self.style.SUCCESS(f'Created {len(notes)} notes and {created_links} links for user {username}'))
        self.stdout.write(self.style.SUCCESS('Done. Visit /graph/ after logging in as the demo user.'))
