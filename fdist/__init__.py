import logging
import sys

from fdist.globals import LOG_LEVEL

logging.basicConfig(level=LOG_LEVEL,
                    format='%(asctime)s %(levelname)s [%(name)-5s] %(message)s',
                    stream=sys.stdout
                    )


def main():
    logging.info('FDIST started')
