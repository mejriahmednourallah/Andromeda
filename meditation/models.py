from django.db import models
from django.conf import settings


class FocusCategory(models.Model):
    name = models.CharField(max_length=100)
    color = models.CharField(max_length=7, default="#FF8C42")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name_plural = "Focus Categories"
        ordering = ['name']

    def __str__(self):
        return self.name


class FocusSession(models.Model):
    STATUS_CHOICES = [
        ('ongoing', 'Ongoing'),
        ('paused', 'Paused'),
        ('completed', 'Completed'),
    ]

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='focus_sessions')
    category = models.ForeignKey(FocusCategory, on_delete=models.SET_NULL, null=True, blank=True)
    start_time = models.DateTimeField(auto_now_add=True)
    end_time = models.DateTimeField(null=True, blank=True)
    duration = models.IntegerField(default=0)  # in minutes
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ongoing')
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-start_time']

    def __str__(self):
        return f"{self.user} - {self.category} ({self.status})"
