from time import sleep

from fdist.files_diff import FilesDiff
from fdist.messages import local_files_message, remote_files_message, missing_file_message
from test.logTestCase import LogTestCase
from test.mock_socket import MockTCPServer

TEST_RELOAD_LOCAL_FILES_SEC = 0.2
TEST_WAIT = TEST_RELOAD_LOCAL_FILES_SEC * 2

TEST_REMOTE_HOST = 'localhost'
TEST_REMOTE_PORT = 15000


class TestFileUpdater(LogTestCase):
    def setUp(self):
        self.fileUpdater = FilesDiff.start()
        self.mockedSocket = MockTCPServer((TEST_REMOTE_HOST, TEST_REMOTE_PORT))

    def tearDown(self):
        self.mockedSocket.stop()

    def test_update_node(self):
        files = ["lala.txt"]
        self.fileUpdater.tell(local_files_message(["lulu.txt"]))
        self.fileUpdater.tell(remote_files_message(TEST_REMOTE_HOST, TEST_REMOTE_PORT, files))

        sleep(TEST_WAIT)
        self.assertTrue(
            missing_file_message(TEST_REMOTE_HOST, TEST_REMOTE_PORT, "lala.txt") in self.mockedSocket.received(),
            self.mockedSocket.received()
        )
