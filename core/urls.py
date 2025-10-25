from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

app_name = 'core'

urlpatterns = [
    # Home & Dashboard
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('story/', views.story_inspiration, name='story_inspiration'),
    path('story/history/', views.story_history, name='story_history'),
    path('story/<uuid:histoire_id>/favorite/', views.toggle_histoire_favorite, name='toggle_histoire_favorite'),
    path('notes/<uuid:note_id>/', views.note_detail, name='note_detail'),
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    
    # === PASSWORD RESET ===
    path('accounts/password_reset/', auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt'
    ), name='password_reset'),
    path('accounts/password_reset/done/', auth_views.PasswordResetDoneView.as_view(
        template_name='registration/password_reset_done.html'
    ), name='password_reset_done'),
    path('accounts/reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='registration/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('accounts/reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='registration/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    # === MEMORIES DASHBOARD (UNIFIED) ===
    path('memories/dashboard/', views.memories_dashboard, name='memories_dashboard'),
    
    # === EMOTIONAL CALENDAR ===
    path('calendar/', views.calendrier_emotionnel, name='calendrier_emotionnel'),
    path('calendar/events/', views.calendrier_emotionnel_events, name='calendrier_emotionnel_events'),
    path('calendar/day-memories/', views.calendrier_emotionnel_day_memories, name='calendrier_emotionnel_day_memories'),
    path('calendar/monthly-analytics/', views.calendrier_emotionnel_monthly_analytics, name='calendrier_emotionnel_monthly_analytics'),
    
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
    path('albums/create-from-suggestion/', views.creer_album_depuis_suggestion, name='creer_album_depuis_suggestion'),
    path('albums/<int:album_id>/', views.detail_album, name='detail_album'),
    path('albums/<int:album_id>/edit/', views.modifier_album, name='modifier_album'),
    path('albums/<int:album_id>/delete/', views.supprimer_album, name='supprimer_album'),
    
    # === PDF EXPORTS ===
    path('exports/pdf/', views.liste_exports_pdf, name='liste_exports_pdf'),
    path('exports/pdf/create/', views.exporter_pdf, name='exporter_pdf'),
    path('exports/pdf/<int:export_id>/download/', views.telecharger_pdf, name='telecharger_pdf'),
]