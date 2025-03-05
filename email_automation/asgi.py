import django
import os
from channels.routing import ProtocolTypeRouter, URLRouter
from django.core.asgi import get_asgi_application
from channels.auth import AuthMiddlewareStack
from email_sender  import routing 

import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'email_automation.settings')

# django.setup()

django_asgi_app = get_asgi_application()

application = ProtocolTypeRouter({
    "http": django_asgi_app, 
    "websocket": AuthMiddlewareStack(
        URLRouter(
            routing.websocket_urlpatterns 
        )
    ),
})



