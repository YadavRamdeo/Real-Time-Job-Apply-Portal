from django.urls import re_path

# Placeholder websocket routing to satisfy Channels ASGI import.
# Add real consumers here when implementing notifications via websockets.
websocket_urlpatterns = [
    # Example:
    # re_path(r"ws/notifications/$", YourConsumer.as_asgi()),
]
