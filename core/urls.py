from django.urls import path
from . import views

app_name = 'core'

urlpatterns = [
    path('', views.index, name='index'),
    path('notes/<uuid:note_id>/', views.note_detail, name='note_detail'),
    path('accounts/signup/', views.signup, name='signup'),
]