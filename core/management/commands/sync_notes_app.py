from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model

from core.models import Note as CoreNote, Link as CoreLink

try:
    from notes.models import Note as NotesNote, NoteLink as NotesNoteLink
except Exception:
    NotesNote = None
    NotesNoteLink = None


class Command(BaseCommand):
    help = 'Sync notes app notes and links into core graph models (one-time)'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to sync (optional)')

    def handle(self, *args, **options):
        if NotesNote is None or NotesNoteLink is None:
            self.stdout.write(self.style.ERROR('notes app not installed or models not found'))
            return

        username = options.get('user')
        User = get_user_model()

        users = []
        if username:
            try:
                users = [User.objects.get(username=username)]
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} not found'))
                return
        else:
            users = User.objects.all()

        total_notes = 0
        total_links = 0
        for user in users:
            notes = NotesNote.objects.filter(user=user)
            for n in notes:
                core_n, created = CoreNote.objects.get_or_create(owner=user, title=n.title, defaults={'body': getattr(n, 'content', '')})
                if created:
                    total_notes += 1

            # Sync links
            links = NotesNoteLink.objects.filter(source_note__user=user)
            for l in links:
                try:
                    src_core = CoreNote.objects.get(owner=user, title=l.source_note.title)
                    dst_core = CoreNote.objects.get(owner=l.target_note.user, title=l.target_note.title)
                    link, created = CoreLink.objects.get_or_create(src=src_core, dst=dst_core)
                    if created:
                        total_links += 1
                except CoreNote.DoesNotExist:
                    # Skip links where core nodes missing (shouldn't happen after previous loop)
                    continue

        self.stdout.write(self.style.SUCCESS(f'Synced {total_notes} notes and {total_links} links'))
