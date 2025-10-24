from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    # Home & Dashboard
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notes/<uuid:note_id>/', views.note_detail, name='note_detail'),
    path('accounts/signup/', views.signup, name='signup'),
    path('profile/', views.profile, name='profile'),
    
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
]