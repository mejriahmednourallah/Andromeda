import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser

# --- Custom user (simple extension) ---
class User(AbstractUser):
    avatar_url = models.URLField(blank=True, null=True)

    # Override to avoid clashes
    groups = models.ManyToManyField(
        'auth.Group',
        verbose_name='groups',
        blank=True,
        help_text='The groups this user belongs to.',
        related_name='core_users',
        related_query_name='core_user',
    )
    user_permissions = models.ManyToManyField(
        'auth.Permission',
        verbose_name='user permissions',
        blank=True,
        help_text='Specific permissions for this user.',
        related_name='core_users',
        related_query_name='core_user',
    )

    def __str__(self):
        return self.get_full_name() or self.username

# --- Templates (Notion-style template objects) ---
class Template(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='templates')
    name = models.CharField(max_length=200)
    # JSON structure for blocks/placeholder values (you can use a block schema later)
    content = models.JSONField(default=dict)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"

# --- Notes (each note is a 'star' in Andromeda) ---
class Note(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='notes', null=True, blank=True)
    title = models.CharField(max_length=400)
    body = models.TextField(blank=True)
    metadata = models.JSONField(default=dict, blank=True)  # tags, mood, pinned, etc
    public = models.BooleanField(default=False)
    source = models.CharField(max_length=200, blank=True, null=True)  # 'webclip', 'import', etc
    embedding_id = models.CharField(max_length=255, blank=True, null=True)  # pointer to vector store
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

# --- Edges between notes (graph links) ---
class Link(models.Model):
    KIND_CHOICES = [
        ('reference', 'Reference'),
        ('derived', 'Derived'),
        ('quote', 'Quote'),
    ]
    src = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='outgoing_links')
    dst = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='incoming_links')
    kind = models.CharField(max_length=50, choices=KIND_CHOICES, default='reference')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('src', 'dst', 'kind')

    def __str__(self):
        return f"{self.src} → {self.dst} ({self.kind})"

# --- Attachments (files/images) ---
class Attachment(models.Model):
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='attachments')
    file = models.FileField(upload_to='attachments/')
    mime = models.CharField(max_length=100, blank=True)
    title = models.CharField(max_length=250, blank=True)
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.title or f"Attachment {self.pk}"

# --- API Integrations (GROQ / Sanity / others) ---
class APIIntegration(models.Model):
    owner = models.ForeignKey('User', on_delete=models.CASCADE, related_name='integrations')
    name = models.CharField(max_length=200)  # e.g., 'Sanity (GROQ)'
    kind = models.CharField(max_length=100, blank=True)  # provider key
    config = models.JSONField(default=dict, blank=True)  # store tokens, dataset etc
    enabled = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.owner})"

# --- AI / background tasks tracker ---
class AITask(models.Model):
    TASK_TYPES = [
        ('embed', 'Embedding'),
        ('transcribe', 'Transcription'),
        ('summarize', 'Summarize'),
        ('ocr', 'OCR'),
    ]
    STATUS = [
        ('queued','Queued'),
        ('running','Running'),
        ('done','Done'),
        ('error','Error')
    ]
    task_type = models.CharField(max_length=50, choices=TASK_TYPES)
    note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='ai_tasks', null=True, blank=True)
    attachment = models.ForeignKey(Attachment, on_delete=models.CASCADE, null=True, blank=True)
    status = models.CharField(max_length=30, choices=STATUS, default='queued')
    result = models.JSONField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.task_type} ({self.status})"

# --- Souvenirs (Memories) ---
class Souvenir(models.Model):
    """Modèle pour stocker les souvenirs des utilisateurs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='souvenirs')
    titre = models.CharField(max_length=200, help_text="Titre du souvenir")
    description = models.TextField(help_text="Description détaillée du souvenir")
    date_evenement = models.DateField(help_text="Date de l'événement")
    photo = models.ImageField(upload_to='souvenirs/photos/%Y/%m/', blank=True, null=True)
    video = models.FileField(upload_to='souvenirs/videos/%Y/%m/', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_evenement']
        verbose_name = 'Souvenir'
        verbose_name_plural = 'Souvenirs'

    def __str__(self):
        return f"{self.titre} - {self.date_evenement}"
    
    def clean(self):
        """Validation personnalisée"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Vérifier que la date n'est pas dans le futur
        if self.date_evenement > timezone.now().date():
            raise ValidationError({'date_evenement': 'La date de l\'événement ne peut pas être dans le futur.'})
        
        # Vérifier la taille des fichiers
        if self.photo and self.photo.size > 10 * 1024 * 1024:  # 10 MB
            raise ValidationError({'photo': 'La photo ne doit pas dépasser 10 MB.'})
        
        if self.video and self.video.size > 100 * 1024 * 1024:  # 100 MB
            raise ValidationError({'video': 'La vidéo ne doit pas dépasser 100 MB.'})
    
    def save(self, *args, **kwargs):
        """Appel de clean() avant la sauvegarde"""
        self.full_clean()
        super().save(*args, **kwargs)

# --- Badge/Medal System (Gamification) ---
class Badge(models.Model):
    BADGE_TYPES = [
        ('consistency', 'Constance'),
        ('reflective', 'Reflexif'),
        ('emotional_balance', 'Equilibre Emotionnel'),
        ('memory_keeper', 'Gardien de Memoires'),
        ('storyteller', 'Conteur'),
        ('explorer', 'Explorateur'),
    ]
    
    code = models.CharField(max_length=50, unique=True, choices=BADGE_TYPES)
    name = models.CharField(max_length=100)
    description = models.TextField()
    icon = models.CharField(max_length=10, default='trophy')
    requirement_value = models.IntegerField(help_text="Valeur requise pour debloquer")
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.icon} {self.name}"


class UserBadge(models.Model):
    user = models.ForeignKey('User', on_delete=models.CASCADE, related_name='badges')
    badge = models.ForeignKey(Badge, on_delete=models.CASCADE)
    earned_at = models.DateTimeField(auto_now_add=True)
    progress = models.IntegerField(default=0, help_text="Progression actuelle vers le badge")
    
    class Meta:
        unique_together = ('user', 'badge')
        ordering = ['-earned_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.badge.name}"
    
    @property
    def is_unlocked(self):
        return self.progress >= self.badge.requirement_value
    
    @property
    def progress_percentage(self):
        if self.badge.requirement_value == 0:
            return 100
        return min(100, (self.progress / self.badge.requirement_value) * 100)
