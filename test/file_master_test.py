import tempfile
from time import sleep

from mock.mock import MagicMock
from pykka.registry import ActorRegistry

from fdist.file_master import FileMaster
from fdist.messages import load_failed_message
from fdist.messages import missing_file_message
from test.helpers import LogTestCase

TEST_WAIT = 0.5
TEST_FILE = '/test.txt'
MISSING_MESSAGE = missing_file_message('333.333.333.333', 999999, TEST_FILE)


class FileMasterTest(LogTestCase):
    def setUp(self):
        self.create_file_loader = MagicMock()
        self.file_master = FileMaster.start(self.create_file_loader)

    def tearDown(self):
        ActorRegistry.stop_all()

    def test_only_one_file_loader_created(self):
        self.file_master.tell(MISSING_MESSAGE)
        self.file_master.tell(MISSING_MESSAGE)
        sleep(TEST_WAIT)

        self.create_file_loader.assert_called_once_with(MISSING_MESSAGE, self.file_master)

    def test_restart_file_loader_when_error(self):
        self.file_master.tell(MISSING_MESSAGE)
        sleep(TEST_WAIT)
        self.create_file_loader.assert_called_with(MISSING_MESSAGE, self.file_master)

        self.file_master.tell(load_failed_message(TEST_FILE))
        sleep(TEST_WAIT)
        self.create_file_loader.assert_called_with(MISSING_MESSAGE, self.file_master)
