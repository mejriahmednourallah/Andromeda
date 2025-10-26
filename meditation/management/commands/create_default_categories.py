from django.core.management.base import BaseCommand
from meditation.models import FocusCategory


class Command(BaseCommand):
    help = 'Create default focus categories'

    def handle(self, *args, **kwargs):
        categories = [
            {'name': 'Study', 'color': '#FF8C42'},
            {'name': 'Meditation', 'color': '#6B7FDB'},
            {'name': 'Work', 'color': '#4ECDC4'},
            {'name': 'Reading', 'color': '#FFD93D'},
            {'name': 'Exercise', 'color': '#95E1D3'},
        ]
        for cat in categories:
            FocusCategory.objects.get_or_create(name=cat['name'], defaults={'color': cat['color']})
        self.stdout.write(self.style.SUCCESS('Categories created!'))
