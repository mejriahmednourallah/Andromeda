import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from django.urls import path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'andromeda.settings')

import meditation.consumers as meditation_consumers
import core.consumers as core_consumers

websocket_urlpatterns = [
    path('ws/focus/', meditation_consumers.FocusConsumer.as_asgi()),
    path('ws/graph/', core_consumers.GraphConsumer.as_asgi()),
]

application = ProtocolTypeRouter({
    'http': get_asgi_application(),
    'websocket': AuthMiddlewareStack(
        URLRouter(websocket_urlpatterns)
    ),
})
