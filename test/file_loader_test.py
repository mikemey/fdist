from time import sleep

from fdist.file_loader import FileLoader
from fdist.messages import missing_file_message, file_request_message
from helpers import free_port
from mock_socket import MockTCPServer
from test.helpers import LogTestCase

TEST_WAIT = 1
TEST_FILE = "file_load_test.txt"


class TestFileLoader(LogTestCase):
    def setUp(self):
        remote_fe_port = free_port()
        self.mockedServer = MockTCPServer(remote_fe_port)
        file_message = missing_file_message('localhost', remote_fe_port, TEST_FILE)
        self.file_loader = FileLoader.start(file_message)

    def tearDown(self):
        self.file_loader.stop()
        self.mockedServer.stop()

    def test_receive_file_request(self):
        sleep(TEST_WAIT)
        received = self.mockedServer.received_data()[0]

        expected = file_request_message(TEST_FILE)
        self.quickEquals(received, expected)
