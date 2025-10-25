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
    """Model for storing user memories with AI-enhanced features"""
    EMOTION_CHOICES = [
        ('joy', 'Joy'),
        ('sadness', 'Sadness'),
        ('nostalgia', 'Nostalgia'),
        ('gratitude', 'Gratitude'),
        ('excitement', 'Excitement'),
        ('peace', 'Peace'),
        ('love', 'Love'),
        ('surprise', 'Surprise'),
        ('pride', 'Pride'),
        ('neutral', 'Neutral'),
    ]
    
    THEME_CHOICES = [
        ('family', 'Family'),
        ('travel', 'Travel'),
        ('work', 'Work'),
        ('friends', 'Friends'),
        ('achievement', 'Achievement'),
        ('celebration', 'Celebration'),
        ('nature', 'Nature'),
        ('learning', 'Learning'),
        ('other', 'Other'),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='souvenirs')
    
    # Basic Information
    titre = models.CharField(max_length=200, help_text="Memory title")
    description = models.TextField(help_text="Detailed description of the memory")
    date_evenement = models.DateField(help_text="Date of the event")
    
    # Media
    photo = models.ImageField(upload_to='souvenirs/photos/%Y/%m/', blank=True, null=True)
    video = models.FileField(upload_to='souvenirs/videos/%Y/%m/', blank=True, null=True)
    
    # Metadata
    emotion = models.CharField(max_length=50, choices=EMOTION_CHOICES, default='neutral', help_text="Primary emotion")
    theme = models.CharField(max_length=50, choices=THEME_CHOICES, default='other', help_text="Memory theme")
    lieu = models.CharField(max_length=200, blank=True, default='', help_text="Location of the memory")
    personnes_presentes = models.CharField(max_length=500, blank=True, default='', help_text="People present (comma-separated)")
    
    # User Preferences
    is_favorite = models.BooleanField(default=False, help_text="Mark as favorite")
    is_public = models.BooleanField(default=False, help_text="Make publicly visible")
    
    # AI-Enhanced Fields
    ai_summary = models.TextField(blank=True, default='', help_text="AI-generated summary")
    ai_emotion_detected = models.CharField(max_length=50, blank=True, default='', help_text="AI-detected emotion")
    ai_tags = models.JSONField(default=list, blank=True, help_text="AI-generated tags")
    ai_analyzed = models.BooleanField(default=False, help_text="Has been analyzed by AI")
    ai_analysis_date = models.DateTimeField(null=True, blank=True, help_text="Date of AI analysis")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-date_evenement']
        verbose_name = 'Memory'
        verbose_name_plural = 'Memories'
        indexes = [
            models.Index(fields=['-date_evenement']),
            models.Index(fields=['utilisateur', '-created_at']),
            models.Index(fields=['is_favorite']),
        ]

    def __str__(self):
        return f"{self.titre} - {self.date_evenement}"
    
    def clean(self):
        """Custom validation"""
        from django.core.exceptions import ValidationError
        from django.utils import timezone
        
        # Check that date is not in the future
        if self.date_evenement > timezone.now().date():
            raise ValidationError({'date_evenement': 'Event date cannot be in the future.'})
        
        # Check file sizes
        if self.photo and self.photo.size > 10 * 1024 * 1024:  # 10 MB
            raise ValidationError({'photo': 'Photo must not exceed 10 MB.'})
        
        if self.video and self.video.size > 100 * 1024 * 1024:  # 100 MB
            raise ValidationError({'video': 'Video must not exceed 100 MB.'})
    
    def save(self, *args, **kwargs):
        """Call clean() before saving"""
        self.full_clean()
        super().save(*args, **kwargs)
    
    @property
    def has_media(self):
        """Check if memory has any media attached"""
        return bool(self.photo or self.video)
    
    @property
    def needs_ai_analysis(self):
        """Check if memory needs AI analysis"""
        return not self.ai_analyzed and (self.description or self.photo)


# --- AI Analysis Results for Memories ---
class AnalyseIASouvenir(models.Model):
    """Stores AI analysis results for a memory"""
    souvenir = models.OneToOneField(Souvenir, on_delete=models.CASCADE, related_name='analyse_ia')
    
    # Text Analysis
    resume_genere = models.TextField(blank=True, default='', help_text="AI-generated summary")
    mots_cles = models.JSONField(default=list, help_text="Extracted keywords")
    emotion_texte = models.CharField(max_length=50, blank=True, default='', help_text="Emotion from text")
    score_emotion_texte = models.FloatField(default=0.0, help_text="Emotion confidence score (0-1)")
    
    # Image Analysis
    objets_detectes = models.JSONField(default=list, help_text="Detected objects in image")
    lieu_detecte = models.CharField(max_length=200, blank=True, default='', help_text="Detected location")
    personnes_detectees = models.IntegerField(default=0, help_text="Number of faces detected")
    emotion_image = models.CharField(max_length=50, blank=True, default='', help_text="Emotion from image")
    couleurs_dominantes = models.JSONField(default=list, help_text="Dominant colors (hex codes)")
    
    # Metadata
    date_analyse = models.DateTimeField(auto_now_add=True)
    modele_utilise = models.CharField(max_length=100, default='gpt-4', help_text="AI model used")
    confiance_globale = models.FloatField(default=0.0, help_text="Overall confidence score (0-1)")
    
    class Meta:
        verbose_name = "AI Analysis"
        verbose_name_plural = "AI Analyses"
    
    def __str__(self):
        return f"AI Analysis: {self.souvenir.titre}"


# --- Memory Albums ---
class AlbumSouvenir(models.Model):
    """Collection of memories organized by theme or manually"""
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='albums')
    titre = models.CharField(max_length=200, help_text="Album title")
    description = models.TextField(blank=True, help_text="Album description")
    
    # Auto-generation
    is_auto_generated = models.BooleanField(default=False, help_text="Generated by AI")
    theme_auto = models.CharField(max_length=100, blank=True, default='', help_text="Auto-detected theme")
    
    souvenirs = models.ManyToManyField(Souvenir, related_name='albums', blank=True)
    
    # Visuals
    couverture_generee = models.ImageField(upload_to='albums/', blank=True, help_text="Auto-generated cover")
    couleur_theme = models.CharField(max_length=7, default='#3498db', help_text="Theme color (hex)")
    
    # Settings
    is_public = models.BooleanField(default=False)
    ordre_affichage = models.IntegerField(default=0, help_text="Display order")
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['ordre_affichage', '-created_at']
        verbose_name = "Memory Album"
        verbose_name_plural = "Memory Albums"
    
    def __str__(self):
        return self.titre
    
    @property
    def souvenirs_count(self):
        return self.souvenirs.count()


# --- Time Capsules ---
class CapsuleTemporelle(models.Model):
    """Time-locked memories that open in the future"""
    souvenir = models.OneToOneField(Souvenir, on_delete=models.CASCADE, related_name='capsule')
    
    # Timing
    date_verrouillage = models.DateTimeField(auto_now_add=True)
    date_ouverture = models.DateField(help_text="Date when capsule unlocks")
    
    # Future Message
    message_futur = models.TextField(help_text="Message to your future self")
    emotion_predite_par_ia = models.CharField(max_length=50, blank=True, default='', help_text="AI-predicted future emotion")
    
    # Status
    is_opened = models.BooleanField(default=False)
    date_ouverture_reelle = models.DateTimeField(null=True, blank=True, help_text="Actual opening date")
    
    # Reflection after opening
    reflexion_ouverture = models.TextField(blank=True, default='', help_text="Reflection upon opening")
    emotion_reelle = models.CharField(max_length=50, blank=True, default='', help_text="Actual emotion upon opening")
    
    class Meta:
        verbose_name = "Time Capsule"
        verbose_name_plural = "Time Capsules"
        ordering = ['date_ouverture']
    
    def __str__(self):
        status = "Opened" if self.is_opened else "Locked"
        return f"{status}: {self.souvenir.titre} (opens {self.date_ouverture})"
    
    @property
    def jours_restants(self):
        """Days remaining until opening"""
        from django.utils import timezone
        if self.is_opened:
            return 0
        delta = self.date_ouverture - timezone.now().date()
        return max(0, delta.days)
    
    @property
    def pourcentage_progression(self):
        """Progress percentage (0-100)"""
        from django.utils import timezone
        if self.is_opened:
            return 100
        total_days = (self.date_ouverture - self.date_verrouillage.date()).days
        if total_days <= 0:
            return 100
        days_passed = (timezone.now().date() - self.date_verrouillage.date()).days
        return min(100, int((days_passed / total_days) * 100))


# --- Memory Sharing ---
class PartageSouvenir(models.Model):
    """Social sharing of memories"""
    VISIBILITE_CHOICES = [
        ('private_link', 'Private Link'),
        ('friends', 'Friends Only'),
        ('public', 'Public'),
    ]
    
    souvenir = models.ForeignKey(Souvenir, on_delete=models.CASCADE, related_name='partages')
    type_visibilite = models.CharField(max_length=50, choices=VISIBILITE_CHOICES, default='private_link')
    
    # Link Settings
    lien_partage = models.UUIDField(unique=True, editable=False, null=True, blank=True)
    code_acces = models.CharField(max_length=20, blank=True, default='', help_text="Optional access code")
    date_expiration = models.DateField(null=True, blank=True, help_text="Link expiration date")
    
    # Content
    message_partage = models.TextField(blank=True, default='', help_text="Accompanying message")
    
    # Statistics
    vues_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    
    # Settings
    autoriser_commentaires = models.BooleanField(default=True)
    autoriser_reactions = models.BooleanField(default=True)
    masquer_infos_perso = models.BooleanField(default=False)
    
    date_partage = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Memory Share"
        verbose_name_plural = "Memory Shares"
    
    def __str__(self):
        return f"Share: {self.souvenir.titre} ({self.type_visibilite})"
    
    def save(self, *args, **kwargs):
        """Generate UUID on first save"""
        if not self.lien_partage:
            self.lien_partage = uuid.uuid4()
        super().save(*args, **kwargs)
    
    @property
    def is_expired(self):
        """Check if share link is expired"""
        from django.utils import timezone
        if not self.date_expiration:
            return False
        return timezone.now().date() > self.date_expiration


# --- Tags for Journal Entries ---
class Tag(models.Model):
    """Tags pour catégoriser les entrées de journal"""
    nom = models.CharField(max_length=50, unique=True, help_text="Nom du tag")
    couleur = models.CharField(max_length=7, default='#3498db', help_text="Couleur du tag (hex)")
    description = models.TextField(blank=True, default='', help_text="Description du tag")
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='tags', null=True, blank=True, help_text="Propriétaire du tag (null = tag global)")
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "Tag"
        verbose_name_plural = "Tags"
        ordering = ['nom']
        unique_together = [['nom', 'utilisateur']]
    
    def __str__(self):
        return self.nom


# --- Humeurs (Moods) ---
class Humeur(models.Model):
    """Humeurs disponibles pour les entrées de journal"""
    INTENSITE_CHOICES = [
        (1, 'Très faible'),
        (2, 'Faible'),
        (3, 'Modérée'),
        (4, 'Forte'),
        (5, 'Très forte'),
    ]
    
    nom = models.CharField(max_length=50, unique=True, help_text="Nom de l'humeur")
    emoji = models.CharField(max_length=10, default='😊', help_text="Emoji représentant l'humeur")
    couleur = models.CharField(max_length=7, default='#FFD700', help_text="Couleur associée (hex)")
    description = models.TextField(blank=True, default='', help_text="Description de l'humeur")
    
    class Meta:
        verbose_name = "Humeur"
        verbose_name_plural = "Humeurs"
        ordering = ['nom']
    
    def __str__(self):
        return f"{self.emoji} {self.nom}"


# --- Journal Entries (for linking memories to journal) ---
class EntreeJournal(models.Model):
    """Journal entries that can be linked to memories"""
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='entrees_journal')
    titre = models.CharField(max_length=200, help_text="Titre de l'entrée")
    contenu_texte = models.TextField(help_text="Contenu de l'entrée")
    
    # Metadata
    lieu = models.CharField(max_length=200, blank=True, default='', help_text="Lieu où l'entrée a été écrite")
    meteo = models.CharField(max_length=50, blank=True, default='', help_text="Météo du jour")
    
    # AI Generated
    auto_summary = models.TextField(blank=True, default='', help_text="Résumé automatique généré par l'IA")
    
    # Privacy
    is_public = models.BooleanField(default=False, help_text="Entrée publique")
    is_favorite = models.BooleanField(default=False, help_text="Entrée favorite")
    
    # Timestamps
    date_creation = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Journal Entry"
        verbose_name_plural = "Journal Entries"
        ordering = ['-date_creation']
        indexes = [
            models.Index(fields=['-date_creation']),
            models.Index(fields=['utilisateur', '-date_creation']),
        ]
    
    def __str__(self):
        return f"{self.titre} - {self.date_creation.strftime('%Y-%m-%d')}"
    
    @property
    def nombre_mots(self):
        """Compte le nombre de mots dans l'entrée"""
        return len(self.contenu_texte.split())
    
    @property
    def tags_list(self):
        """Retourne la liste des tags associés"""
        return [et.tag for et in self.entree_tags.all()]
    
    @property
    def humeurs_list(self):
        """Retourne la liste des humeurs associées"""
        return [eh.humeur for eh in self.entree_humeurs.all()]


# --- Relation Many-to-Many entre EntreeJournal et Tag ---
class EntreeTag(models.Model):
    """Relation entre une entrée de journal et un tag"""
    entree_journal = models.ForeignKey(EntreeJournal, on_delete=models.CASCADE, related_name='entree_tags')
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE, related_name='entree_tags')
    date_association = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('entree_journal', 'tag')
        verbose_name = "Entrée-Tag"
        verbose_name_plural = "Entrées-Tags"
        ordering = ['-date_association']
    
    def __str__(self):
        return f"{self.entree_journal.titre} → {self.tag.nom}"


# --- Relation Many-to-Many entre EntreeJournal et Humeur ---
class EntreeHumeur(models.Model):
    """Relation entre une entrée de journal et une humeur avec intensité"""
    INTENSITE_CHOICES = [
        (1, 'Très faible'),
        (2, 'Faible'),
        (3, 'Modérée'),
        (4, 'Forte'),
        (5, 'Très forte'),
    ]
    
    entree_journal = models.ForeignKey(EntreeJournal, on_delete=models.CASCADE, related_name='entree_humeurs')
    humeur = models.ForeignKey(Humeur, on_delete=models.CASCADE, related_name='entree_humeurs')
    intensite = models.IntegerField(choices=INTENSITE_CHOICES, default=3, help_text="Intensité de l'humeur (1-5)")
    note = models.TextField(blank=True, default='', help_text="Note sur cette humeur")
    date_association = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('entree_journal', 'humeur')
        verbose_name = "Entrée-Humeur"
        verbose_name_plural = "Entrées-Humeurs"
        ordering = ['-intensite', '-date_association']
    
    def __str__(self):
        return f"{self.entree_journal.titre} → {self.humeur.nom} (Intensité: {self.intensite})"


# --- Link between Memories and Journal Entries ---
class SouvenirEntree(models.Model):
    """Many-to-many relationship between memories and journal entries"""
    souvenir = models.ForeignKey(Souvenir, on_delete=models.CASCADE, related_name='entrees_liees')
    entree_journal = models.ForeignKey(EntreeJournal, on_delete=models.CASCADE, related_name='souvenirs_lies')
    date_association = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('souvenir', 'entree_journal')
        verbose_name = "Memory-Journal Link"
        verbose_name_plural = "Memory-Journal Links"
    
    def __str__(self):
        return f"{self.souvenir.titre} ↔ {self.entree_journal.titre}"


# --- PDF Export ---
class ExportPDF(models.Model):
    """PDF export of memories"""
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('ready', 'Ready'),
        ('error', 'Error'),
    ]
    
    utilisateur = models.ForeignKey('User', on_delete=models.CASCADE, related_name='exports_pdf')
    titre_export = models.CharField(max_length=200)
    
    # Content
    souvenirs = models.ManyToManyField(Souvenir, related_name='exports')
    inclure_photos = models.BooleanField(default=True)
    style_template = models.CharField(max_length=50, default='modern', help_text="PDF style template")
    
    # File
    fichier_pdf = models.FileField(upload_to='exports/pdf/', blank=True)
    nombre_pages = models.IntegerField(default=0)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    date_export = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name = "PDF Export"
        verbose_name_plural = "PDF Exports"
        ordering = ['-date_export']
    
    def __str__(self):
        return f"{self.titre_export} - {self.status}"


# --- Motivational Tracking ---
class SuiviMotivationnel(models.Model):
    """Track user engagement and motivation"""
    NIVEAU_MOTIVATION = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('very_high', 'Very High'),
    ]
    
    utilisateur = models.OneToOneField('User', on_delete=models.CASCADE, related_name='suivi_motivationnel')
    
    # Statistics
    nb_souvenirs_ajoutes = models.IntegerField(default=0)
    nb_entrees_journal = models.IntegerField(default=0)
    total_mots_ecrits = models.IntegerField(default=0)
    souvenirs_partages = models.IntegerField(default=0)
    exports_realises = models.IntegerField(default=0)
    
    # Streaks
    jours_consecutifs = models.IntegerField(default=0, help_text="Current streak")
    meilleure_serie = models.IntegerField(default=0, help_text="Best streak")
    
    # Last Activity
    derniere_activite = models.DateTimeField(null=True, blank=True)
    dernier_souvenir_ajoute = models.DateTimeField(null=True, blank=True)
    derniere_entree_journal = models.DateTimeField(null=True, blank=True)
    
    # Motivation
    niveau_motivation = models.CharField(max_length=20, choices=NIVEAU_MOTIVATION, default='medium')
    messages_motivationnels = models.JSONField(default=list, help_text="Motivational messages shown")
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = "Motivational Tracking"
        verbose_name_plural = "Motivational Tracking"
    
    def __str__(self):
        return f"{self.utilisateur.username} - {self.niveau_motivation}"


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
