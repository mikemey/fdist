from time import sleep

from node_connect import NodeConnect
from signals import SYSTEM_SHUTDOWN, PEER_UPDATE
from test import LogTestCase


class TestNodeConnect(LogTestCase):
    def tearDown(self):
        SYSTEM_SHUTDOWN.send(self)
        sleep(2)

    def test_find_nodes(self):
        NodeConnect(6500, 6600)
        sleep(0.5)
        NodeConnect(6501, 6601)

        PEER_UPDATE.connect(update_callback)


def update_callback(sender, **kwargs):
    print 'received:', str(kwargs['peers'])

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
