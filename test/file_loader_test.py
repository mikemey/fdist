import json
from SocketServer import TCPServer, BaseRequestHandler
from time import sleep

from mock.mock import MagicMock
from pykka.actor import ActorRef
from pykka.registry import ActorRegistry

from fdist.file_loader import FileLoader
from fdist.messages import *
from fdist.rsync_wrapper import RsyncWrapper
from helpers import free_port
from mock_socket import MockServer
from test.helpers import LogTestCase

TEST_TIMEOUT = 0.5
TEST_WAIT = TEST_TIMEOUT * 2
TEST_FILE = '/dir/file_load_test.txt'

TEST_FILE_LOCATION_MESSAGE = file_location_message(TEST_FILE, 'someone@somewhere:~/dir/file_load_test.txt')


class FileRequestHandler(BaseRequestHandler):
    def handle(self):
        data = self.request.recv(1024).strip()
        self.server.data_records.append(json.loads(data))
        self.request.sendall(json.dumps(TEST_FILE_LOCATION_MESSAGE))


class FileRequestServer(MockServer):
    server_type = TCPServer
    handler_type = FileRequestHandler


def setup_rsync_response_with(ret_val):
    rsync_mock = MagicMock(ref=ActorRef)
    rsync_mock.ask = MagicMock(return_value=ret_val)
    RsyncWrapper.start = MagicMock(return_value=rsync_mock)
    return rsync_mock


class FileLoaderTest(LogTestCase):
    def setUp(self):
        self.remote_fe_port = free_port()
        self.mockedServer = FileRequestServer(self.remote_fe_port)

        self.parentActor = MagicMock(ref=ActorRef)
        self.rsync_start = RsyncWrapper.start

    def tearDown(self):
        RsyncWrapper.start = self.rsync_start
        self.mockedServer.stop()
        ActorRegistry.stop_all()

    def start_file_loader(self):
        file_message = missing_file_message('localhost', self.remote_fe_port, TEST_FILE)
        FileLoader.start(file_message, self.parentActor, TEST_TIMEOUT)
        sleep(TEST_WAIT)

    def test_receive_file_request(self):
        self.start_file_loader()

        received = self.mockedServer.received_data()[0]
        expected = file_request_message(TEST_FILE)
        self.quickEquals(received, expected)

    def test_send_incomplete_message_on_failure(self):
        self.mockedServer.stop()
        self.start_file_loader()

        self.parentActor.tell.assert_called_once_with(load_failed_message(TEST_FILE))

    def test_start_and_stop_rsync(self):
        rsync_mock = setup_rsync_response_with(SUCCESS_MESSAGE)
        self.start_file_loader()

        rsync_mock.ask.assert_called_once_with(TEST_FILE_LOCATION_MESSAGE)
        rsync_mock.stop.assert_called_once()

    def test_send_incomplete_message_on_rsync_failure(self):
        setup_rsync_response_with(FAILURE_MESSAGE)
        self.start_file_loader()

        self.parentActor.tell.assert_called_once_with(load_failed_message(TEST_FILE))
