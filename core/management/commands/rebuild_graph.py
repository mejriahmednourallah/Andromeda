from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from core.utils import rebuild_all_links


class Command(BaseCommand):
    help = 'Rebuild note link graph for all users or specific user'

    def add_arguments(self, parser):
        parser.add_argument('--user', type=str, help='Username to rebuild links for (optional)')

    def handle(self, *args, **options):
        username = options.get('user')
        User = get_user_model()

        if username:
            try:
                user = User.objects.get(username=username)
                total = rebuild_all_links(user)
                self.stdout.write(self.style.SUCCESS(f'Rebuilt {total} links for user {username}'))
            except User.DoesNotExist:
                self.stdout.write(self.style.ERROR(f'User {username} not found'))
        else:
            total = 0
            for user in User.objects.all():
                links = rebuild_all_links(user)
                total += links
                self.stdout.write(f'User {user.username}: {links} links')

            self.stdout.write(self.style.SUCCESS(f'Total: {total} links rebuilt'))
