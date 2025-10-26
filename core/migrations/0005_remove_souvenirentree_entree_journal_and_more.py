from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import uuid


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_remove_souvenir_note_associee_and_more'),
    ]

    operations = [
        migrations.CreateModel(
            name='MoodAnalysis',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('text', models.TextField()),
                ('top', models.CharField(max_length=32)),
                ('scores', models.JSONField(default=dict)),
                ('source', models.CharField(max_length=64, blank=True, null=True)),
                ('model', models.CharField(max_length=200, blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE, related_name='mood_analyses')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
        migrations.CreateModel(
            name='MoodRecommendation',
            fields=[
                ('id', models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False, serialize=False)),
                ('recommendation', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('analysis', models.ForeignKey(to='core.moodanalysis', on_delete=django.db.models.deletion.CASCADE, related_name='recommendations')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL, on_delete=django.db.models.deletion.CASCADE, related_name='mood_recommendations')),
            ],
            options={
                'ordering': ['-created_at'],
            },
        ),
    ]
