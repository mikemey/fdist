from time import sleep

from pykka.registry import ActorRegistry

from fdist.announcer import Announcer
from fdist.messages import broadcast_message, local_files_message
from helpers import free_port
from test.helpers import LogTestCase
from test.mock_socket import MockUDPServer

BC_INTERVAL_SEC = 0.3

TEST_WAIT = BC_INTERVAL_SEC * 2

TEST_IP = 'some-ip'
TEST_PORT = 14000
TEST_FILES = ["/file_a.txt", "/file_b.txt"]


class AnnouncerTest(LogTestCase):
    def setUp(self):
        broadcast_port = free_port()
        self.mockedSocket = MockUDPServer(broadcast_port)
        self.announcer = Announcer.start(TEST_PORT, broadcast_port, BC_INTERVAL_SEC)

    def tearDown(self):
        ActorRegistry.stop_all()
        self.mockedSocket.stop()

    def test_received_broadcast(self):
        sleep(TEST_WAIT)
        received = self.mockedSocket.received_data()

        expected = broadcast_message(TEST_PORT, [])
        self.assertTrue(expected in received, received)

    def test_broadcast_with_updated_files(self):
        files = ["/ann_file_1.txt", "/ann_file_2.txt"]
        self.announcer.tell(local_files_message(files))

        sleep(TEST_WAIT)
        received = self.mockedSocket.received_data()
        expected = broadcast_message(TEST_PORT, files)
        self.assertTrue(expected in received,
                        "\n expected: [%s]"
                        "\n received: [%s]" % (expected, received))
