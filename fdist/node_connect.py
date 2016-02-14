import logging
import threading
from socket import *
from thread import *
from time import sleep

from signals import SYSTEM_SHUTDOWN


class NodeConnect:
    def __init__(self, broadcast_port, fe_port, broadcast_interval=1):
        self.port = broadcast_port

        name = 'NC_' + str(self.port)
        start_new_thread(send_broadcast, (name, broadcast_port, fe_port, broadcast_interval,))
        start_new_thread(receive_broadcast, (fe_port,), name='BC_RECEIVER')


def send_broadast(name, broadcast_port, fe_port,broadcast_interval):
    running = True
    local_address = "%s-%s" % (
        socket.gethostbyname(socket.gethostname()),
        str(fe_port))

    socket = bc_socket()

    self.broadcast_interval = broadcast_interval
    self.message = message
    SYSTEM_SHUTDOWN.connect(teardown)

    def teardown( sender, **kwargs):
        running = False

    def run(self):
        try:
            while self.running:
                self.broadcast_message(self.message)
                sleep(self.broadcast_interval)
        except KeyboardInterrupt:
            self.teardown(None)

        logging.info("shutting down.")

    def broadcast_message(self, message):
        logging.debug("broadcasting message: [%s]", message)
        self.socket.sendto(message, ('<broadcast>', self.broadcast_port))


def bc_socket():
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    s.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
    return s


def receive_broadcast(port):
    def update_peers(conn):
        while True:
            data = conn.recv(1024)
            if not data:
                break
            print "received:", data

        conn.close()

    s = bc_socket()
    s.bind(('', port))
    s.listen(10)

    while 1:
        connection, addr = s.accept()
        start_new_thread(update_peers, (connection,))

    s.close()
