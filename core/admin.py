from django.contrib import admin
from .models import User, Note, Link, Template, Attachment, APIIntegration, AITask, Souvenir
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(Souvenir)
class SouvenirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'date_evenement', 'created_at')
    list_filter = ('date_evenement', 'created_at')
    search_fields = ('titre', 'description', 'utilisateur__username')
    date_hierarchy = 'date_evenement'
    readonly_fields = ('id', 'created_at', 'updated_at')
    
    fieldsets = (
        ('Informations principales', {
            'fields': ('utilisateur', 'titre', 'description', 'date_evenement')
        }),
        ('Médias', {
            'fields': ('photo', 'video')
        }),
        ('Métadonnées', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )

admin.site.register(Note)
admin.site.register(Link)
admin.site.register(Template)
admin.site.register(Attachment)
admin.site.register(APIIntegration)
admin.site.register(AITask)