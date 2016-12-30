import logging
import random
import socket
from unittest import TestCase

from fdist import init_logging

init_logging(logging.DEBUG)
logging.getLogger("pykka").setLevel(logging.INFO)


class LogTestCase(TestCase):
    def setUp(self):
        test_class = self.__class__.__name__
        test_method = self._testMethodName
        print("--------------\nTest run: [{} - {}]".format(test_class, test_method))

    def quickEquals(self, actual, expected):
        self.assertEquals(actual, expected,
                          "Error:\n\tactual  : =={}==\n\texpected: =={}==".format(actual, expected))


class AllItemsIn:
    def __init__(self, expected):
        self.expected = expected

    def __eq__(self, other):
        for exp_item in self.expected:
            if exp_item not in other:
                return False
        return True

    def __repr__(self):
        return "Any(%s)" % self.expected


r = random.Random()


def free_port():
    distance = r.randint(1, 20)
    start = 15000 + distance
    while True:
        try:
            print "try socket", start
            sck = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            sck.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
            sck.settimeout(1.0)
            sck.bind(('', start))
            return start
        except IOError:
            start += distance
        finally:
            sck.close()
