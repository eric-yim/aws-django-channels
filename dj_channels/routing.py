from channels.routing import ProtocolTypeRouter
from channels.auth import AuthMiddlewareStack
from channels.routing import ProtocolTypeRouter, URLRouter
import stream.routing
from channels.security.websocket import AllowedHostsOriginValidator, OriginValidator


#application = ProtocolTypeRouter({
#    # (http->django views is added by default)
#    'websocket': AllowedHostsOriginValidator(
#        AuthMiddlewareStack(
#            URLRouter(
#                stream.routing.websocket_urlpatterns
#            )
#        ),
#    )
#})
application = ProtocolTypeRouter({
    # (http->django views is added by default)
    'websocket': URLRouter(
                stream.routing.websocket_urlpatterns
            )
})
