from django.urls import path
from . import views

app_name = 'notes'

urlpatterns = [
    # Page views
    path('', views.note_list, name='list'),
    path('create/', views.note_create, name='create'),
    path('<int:note_id>/', views.note_detail, name='detail'),
    path('<int:note_id>/edit/', views.note_edit, name='edit'),
    path('api/notes/<int:note_id>/', views.api_note_detail, name='api_detail'),
    
    # API endpoints
    path('api/notes/', views.api_notes_list, name='api_list'),
    path('api/notes/create/', views.api_note_create, name='api_create'),
    path('api/notes/<int:note_id>/update/', views.api_note_update, name='api_update'),
    path('api/notes/<int:note_id>/delete/', views.api_note_delete, name='api_delete'),
    path('api/notes/<int:note_id>/restore/', views.api_note_restore, name='api_restore'),
    path('api/notes/<int:note_id>/pin/', views.api_note_pin, name='api_pin'),
    path('api/notes/<int:note_id>/archive/', views.api_note_archive, name='api_archive'),
    path('api/notes/<int:note_id>/autosave/', views.api_note_autosave, name='api_autosave'),
    path('api/tags/', views.api_tags_list, name='api_tags'),
]
