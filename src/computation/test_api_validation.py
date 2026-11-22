import unittest

from app import app


class ApiValidationTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_prepare_rejects_unknown_edge_node_with_actionable_error(self):
        response = self.client.post("/simulation/prepare", json={
            "topology": {
                "nodes": [{"id": "router-1", "device_type": "Router"}],
                "edges": [{"id": "edge-1", "source": "router-1", "target": "missing"}],
            }
        })

        self.assertEqual(response.status_code, 400)
        body = response.get_json()
        self.assertFalse(body["ok"])
        self.assertIn("unknown node", body["error"])

    def test_prepare_rejects_unsupported_device_type(self):
        response = self.client.post("/simulation/prepare", json={
            "topology": {"nodes": [{"id": "n1", "device_type": "Firewall"}], "edges": []}
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("unsupported device_type", response.get_json()["error"])

    def test_prepare_rejects_duplicate_node_id(self):
        response = self.client.post("/simulation/prepare", json={
            "topology": {
                "nodes": [
                    {"id": "n1", "device_type": "Router"},
                    {"id": "n1", "device_type": "Server"},
                ],
                "edges": [],
            }
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("duplicate node id", response.get_json()["error"])

    def test_prepare_rejects_unsupported_connection_type(self):
        response = self.client.post("/simulation/prepare", json={
            "topology": {
                "nodes": [
                    {"id": "n1", "device_type": "Router"},
                    {"id": "n2", "device_type": "Server"},
                ],
                "edges": [{
                    "id": "edge-1",
                    "source": "n1",
                    "target": "n2",
                    "connection_type": "ICMP",
                }],
            }
        })

        self.assertEqual(response.status_code, 400)
        self.assertIn("unsupported connection_type", response.get_json()["error"])

    def test_prepare_accepts_valid_network(self):
        response = self.client.post("/simulation/prepare", json={
            "topology": {
                "nodes": [{"id": "n1", "device_type": "Router"}],
                "edges": [],
            }
        })

        self.assertEqual(response.status_code, 200)
        body = response.get_json()
        self.assertTrue(body["ok"])
        self.assertIn("state_string", body)


if __name__ == "__main__":
    unittest.main()
