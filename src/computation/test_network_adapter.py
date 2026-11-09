import unittest

from network_adapter import prepare_network


class NetworkAdapterTests(unittest.TestCase):
    def test_converts_cytoscape_graph_to_state_string(self):
        result = prepare_network({
            "nodes": [
                {"data": {"id": "n1", "device_type": "Router", "label": "Gateway"}},
                {"data": {"id": "n2", "device_type": "Server", "label": "App"}},
            ],
            "edges": [{
                "data": {
                    "id": "e1", "source": "n1", "target": "n2",
                    "cost": 2, "bandwidth": 100, "connection_type": "TCP", "source_port": 443,
                }
            }],
        })

        self.assertEqual(result["topology"]["nodes"][0]["device_ip"], "10.0.0.1")
        self.assertIn("Router,[10,0,0,1]", result["state_string"])
        self.assertIn("([10,0,0,2],2,100,TCP,443)", result["state_string"])

    def test_rejects_unknown_edge_node(self):
        with self.assertRaisesRegex(ValueError, "unknown node"):
            prepare_network({
                "nodes": [{"id": "n1", "device_type": "PC"}],
                "edges": [{"source": "n1", "target": "missing"}],
            })


if __name__ == "__main__":
    unittest.main()
