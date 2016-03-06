import logging
import sys


def init_logging(level=logging.INFO):
    logging.basicConfig(level=level,
                        format='%(asctime)s %(levelname)s [%(name)-5s] %(message)s',
                        stream=sys.stdout
                        )


def main():
    init_logging()
    logging.info('FDIST started')
