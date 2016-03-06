import logging
import sys
from unittest import TestCase

logging.basicConfig(level=logging.DEBUG,
                    format='%(asctime)s %(levelname)s [%(name)-5s] %(message)s',
                    stream=sys.stdout
                    )


class LogTestCase(TestCase):
    def setUp(self):
        test_class = self.__class__.__name__
        test_method = self._testMethodName
        print("--------------\nTest run: [{} - {}]".format(test_class, test_method))

    def quickEquals(self, actual, expected):
        self.assertEquals(actual, expected,
                          "Error:\n\tactual  : [{}]\n\texpected: [{}]".format(actual, expected))
