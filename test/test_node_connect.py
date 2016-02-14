from time import sleep

from fdist import shutdown_sig, version_update
from node_connect import NodeConnect
from test import LogTestCase


class TestNodeConnect(LogTestCase):
    def tearDown(self):
        shutdown_sig.send(self.__class__)

    def test_set_version(self):
        NodeConnect(6000)
        version_update.send(self.__class__, version=3)

        sleep(3)

    def test_find_nodes(self):
        node1 = NodeConnect(6001)

        sleep(1)
        node2 = NodeConnect(6002)

        sleep(1)
        # node3 = self.create_node(6003)
        #
        sleep(3)
        self.assertIn("localhost:6002", node1.remote_ips())
        self.assertIn("localhost:6003", node1.remote_ips())
        #
        # self.assertIn("localhost:6001", node2.remote_ips())
        # self.assertIn("localhost:6003", node2.remote_ips())
        #
        # self.assertIn("localhost:6001", node3.remote_ips())
        # self.assertIn("localhost:6002", node3.remote_ips())
