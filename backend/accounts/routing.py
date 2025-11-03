from django.urls import re_path
from .consumers import NotificationConsumer

# WebSocket routing for real-time notifications
websocket_urlpatterns = [
    re_path(r"^ws/notifications/$", NotificationConsumer.as_asgi()),
]
