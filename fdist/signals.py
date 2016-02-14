from django.dispatch.dispatcher import Signal

SYSTEM_SHUTDOWN = Signal()
PEER_UPDATE = Signal(providing_args=["peers"])
VERSION_UPDATE = Signal(providing_args=["version"])
