import socket
from time import sleep

from node_connect import NodeConnect
from signals import SYSTEM_SHUTDOWN, PEER_UPDATE
from test import LogTestCase


def local_ip():
    return str(socket.gethostbyname(socket.gethostname()))


class TestNodeConnect(LogTestCase):
    def tearDown(self):
        SYSTEM_SHUTDOWN.send(self)
        sleep(2)

    def test_find_nodes(self):
        NodeConnect(6500, 6600)
        sleep(0.5)
        NodeConnect(6501, 6601)

        collector = PeerCollector()
        PEER_UPDATE.connect(collector.matches_nodes)
        sleep(3)

        self.assertTrue(collector.has_node(local_ip() + '-6600'))
        self.assertTrue(collector.has_node(local_ip() + '-6601'))


class PeerCollector:
    def __init__(self):
        pass

    def matches_nodes(self, sender, **kwargs):
        print 'TEST received:', str(kwargs['peers'])

    def has_node(self, node):
        print node
        return False

#
# sleep(1)
# # node3 = self.create_node(6003)
# #
# sleep(3)
# self.assertIn("localhost:6002", node1.remote_ips())
# self.assertIn("localhost:6003", node1.remote_ips())
#
# self.assertIn("localhost:6001", node2.remote_ips())
# self.assertIn("localhost:6003", node2.remote_ips())
#
# self.assertIn("localhost:6001", node3.remote_ips())
# self.assertIn("localhost:6002", node3.remote_ips())
