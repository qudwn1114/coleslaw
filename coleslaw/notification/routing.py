from django.urls import re_path, path

from notification import consumers

websocket_urlpatterns = [
    path('ws/shop/<int:shop_id>/', consumers.NotificationConsumer.as_asgi()),
]