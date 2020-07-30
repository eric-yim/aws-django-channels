from django.urls import path,re_path
from channels.routing import ProtocolTypeRouter,URLRouter
from channels.auth import AuthMiddlewareStack

from . import consumers




websocket_urlpatterns = [


    re_path(r'ws/stream/(?P<room_name>\w+)/$', consumers.MyConsumer),
]
