import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')
django.setup()

from core.models import User

print('Total users:', User.objects.all().count())
for user in User.objects.all():
    print(f'Username: {user.username}, Email: {user.email}, Is active: {user.is_active}')