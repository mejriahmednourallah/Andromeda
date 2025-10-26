from django.urls import path
from . import views

app_name = 'meditation'

urlpatterns = [
    path('', views.focus_timer_page, name='focus_timer'),
    path('api/categories/', views.get_categories, name='get_categories'),
    path('api/sessions/start/', views.start_session, name='start_session'),
    path('api/sessions/<int:session_id>/pause/', views.pause_session, name='pause_session'),
    path('api/sessions/<int:session_id>/resume/', views.resume_session, name='resume_session'),
    path('api/sessions/<int:session_id>/complete/', views.complete_session, name='complete_session'),
    path('api/sessions/', views.get_sessions, name='get_sessions'),
    path('api/stats/', views.get_stats, name='get_stats'),
]
