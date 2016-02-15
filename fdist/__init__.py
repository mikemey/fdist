import logging
import signal
import sys
from threading import current_thread

from node_connect import NodeConnect
from signals import SYSTEM_SHUTDOWN

BROADCAST_PORT = 6400
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 6401
LOG_LEVEL = logging.INFO


def init_logging(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level,
                        format='%(levelname)5s [%(threadName)-10s] %(message)s',
                        stream=sys.stdout
                        )


def signal_handler(signal, frame):
    logging.info('SHUTTING DOWN...')
    SYSTEM_SHUTDOWN.send(None)


signal.signal(signal.SIGINT, signal_handler)


def main():
    current_thread().setName('main')
    init_logging()

    NodeConnect(BROADCAST_PORT, FILE_EXCHANGE_PORT, BROADCAST_INTERVAL_SEC)
    logging.info('FDIST started')
