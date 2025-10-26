from django.contrib import admin
from django.urls import path, include
from core import views_graph
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('accounts/', include('django.contrib.auth.urls')),
    path('', include('core.urls')),
    # New modules
    path('focus/', include('meditation.urls')),
    path('graph/', views_graph.universe_graph_page, name='universe_graph'),
    path('graph/api/graph/', views_graph.graph_data_api, name='graph_data_api'),
    path('graph/api/notes/<str:note_id>/', views_graph.note_detail_api, name='graph_note_detail'),
]

# Servir les fichiers média en développement
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)