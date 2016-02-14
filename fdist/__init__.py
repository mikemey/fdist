import logging
from threading import current_thread

from django.dispatch.dispatcher import Signal

from node_connect import NodeConnect


def init_logging(log_level=logging.DEBUG):
    logging.basicConfig(level=log_level,
                        format='%(levelname)-5s [%(threadName)-10s] %(message)s',
                        )


def main():
    current_thread().setName('main')
    init_logging(logging.INFO)
    NodeConnect(4001)
    logging.info('FDIST started')


version_update = Signal(providing_args=["version"])
shutdown_sig = Signal()
