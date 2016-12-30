import tempfile
from time import sleep

from mock.mock import MagicMock

from file_loader import ActorProvider
from file_master import FileMaster
from messages import missing_file_message
from test.helpers import LogTestCase

TEST_IP = '333.333.333.333'
TEST_PORT = 999999
TEST_WAIT = 0.5


class TestFileMaster(LogTestCase):
    def setUp(self):
        self.tmpdir = tempfile.mkdtemp()
        self.provider_mock = MagicMock(spec=ActorProvider)
        self.file_master = FileMaster.start(self.provider_mock)

    def tearDown(self):
        self.file_master.stop()

    def test_only_one_file_loader_created(self):
        message = missing_file_message(TEST_IP, TEST_PORT, 'test.txt')
        self.file_master.tell(message)
        self.file_master.tell(message)
        sleep(TEST_WAIT)

        self.provider_mock.create_file_loader.assert_called_once()
