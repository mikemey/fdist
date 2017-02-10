from fdist.globals import md5_hash, hashed_file_path
from test.helpers import LogTestCase


class GlobalsTest(LogTestCase):
    def test_md5_hash(self):
        self.quickEquals(md5_hash("ABC"), "902fbdd2b1df0c4f70b4a5d23525e932")
        self.quickEquals(md5_hash("ABC", 4), "902f")

    def test_hashed_file(self):
        self.quickEquals(hashed_file_path("/abc", "/bla_bla.tmp"),
                         "/abc/.bla_bla.tmp.6ee938")
        self.quickEquals(hashed_file_path("/abc", "/def/bla_bla.tmp"),
                         "/abc/def/.bla_bla.tmp.184717")
