import json
import socket
from time import sleep

from mock import MagicMock
from pykka import ActorRef

from fdist.messages import broadcast_message, remote_files_message
from fdist.remote_files import RemoteFileSystem
from helpers import free_port
from test.helpers import LogTestCase

BC_INTERVAL_SEC = 0.3

TEST_WAIT = BC_INTERVAL_SEC * 2

TEST_IP = socket.gethostbyname(socket.gethostname())
TEST_PORT = 12121
TEST_FILES = ["file_a.txt", "file_b.txt"]


class TestRemoteFileSystem(LogTestCase):
    def setUp(self):
        self.broadcast_port = free_port()

        self.receiver = MagicMock(spec=ActorRef)
        self.remote_files = RemoteFileSystem(self.receiver, self.broadcast_port)

    def tearDown(self):
        self.remote_files.stop()

    def send_broadcast(self, message):
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.socket.sendto(json.dumps(message), ('<broadcast>', self.broadcast_port))
        self.socket.close()

    def test_forwards_new_node(self):
        self.send_broadcast(broadcast_message(TEST_PORT, TEST_FILES))
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_with(remote_files_message(TEST_IP, TEST_PORT, TEST_FILES))

    def test_forwards_two_new_nodes(self):
        test_port_2 = 32323
        test_files_2 = ["2_file_a.txt", "2_file_b.txt"]

        self.send_broadcast(broadcast_message(TEST_PORT, TEST_FILES))
        self.send_broadcast(broadcast_message(test_port_2, test_files_2))
        sleep(TEST_WAIT)

        self.receiver.tell.assert_any_call(remote_files_message(TEST_IP, TEST_PORT, TEST_FILES))
        self.receiver.tell.assert_any_call(remote_files_message(TEST_IP, test_port_2, test_files_2))
