from django.urls import path
from . import views
from . import views_journal
from . import views_ai

app_name = 'core'

urlpatterns = [
    # Home & Dashboard
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notes/<uuid:note_id>/', views.note_detail, name='note_detail'),
    path('accounts/signup/', views.signup, name='signup'),
    
    # === MEMORIES DASHBOARD (UNIFIED) ===
    path('memories/dashboard/', views.memories_dashboard, name='memories_dashboard'),
    
    # === LEGACY REDIRECTS ===
    path('memories/', views.memories_dashboard, name='liste_souvenirs'),  # Redirect old URL
    path('ai-gallery/', views.memories_dashboard, name='galerie_ia'),  # Redirect old URL
    
    # === MEMORIES (CRUD) ===
    path('memories/add/', views.ajouter_souvenir, name='ajouter_souvenir'),
    path('memories/<uuid:souvenir_id>/', views.detail_souvenir, name='detail_souvenir'),
    path('memories/<uuid:souvenir_id>/edit/', views.modifier_souvenir, name='modifier_souvenir'),
    path('memories/<uuid:souvenir_id>/delete/', views.supprimer_souvenir, name='supprimer_souvenir'),
    
    # === FILTERS & ACTIONS ===
    path('memories/<uuid:souvenir_id>/favorite/', views.toggle_favori, name='toggle_favori'),
    
    # === AI ANALYSIS ===
    path('memories/<uuid:souvenir_id>/analyze/', views.analyser_souvenir_ia, name='analyser_souvenir_ia'),
    
    # === TIME CAPSULES ===
    path('capsules/', views.liste_capsules, name='liste_capsules'),
    path('capsules/create/', views.creer_capsule, name='creer_capsule'),
    path('capsules/generate-message/', views.generate_ai_message, name='generate_ai_message'),
    path('capsules/<int:capsule_id>/', views.detail_capsule, name='detail_capsule'),
    path('capsules/<int:capsule_id>/open/', views.ouvrir_capsule, name='ouvrir_capsule'),
    
    # === ALBUMS ===
    path('albums/', views.liste_albums, name='liste_albums'),
    path('albums/create/', views.creer_album, name='creer_album'),
    path('albums/<int:album_id>/', views.detail_album, name='detail_album'),
    path('albums/<int:album_id>/edit/', views.modifier_album, name='modifier_album'),
    path('albums/<int:album_id>/delete/', views.supprimer_album, name='supprimer_album'),
    
    # === JOURNAL (CRUD) ===
    path('journal/', views_journal.liste_entrees_journal, name='liste_entrees_journal'),
    path('journal/add/', views_journal.ajouter_entree_journal, name='ajouter_entree_journal'),
    path('journal/<int:pk>/', views_journal.detail_entree_journal, name='detail_entree_journal'),
    path('journal/<int:pk>/edit/', views_journal.modifier_entree_journal, name='modifier_entree_journal'),
    path('journal/<int:pk>/delete/', views_journal.supprimer_entree_journal, name='supprimer_entree_journal'),
    path('journal/<int:pk>/favorite/', views_journal.toggle_favori_entree, name='toggle_favori_entree'),
    
    # === TAGS ===
    path('journal/tags/', views_journal.liste_tags, name='liste_tags'),
    path('journal/tags/add/', views_journal.ajouter_tag, name='ajouter_tag'),
    path('journal/tags/<int:pk>/edit/', views_journal.modifier_tag, name='modifier_tag'),
    path('journal/tags/<int:pk>/delete/', views_journal.supprimer_tag, name='supprimer_tag'),
    
    # === STATISTIQUES JOURNAL ===
    path('journal/stats/', views_journal.statistiques_journal, name='statistiques_journal'),
    
    # === EXPORT PDF ===
    path('journal/export-pdf/', views_journal.export_journal_pdf, name='export_journal_pdf'),
    path('journal/<int:pk>/export-pdf/', views_journal.export_entree_pdf, name='export_entree_pdf'),
    
    # === ANALYSE IA (OLD) ===
    path('journal/analyze-ai/', views_journal.analyser_entree_ia, name='analyser_entree_ia'),
    
    # === ANALYSE IA GROQ (NEW) ===
    path('journal/ai/', views_ai.page_analyse_ai, name='page_analyse_ai'),
    path('journal/ai/analyser/<int:pk>/', views_ai.analyser_entree_ai, name='analyser_entree_ai_groq'),
    path('journal/ai/tendances/', views_ai.analyse_tendances_ai, name='analyse_tendances_ai'),
    path('journal/ai/prompt/', views_ai.generer_prompt_ai, name='generer_prompt_ai'),
    path('journal/ai/appliquer-tags/<int:pk>/', views_ai.appliquer_tags_suggeres, name='appliquer_tags_suggeres'),
    
    # === CHATBOT ===
    path('journal/chatbot/', views_ai.page_chatbot, name='page_chatbot'),
    path('journal/chatbot/message/', views_ai.chatbot_message, name='chatbot_message'),
    path('journal/chatbot/questions/<int:pk>/', views_ai.chatbot_questions_suggerees, name='chatbot_questions_suggerees'),
]