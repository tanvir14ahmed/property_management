import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

# Initialize Django ASGI application early to ensure the AppRegistry
# is populated before importing consumers and routing modules that
# may import ORM models.
django_asgi_app = get_asgi_application()

import chatapp.routing
import notifications.routing

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": AuthMiddlewareStack(
        URLRouter(
            chatapp.routing.websocket_urlpatterns +
            notifications.routing.websocket_urlpatterns
        )
    ),
})
