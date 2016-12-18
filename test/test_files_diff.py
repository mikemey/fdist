from time import sleep

from mock.mock import MagicMock
from pykka.actor import ActorRef

from fdist.files_diff import FilesDiff
from fdist.messages import local_files_message, remote_files_message, missing_file_message
from test.helpers import LogTestCase

TEST_REMOTE_IP = '333.333.333.333'
TEST_REMOTE_PORT = 999999

TEST_WAIT = 0.5


class TestFileUpdater(LogTestCase):
    def setUp(self):
        self.receiver = MagicMock(spec=ActorRef)
        self.filesDiff = FilesDiff.start(self.receiver)

    def test_report_missing_file(self):
        files = ["lala.txt", "li_li.txt"]
        self.filesDiff.tell(local_files_message(["lulu.txt"]))
        self.filesDiff.tell(remote_files_message(TEST_REMOTE_IP, TEST_REMOTE_PORT, files))

        sleep(TEST_WAIT)
        self.receiver.tell.assert_any_call(missing_file_message(TEST_REMOTE_IP, TEST_REMOTE_PORT, files[0]))
        self.receiver.tell.assert_any_call(missing_file_message(TEST_REMOTE_IP, TEST_REMOTE_PORT, files[1]))
