import bz2
import cPickle
import errno
import logging
import socket
import traceback
from logging import DEBUG
from time import sleep

from fdist.globals import md5_hash

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
    payload = cPickle.dumps(data)
    if is_network_log_enabled():
        send_log(src, 'payload length [%s]', len(payload))
        send_log(src, 'payload hash [%s]', md5_hash(payload))

    frame = create_frame(src, payload)
    total_bytes_sent = 0
    while len(frame) > 0:
        try:
            bytes_sent = sck.send(frame)
            total_bytes_sent += bytes_sent
            frame = frame[bytes_sent:]
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                sleep(0)
            else:
                send_log(src, 'error: %s', e.message)
                if is_network_log_enabled():
                    traceback.print_exc()
                raise e
    send_log(src, 'total sent [%s] bytes', total_bytes_sent)


def create_frame(src, data):
    compressed = bz2.compress(data)
    frame_len = str(len(compressed))
    send_log(src, 'compressed frame size [%s] bytes', frame_len)
    return frame_len + FRAME_SEPARATOR + compressed


def read_data_from(connection, src=''):
    recv_log(src, 'start')

    def length_read(loop_data, chunk):
        buf = loop_data

        if str(chunk) == FRAME_SEPARATOR:
            recv_log(src, 'compressed frame size [%s] bytes', buf)
            return long(buf), True
        buf += chunk
        return buf, None

    frame_length = read_loop(src, connection, length_read, 1, '')
    total_bytes_received = frame_length + len(FRAME_SEPARATOR)

    def data_read(loop_data, chunk):
        uncompressed, read_counter, decompressor = loop_data
        read_counter += len(chunk)

        uncompressed += decompressor.decompress(chunk)
        if read_counter >= frame_length:
            if is_network_log_enabled():
                recv_log(src, 'payload length [%s]', len(uncompressed))
                recv_log(src, 'payload hash [%s]', md5_hash(uncompressed))
            return (uncompressed, read_counter), True
        return (uncompressed, read_counter, decompressor), None

    frame_data, bytes_received = read_loop(src, connection, data_read, CHUNK_SIZE, (b'', 0, bz2.BZ2Decompressor()))
    total_bytes_received += bytes_received
    send_log(src, 'total recv [%s] bytes', total_bytes_received)
    return cPickle.loads(frame_data)


def read_loop(src, connection, read_func, buffersize, loop_data):
    while True:
        try:
            chunk = connection.recv(buffersize)

            loop_data, done = read_func(loop_data, chunk)
            if done:
                return loop_data
        except socket.error as e:
            err = e.args[0]
            if err == errno.EAGAIN:
                sleep(0)
            else:
                recv_log(src, 'error: %s', e.message)
                if is_network_log_enabled():
                    traceback.print_exc()
                raise e
