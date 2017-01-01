import json
from SocketServer import TCPServer, BaseRequestHandler
from time import sleep

from mock.mock import MagicMock
from pykka.actor import ActorRef

from fdist.file_loader import FileLoader
from fdist.messages import missing_file_message, file_request_message, load_failed_message
from helpers import free_port
from mock_socket import MockServer
from test.helpers import LogTestCase

TEST_WAIT = 1
TEST_FILE = "/file_load_test.txt"


class FileRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.data_records.append(json.loads(data))


class FileRequestServer(MockServer):
    server_type = TCPServer
    handler_type = FileRequestHandler


class TestFileLoader(LogTestCase):
    def setUp(self):
        remote_fe_port = free_port()
        self.mockedServer = FileRequestServer(remote_fe_port)
        file_message = missing_file_message('localhost', remote_fe_port, TEST_FILE)

        self.parentActor = MagicMock(ref=ActorRef)
        self.file_loader = FileLoader.start(file_message, self.parentActor)

    def tearDown(self):
        self.file_loader.stop()
        self.mockedServer.stop()

    def test_receive_file_request(self):
        sleep(TEST_WAIT)
        received = self.mockedServer.received_data()[0]

        expected = file_request_message(TEST_FILE)
        self.quickEquals(received, expected)
    #
    # def test_send_incomplete_message_on_failure(self):
    #     self.mockedServer.stop()
    #     sleep(2)
    #
    #     self.parentActor.assert_called_once_with(load_failed_message(TEST_FILE))

    # def test_issue_rsync_request(self):
    #     self.fail('not yet implemented')
