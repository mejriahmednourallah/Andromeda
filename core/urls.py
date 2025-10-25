from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('notes/<uuid:note_id>/', views.note_detail, name='note_detail'),
    path('accounts/signup/', views.signup, name='signup'),
    path('moodai/', views.moodai, name='moodai'),
    path('api/moodai/analyze/', views.moodai_analyze, name='moodai_analyze'),
    # URLs pour les souvenirs
    path('souvenirs/', views.liste_souvenirs, name='liste_souvenirs'),
    path('souvenirs/ajouter/', views.ajouter_souvenir, name='ajouter_souvenir'),
    path('souvenirs/<uuid:souvenir_id>/', views.detail_souvenir, name='detail_souvenir'),
    path('souvenirs/<uuid:souvenir_id>/supprimer/', views.supprimer_souvenir, name='supprimer_souvenir'),
]