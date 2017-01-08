import json
import socket
import time

from log_actor import LogActor
from messages import SELF_POKE, broadcast_message, LOCAL_FILES, command


class Announcer(LogActor):
    def __init__(self, fe_port, broadcast_port, interval_seconds):
        super(Announcer, self).__init__()

        self.interval_seconds = interval_seconds
        self.fe_port = fe_port
        self.message = broadcast_message(self.fe_port, [])
        self.addr = ('<broadcast>', broadcast_port)

    def on_start(self):
        super(Announcer, self).on_start()
        self.poke()

    def on_receive(self, message):
        if command(message) == LOCAL_FILES:
            self.message = broadcast_message(self.fe_port, message['files'])

        if message is SELF_POKE:
            self.broadcast()
            time.sleep(self.interval_seconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(SELF_POKE)

    def broadcast(self):
        self.logger.debug('broadcasting [%s]', self.message)
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        s.sendto(json.dumps(self.message), self.addr)
        s.close()
