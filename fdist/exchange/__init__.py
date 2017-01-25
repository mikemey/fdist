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
    loops = 3
    while loops > 0:
        loops -= 1
        try:
            while True:
                chunk = connection.recv(CHUNK_SIZE)
                bytes_read = len(chunk)
                buf += chunk
                if bytes_read < CHUNK_SIZE:
                    break
            return buf
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                time.sleep(0)
            else:
                raise e
