from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/email-status/(?P<user_id>\w+)/$', consumers.EmailStatusConsumer.as_asgi()),
]
