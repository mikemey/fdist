import errno

import sys

CHUNK_SIZE = 8192

if "darwin" == sys.platform:
    import socket
    import time


    def socket_socket_sendall(self, data):
        while len(data) > 0:
            try:
                bytes_sent = self.send(data)
                data = data[bytes_sent:]
            except socket.error as e:
                err = e.args[0]
                if err == errno.EAGAIN:
                    time.sleep(0)
                else:
                    raise e


    socket._socketobject.sendall = socket_socket_sendall


def read_data_from(connection):
    buf = ''
    while True:
        try:
            chunk = connection.recv(CHUNK_SIZE)
            bytes_read = len(chunk)
            buf += chunk
            if bytes_read < CHUNK_SIZE:
                return buf
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                time.sleep(0)
            else:
                raise e
