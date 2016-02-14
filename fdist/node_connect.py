import logging
from threading import Thread
from time import sleep


class NodeConnect:
    def __init__(self, port):
        self.port = port

        name = 'NC_' + str(self.port)
        self.broadcaster = ScheduledBroadcast(name)
        self.broadcaster.start()


class ScheduledBroadcast(Thread):
    def __init__(self, name):
        super(ScheduledBroadcast, self).__init__(self, name=name)
        self.setDaemon(True)
        self.running = True

    def run(self):
        try:
            while self.running:
                sleep(1)
                self.announce_myself()
        except KeyboardInterrupt:
            logging.info("KLL received")
            self.running = False

    def announce_myself(self):
        logging.debug("ANN sent")

# import socket
# import threading
#
#
# def handle_client(sock):
#     with sock.makefile() as f:
#         sock.close()
#         for line in f:
#             f.writeline(line)
#
#
# def serve_forever():
#     server = socket.socket()
#     server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
#     server.bind(('', 12345))
#     server.listen(1)
#     while True:
#         conn, address = server.accept()
#         thread = threading.Thread(target=handle_client, args=[conn])
#         thread.daemon = True
#         thread.start()
#
#
# s = socket(AF_INET, SOCK_DGRAM)
# s.bind(('', 0))
# s.setsockopt(SOL_SOCKET, SO_BROADCAST, 1)
#
# while 1:
#     data = repr(time.time()) + '\n'
#     s.sendto(data, ('<broadcast>', MYPORT))
#     time.sleep(2)
