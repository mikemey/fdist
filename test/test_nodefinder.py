from time import sleep

from fdist.nodefinder import Announcer
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
        sleep(BC_INTERVAL_SEC * 2)
        received = self.mockedSocket.received()

        expected = {"node": '{0}:{1}'.format(self.local_node[0], self.local_node[1])}
        self.assertTrue(expected in received, received)
