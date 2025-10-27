from django.db import models
from django.conf import settings
from django.utils.text import slugify


class Tag(models.Model):
    """Tags for organizing notes"""
    name = models.CharField(max_length=50, unique=True)
    color = models.CharField(max_length=7, default="#FF8C42")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return self.name


class Note(models.Model):
    """Main note model - Obsidian-style markdown notes"""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='user_notes')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, blank=True)
    content = models.TextField(blank=True)
    tags = models.ManyToManyField(Tag, blank=True, related_name='notes')

    # Metadata
    is_pinned = models.BooleanField(default=False)
    is_archived = models.BooleanField(default=False)
    is_deleted = models.BooleanField(default=False)  # Soft delete

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    deleted_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['-is_pinned', '-updated_at']
        indexes = [
            models.Index(fields=['user', '-updated_at']),
            models.Index(fields=['user', 'is_deleted']),
        ]

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def get_backlinks(self):
        """Get all notes that link to this note"""
        return self.incoming_links.all()

    def get_word_count(self):
        """Calculate word count"""
        return len(self.content.split())


class NoteLink(models.Model):
    """Links between notes"""
    source_note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='outgoing_links')
    target_note = models.ForeignKey(Note, on_delete=models.CASCADE, related_name='incoming_links')
    link_strength = models.FloatField(default=1.0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('source_note', 'target_note')
