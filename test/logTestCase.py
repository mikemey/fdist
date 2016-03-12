import logging
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
