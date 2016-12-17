import json
import logging
import socket
import time
from _socket import timeout
from thread import start_new_thread

import pykka

BROADCAST = {'cmd': 'BROADCAST'}


def to_local_node_message(local_node):
    return json.dumps({"node": {
        "ip": local_node[0],
        "port": local_node[1]}
    })


def from_local_node_message(message):
    node_info = json.loads(message)['node']
    return node_info['ip'], node_info['port']


# broadcasts local IP/port
class Announcer(pykka.ThreadingActor):
    use_daemon_thread = True

    def __init__(self, local_node, broadcast_port, interval_seconds):
        super(Announcer, self).__init__()
        self.logger = logging.getLogger(Announcer.__name__)

        self.interval_seconds = interval_seconds
        self.message = to_local_node_message(local_node)
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


# receives broadcast and sends off dict of remote node -> port
class NodeFinder(object):
    def __init__(self, receiver, broadcast_port):
        super(NodeFinder, self).__init__()
        self.logger = logging.getLogger(NodeFinder.__name__)
        self.running = True

        self.socket = self.setup_socket(broadcast_port)
        self.logger.debug("socket opened [%s]", broadcast_port)
        self.receiver = receiver
        self.nodes = {}
        start_new_thread(self.run, ())

    def run(self):
        while self.running:
            try:
                message, address = self.socket.recvfrom(1024)
                self.logger.debug("received from [%s]: %s-%s", address, type(message), message)
                ip, port = from_local_node_message(message)

                self.nodes[ip] = port
                self.receiver.tell(self.nodes)
            except timeout:
                pass

        self.socket.close()

    @staticmethod
    def setup_socket(broadcast_port):
        sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sck.settimeout(1.0)
        sck.bind(('', broadcast_port))
        return sck

    def stop(self):
        self.running = False
