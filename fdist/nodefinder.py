import logging
import socket
import time

import pykka

BROADCAST = {'cmd': 'BROADCAST'}


class Announcer(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, local_node, broadcast_port, interval_seconds):
        super(Announcer, self).__init__()
        self.logger = logging.getLogger(Announcer.__name__)

        self.interval_seconds = interval_seconds
        self.message = """{{ "node": "{0}:{1}" }}""".format(local_node[0], str(local_node[1]))
        self.addr = ('<broadcast>', broadcast_port)

        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def on_start(self):
        self.logger.info('started')
        self.poke()

    def on_receive(self, message):
        if message is BROADCAST:
            self.broadcast()
            time.sleep(self.interval_seconds)
            self.poke()

    def poke(self):
        self.actor_ref.tell(BROADCAST)

    def broadcast(self):
        self.socket.sendto(self.message, self.addr)
