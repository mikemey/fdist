import errno
import logging
import socket
import traceback
from logging import DEBUG
from time import sleep

CHUNK_SIZE = 8192
FRAME_SEPARATOR = ":"

recv_logger, send_logger = None, None


def is_network_log_enabled(): return logging.getLogger('network').isEnabledFor(DEBUG)


if is_network_log_enabled():
    recv_logger = logging.getLogger('recv')
    send_logger = logging.getLogger('send')


def send_log(src, msg, *args, **kwargs):
    if send_logger:
        send_logger.debug('[%s] ' % src + msg, *args, **kwargs)


def recv_log(src, msg, *args, **kwargs):
    if recv_logger:
        recv_logger.debug('[%s] ' % src + msg, *args, **kwargs)


def send_data_to(sck, data, src=''):
    send_log(src, 'start')

    data = frame_data(src, data)
    while len(data) > 0:
        try:
            bytes_sent = sck.send(data)
            data = data[bytes_sent:]
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                sleep(0)
            else:
                send_log(src, 'error: %s', e.message)
                if is_network_log_enabled():
                    traceback.print_exc()
                raise e
    send_log(src, 'payload sent.')


def frame_data(src, data):
    frame_len = str(len(data))
    send_log(src, 'framing %6s bytes', frame_len)
    return frame_len + FRAME_SEPARATOR + data


def read_data_from(connection, src=''):
    recv_log(src, 'start')

    def length_read(buf, chunk):
        if str(chunk) == FRAME_SEPARATOR:
            recv_log(src, 'frame size [%s] bytes', len(buf))
            return buf, True
        buf += chunk
        return buf, None

    frame_len = long(read_loop(src, connection, length_read, 1))

    def data_read(buf, chunk):
        buf += chunk
        if len(buf) >= frame_len:
            recv_log(src, 'payload read.')
            return buf, True
        return buf, None

    return read_loop(src, connection, data_read, CHUNK_SIZE)


def read_loop(src, connection, read_func, buffersize):
    buf = ''
    while True:
        try:
            chunk = connection.recv(buffersize)
            buf, done = read_func(buf, chunk)
            if done:
                return buf
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                sleep(0)
            else:
                recv_log(src, 'error: %s', e.message)
                if is_network_log_enabled():
                    traceback.print_exc()
                raise e
