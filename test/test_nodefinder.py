import socket
from time import sleep

from mock import MagicMock
from pykka import ActorRef

from fdist.nodefinder import Announcer, NodeFinder
from test.logTestCase import LogTestCase
from test.mock_socket import MockUDPServer

BC_INTERVAL_SEC = 0.3

TEST_WAIT = BC_INTERVAL_SEC * 2


class TestAnnouncer(LogTestCase):
    def setUp(self):
        self.remote_bc_port = 15000
        self.mockedSocket = MockUDPServer(self.remote_bc_port)

        self.local_node = ('some-ip', 14000)
        self.announcer = Announcer.start(self.local_node, self.remote_bc_port, BC_INTERVAL_SEC)

    def tearDown(self):
        self.announcer.stop()
        self.mockedSocket.stop()

    def test_received_broadcast(self):
        sleep(TEST_WAIT)
        received = self.mockedSocket.received()

        expected = {"node": "{0}:{1}".format(self.local_node[0], self.local_node[1])}
        self.assertTrue(expected in received, received)


class TestNodeFinder(LogTestCase):
    def setUp(self):
        self.broadcast_port = 15422
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_BROADCAST, 1)
        self.socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        self.receiver = MagicMock(spec=ActorRef)
        self.node_finder = NodeFinder.start(self.receiver, self.broadcast_port)

    def send_broadcast(self, message):
        self.socket.sendto(message, ('<broadcast>', self.broadcast_port))

    def test_forwards_new_node(self):
        self.send_broadcast("""{"node": "some-ip:12121" }""")
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_with({'nodes': [("some-ip", 12121)]})

    def test_forwards_two_new_node(self):
        self.send_broadcast("""{"node": "some-ip:12121" }""")
        self.send_broadcast("""{"node": "some-ip:32323" }""")
        sleep(TEST_WAIT)

        self.receiver.tell.assert_called_with({'nodes': [("some-ip", 12121), ("some-ip", 32323)]})
