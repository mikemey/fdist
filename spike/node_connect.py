import logging
import socket
from _socket import timeout
from threading import Thread
from time import sleep


class NodeConnect:
    def __init__(self, broadcast_port, fe_port, broadcast_interval=1):
        self.port = broadcast_port

        name = 'NC_' + str(self.port)
        self.setup_broadcaster(name, broadcast_port, broadcast_interval, fe_port)
        BroadcastReceiver(name + "_RB", broadcast_port).start()

    @staticmethod
    def setup_broadcaster(name, broadcast_port, broadcast_interval, fe_port):
        local_address = "%s-%s" % (
            socket.gethostbyname(socket.gethostname()),
            str(fe_port))
        ScheduledBroadcast(name + "_BC", local_address, broadcast_port, broadcast_interval).start()


class ScheduledBroadcast(Thread):
    def __init__(self, name, message, broadcast_port, broadcast_interval):
        Thread.__init__(self, name=name)
        self.message = message
        self.broadcast_port = broadcast_port
        self.broadcast_interval = broadcast_interval

        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)

    def teardown(self):
        self.running = False

    def run(self):
        try:
            while self.running:
                self.broadcast_message(self.message)
                sleep(self.broadcast_interval)
        except KeyboardInterrupt:
            self.teardown()

        logging.info("shutting down.")

    def broadcast_message(self, message):
        logging.debug("broadcasting message: [%s]", message)
        self.socket.sendto(message, ('<broadcast>', self.broadcast_port))


class BroadcastReceiver(Thread):
    def __init__(self, name, port):
        Thread.__init__(self, name=name)
        self.setDaemon(True)

        self.running = True
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.bind(('', port))
        self.socket.settimeout(1.0)
        # SYSTEM_SHUTDOWN.connect(self.teardown)

    def teardown(self, sender, **kwargs):
        self.running = False

    def run(self):
        while self.running:
            try:
                bcm = self.socket.recvfrom(1024)
                logging.debug('received broadcast message: [%s]', bcm[0])
            except timeout:
                pass
