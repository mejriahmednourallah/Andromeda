from django.contrib import admin
from .models import (
    User, Note, Link, Template, Attachment, APIIntegration, AITask,
    Souvenir, AnalyseIASouvenir, AlbumSouvenir, CapsuleTemporelle,
    EntreeJournal, SouvenirEntree, PartageSouvenir,
    ExportPDF, SuiviMotivationnel, Badge, UserBadge, HistoireInspirante, DefiQuotidien,
    Tag, Humeur, EntreeTag, EntreeHumeur
)
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    pass

@admin.register(Souvenir)
class SouvenirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'date_evenement', 'emotion', 'theme', 'is_favorite', 'ai_analyzed', 'created_at')
    list_filter = ('date_evenement', 'emotion', 'theme', 'is_favorite', 'is_public', 'ai_analyzed', 'created_at')
    search_fields = ('titre', 'description', 'utilisateur__username', 'lieu', 'personnes_presentes')
    date_hierarchy = 'date_evenement'
    readonly_fields = ('id', 'created_at', 'updated_at', 'ai_summary', 'ai_emotion_detected', 'ai_tags', 'ai_analysis_date')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('utilisateur', 'titre', 'description', 'date_evenement')
        }),
        ('Media', {
            'fields': ('photo', 'video')
        }),
        ('Metadata', {
            'fields': ('emotion', 'theme', 'lieu', 'personnes_presentes', 'is_favorite', 'is_public')
        }),
        ('AI Analysis', {
            'fields': ('ai_analyzed', 'ai_summary', 'ai_emotion_detected', 'ai_tags', 'ai_analysis_date'),
            'classes': ('collapse',)
        }),
        ('System', {
            'fields': ('id', 'created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_favorite', 'analyze_with_ai']
    
    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} memories marked as favorite.')
    mark_as_favorite.short_description = "Mark selected as favorite"
    
    def analyze_with_ai(self, request, queryset):
        from .ai_services import AIAnalysisService
        count = 0
        for souvenir in queryset:
            if not souvenir.ai_analyzed:
                try:
                    AIAnalysisService.analyze_memory(souvenir)
                    count += 1
                except Exception:
                    pass
        self.message_user(request, f'{count} memories analyzed with AI.')
    analyze_with_ai.short_description = "Analyze with AI"


@admin.register(AnalyseIASouvenir)
class AnalyseIASouvenirAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'emotion_texte', 'emotion_image', 'confiance_globale', 'date_analyse')
    list_filter = ('date_analyse', 'emotion_texte', 'emotion_image')
    search_fields = ('souvenir__titre', 'resume_genere')
    readonly_fields = ('souvenir', 'date_analyse')


@admin.register(AlbumSouvenir)
class AlbumSouvenirAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'is_auto_generated', 'is_public', 'created_at')
    list_filter = ('is_auto_generated', 'is_public', 'created_at')
    search_fields = ('titre', 'description', 'utilisateur__username')
    filter_horizontal = ('souvenirs',)


@admin.register(CapsuleTemporelle)
class CapsuleTemporelleAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'date_ouverture', 'is_opened', 'date_verrouillage', 'jours_restants')
    list_filter = ('is_opened', 'date_ouverture', 'date_verrouillage')
    search_fields = ('souvenir__titre', 'message_futur')
    date_hierarchy = 'date_ouverture'
    readonly_fields = ('date_verrouillage', 'date_ouverture_reelle', 'jours_restants', 'pourcentage_progression')


class EntreeTagInline(admin.TabularInline):
    model = EntreeTag
    extra = 1
    autocomplete_fields = ['tag']


class EntreeHumeurInline(admin.TabularInline):
    model = EntreeHumeur
    extra = 1
    autocomplete_fields = ['humeur']


@admin.register(EntreeJournal)
class EntreeJournalAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'is_favorite', 'is_public', 'nombre_mots', 'date_creation')
    list_filter = ('date_creation', 'is_favorite', 'is_public')
    search_fields = ('titre', 'contenu_texte', 'utilisateur__username', 'lieu')
    date_hierarchy = 'date_creation'
    readonly_fields = ('date_creation', 'updated_at', 'nombre_mots')
    inlines = [EntreeTagInline, EntreeHumeurInline]
    
    fieldsets = (
        ('Information principale', {
            'fields': ('utilisateur', 'titre', 'contenu_texte')
        }),
        ('Métadonnées', {
            'fields': ('lieu', 'meteo', 'is_favorite', 'is_public')
        }),
        ('Système', {
            'fields': ('date_creation', 'updated_at', 'nombre_mots'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_favorite']
    
    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} entrées marquées comme favorites.')
    mark_as_favorite.short_description = "Marquer comme favorite"


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('nom', 'couleur', 'utilisateur', 'created_at')
    list_filter = ('created_at', 'utilisateur')
    search_fields = ('nom', 'description')
    readonly_fields = ('created_at',)
    list_per_page = 50


@admin.register(Humeur)
class HumeurAdmin(admin.ModelAdmin):
    list_display = ('nom', 'emoji', 'couleur')
    search_fields = ('nom', 'description')
    list_per_page = 50


@admin.register(EntreeTag)
class EntreeTagAdmin(admin.ModelAdmin):
    list_display = ('entree_journal', 'tag', 'date_association')
    list_filter = ('date_association', 'tag')
    search_fields = ('entree_journal__titre', 'tag__nom')
    date_hierarchy = 'date_association'
    readonly_fields = ('date_association',)
    autocomplete_fields = ['entree_journal', 'tag']


@admin.register(EntreeHumeur)
class EntreeHumeurAdmin(admin.ModelAdmin):
    list_display = ('entree_journal', 'humeur', 'intensite', 'date_association')
    list_filter = ('date_association', 'humeur', 'intensite')
    search_fields = ('entree_journal__titre', 'humeur__nom', 'note')
    date_hierarchy = 'date_association'
    readonly_fields = ('date_association',)
    autocomplete_fields = ['entree_journal', 'humeur']


@admin.register(SouvenirEntree)
class SouvenirEntreeAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'entree_journal', 'date_association')
    list_filter = ('date_association',)
    search_fields = ('souvenir__titre', 'entree_journal__titre')
    date_hierarchy = 'date_association'
    readonly_fields = ('date_association',)


@admin.register(PartageSouvenir)
class PartageSouvenirAdmin(admin.ModelAdmin):
    list_display = ('souvenir', 'type_visibilite', 'date_partage', 'vues_count', 'likes_count', 'is_expired')
    list_filter = ('type_visibilite', 'date_partage', 'date_expiration')
    search_fields = ('souvenir__titre', 'message_partage')
    date_hierarchy = 'date_partage'
    readonly_fields = ('lien_partage', 'date_partage', 'is_expired')


@admin.register(ExportPDF)
class ExportPDFAdmin(admin.ModelAdmin):
    list_display = ('titre_export', 'utilisateur', 'date_export', 'status', 'nombre_pages')
    list_filter = ('status', 'date_export')
    search_fields = ('titre_export', 'utilisateur__username')
    date_hierarchy = 'date_export'
    readonly_fields = ('date_export',)
    filter_horizontal = ('souvenirs',)


@admin.register(SuiviMotivationnel)
class SuiviMotivationnelAdmin(admin.ModelAdmin):
    list_display = ('utilisateur', 'niveau_motivation', 'nb_souvenirs_ajoutes', 'jours_consecutifs', 'meilleure_serie')
    list_filter = ('niveau_motivation', 'created_at')
    search_fields = ('utilisateur__username',)
    readonly_fields = ('created_at', 'updated_at')


@admin.register(Badge)
class BadgeAdmin(admin.ModelAdmin):
    list_display = ('name', 'code', 'icon', 'requirement_value', 'created_at')
    list_filter = ('code', 'created_at')
    search_fields = ('name', 'description')


@admin.register(UserBadge)
class UserBadgeAdmin(admin.ModelAdmin):
    list_display = ('user', 'badge', 'progress', 'is_unlocked', 'progress_percentage', 'earned_at')
    list_filter = ('earned_at', 'badge__code')
    search_fields = ('user__username', 'badge__name')
    readonly_fields = ('earned_at', 'is_unlocked', 'progress_percentage')


@admin.register(HistoireInspirante)
class HistoireInspiranteAdmin(admin.ModelAdmin):
    list_display = ('celebrite', 'utilisateur', 'est_simulee', 'is_favorite', 'created_at')
    list_filter = ('est_simulee', 'is_favorite', 'created_at')
    search_fields = ('celebrite', 'reflexion_text', 'histoire_generee', 'utilisateur__username')
    date_hierarchy = 'created_at'
    readonly_fields = ('id', 'created_at', 'updated_at', 'reflexion_courte')
    
    fieldsets = (
        ('Information Principale', {
            'fields': ('utilisateur', 'celebrite', 'is_favorite')
        }),
        ('Contenu', {
            'fields': ('reflexion_text', 'histoire_generee', 'notes_personnelles')
        }),
        ('Métadonnées IA', {
            'fields': ('est_simulee', 'modele_utilise'),
            'classes': ('collapse',)
        }),
        ('Système', {
            'fields': ('id', 'created_at', 'updated_at', 'reflexion_courte'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_favorite']
    
    def mark_as_favorite(self, request, queryset):
        updated = queryset.update(is_favorite=True)
        self.message_user(request, f'{updated} histoires marquées comme favorites.')
    mark_as_favorite.short_description = "Marquer comme favorite"


@admin.register(DefiQuotidien)
class DefiQuotidienAdmin(admin.ModelAdmin):
    list_display = ('titre', 'utilisateur', 'date_defi', 'statut', 'categorie', 'duree_estimee', 'priorite')
    list_filter = ('statut', 'categorie', 'priorite', 'date_defi', 'est_genere_par_ia')
    search_fields = ('titre', 'description', 'utilisateur__username', 'histoire_inspirante__celebrite')
    date_hierarchy = 'date_defi'
    readonly_fields = ('id', 'created_at', 'updated_at', 'est_termine', 'est_en_retard')
    
    fieldsets = (
        ('Information Principale', {
            'fields': ('utilisateur', 'histoire_inspirante', 'titre', 'description')
        }),
        ('Planning', {
            'fields': ('date_defi', 'duree_estimee', 'priorite', 'categorie')
        }),
        ('État', {
            'fields': ('statut', 'date_completion', 'notes_utilisateur')
        }),
        ('Métadonnées', {
            'fields': ('est_genere_par_ia',),
            'classes': ('collapse',)
        }),
        ('Système', {
            'fields': ('id', 'created_at', 'updated_at', 'est_termine', 'est_en_retard'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_completed', 'mark_as_pending']
    
    def mark_as_completed(self, request, queryset):
        from django.utils import timezone
        updated = queryset.update(statut='completed', date_completion=timezone.now())
        self.message_user(request, f'{updated} défis marqués comme terminés.')
    mark_as_completed.short_description = "Marquer comme terminé"
    
    def mark_as_pending(self, request, queryset):
        updated = queryset.update(statut='pending', date_completion=None)
        self.message_user(request, f'{updated} défis marqués comme à faire.')
    mark_as_pending.short_description = "Marquer comme à faire"


admin.site.register(Note)
admin.site.register(Link)
admin.site.register(Template)
admin.site.register(Attachment)
admin.site.register(APIIntegration)
admin.site.register(AITask)