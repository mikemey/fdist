import logging
import sys
from threading import current_thread

from node_connect import NodeConnect

BROADCAST_PORT = 6400
BROADCAST_INTERVAL_SEC = 5

FILE_EXCHANGE_PORT = 6401
LOG_LEVEL = logging.INFO


def init_logging(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level,
                        format='%(levelname)5s [%(threadName)-10s] %(message)s',
                        stream=sys.stdout
                        )


def main():
    current_thread().setName('main')
    init_logging(LOG_LEVEL)
    NodeConnect(BROADCAST_PORT, FILE_EXCHANGE_PORT, BROADCAST_INTERVAL_SEC)
    logging.info('FDIST started')
