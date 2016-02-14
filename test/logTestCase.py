from unittest import TestCase


class LogTestCase(TestCase):
    def setUp(self):
        test_class = self.__class__.__name__
        test_method = self._testMethodName
        print """--------------\nTest run: [%s - %s]""" % (test_class, test_method)

    def quickEquals(self, actual, expected):
        self.assertEquals(actual, expected,
                          "Error:\n\tactual  : [%s]\n\texpected: [%s]" % (actual, expected))
