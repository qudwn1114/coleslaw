from django.urls import re_path, path

from notification import consumers

websocket_urlpatterns = [
    path('ws/shop/<int:shop_id>/order/', consumers.OrderConsumer.as_asgi()),
    path('ws/shop/<int:shop_id>/entry/<int:entry_queue_id>/', consumers.EntryConsumer.as_asgi()),
]