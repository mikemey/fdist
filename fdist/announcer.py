import json
import logging
import socket
import time

import pykka

from messages import SELF_POKE, broadcast_message, LOCAL_FILES, command


class Announcer(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, fe_port, broadcast_port, interval_seconds):
        super(Announcer, self).__init__()
        self.logger = logging.getLogger(Announcer.__name__)

        self.interval_seconds = interval_seconds
        self.fe_port = fe_port
        self.message = broadcast_message(self.fe_port, [])
        self.addr = ('<broadcast>', broadcast_port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def on_start(self):
        self.logger.info('started')
        self.poke()

    def on_receive(self, message):
        if command(message) is LOCAL_FILES:
            self.message = broadcast_message(self.fe_port, message['files'])

        if message is SELF_POKE:
            self.broadcast()
            time.sleep(self.interval_seconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(SELF_POKE)

    def broadcast(self):
        print "sending:", json.dumps(self.message)
        self.socket.sendto(json.dumps(self.message), self.addr)
