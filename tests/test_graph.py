import unittest
from unittest import TestCase

from src.graph import GamebookGraph

class GamebookGraphTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.example_action = "Action"
        cls.example_narrative = "Narrative"
        cls.example_node_data = {
            "narratives": [
                {
                    "nodeId": 0,
                    "data": "N0",
                    "childrenIds": [1, 2],
                    "isEnding": False
                },
                {
                    "nodeId": 3,
                    "data": "N3",
                    "childrenIds": [],
                    "isEnding": True
                },
                {
                    "nodeId": 4,
                    "data": "N4",
                    "childrenIds": [],
                    "isEnding": False
                }
            ],
            "actions": [
                {
                    "nodeId": 1,
                    "data": "A1",
                    "childrenIds": [3]
                },
                {
                    "nodeId": 2,
                    "data": "A2",
                    "childrenIds": [4]
                }
            ]
        }
    
    def setUp(self) -> None:
        self.gamebook_graph = GamebookGraph.from_graph_dict(self.example_node_data)

    def test_parent_ids_are_correctly_set(self):
        self.assertEqual(1, self.gamebook_graph.parent_lookup[3][0])

    def test_graph_can_serialize_from_and_to_dict(self):
        self.assertEqual(
            GamebookGraph.from_graph_dict(self.example_node_data).to_graph_dict(),
            self.example_node_data
        )
    
    def test_make_action_node(self):
        parent_id = 0
        node_id = self.gamebook_graph.make_action_node(0, self.example_action)
        self.assertEqual(5, node_id)
        node = self.gamebook_graph.node_lookup[node_id]
        self.assertEqual(self.example_action, node.data)
        self.assertEqual([], node.children_ids)
        self.assertEqual([1, 2, 5], self.gamebook_graph.node_lookup[parent_id].children_ids)
        self.assertEqual([parent_id], self.gamebook_graph.parent_lookup[node_id])
    
    def test_make_narrative_node(self):
        parent_id = 1
        node_id = self.gamebook_graph.make_narrative_node(parent_id, self.example_narrative)
        self.assertEqual(5, node_id)
        node = self.gamebook_graph.node_lookup[node_id]
        self.assertEqual(self.example_narrative, node.data)
        self.assertEqual([], node.children_ids)
        self.assertEqual([parent_id], self.gamebook_graph.parent_lookup[node_id])
        self.assertEqual([3, 5], self.gamebook_graph.node_lookup[parent_id].children_ids)
        self.assertFalse(node.is_ending)

    def test_make_narrative_node_with_is_ending(self):
        parent_id = 1
        node_id = self.gamebook_graph.make_narrative_node(parent_id, self.example_narrative, is_ending=True)
        self.assertEqual(5, node_id)
        node = self.gamebook_graph.node_lookup[node_id]
        self.assertEqual(self.example_narrative, node.data)
        self.assertEqual([], node.children_ids)
        self.assertEqual([parent_id], self.gamebook_graph.parent_lookup[node_id])
        self.assertEqual([3, 5], self.gamebook_graph.node_lookup[parent_id].children_ids)
        self.assertTrue(node.is_ending)

    def test_set_ending_narrative(self):
        self.gamebook_graph.set_ending_narrative(4, is_ending=True)
        self.assertTrue(self.gamebook_graph.node_lookup[4].is_ending)

    def test_is_narrative(self):
        self.assertFalse(self.gamebook_graph.is_narrative(2))
        self.assertTrue(self.gamebook_graph.is_narrative(4))

    def test_set_data(self):
        self.gamebook_graph.set_data(3, self.example_narrative)
        self.assertEqual(self.example_narrative, self.gamebook_graph.node_lookup[3].data)

    def test_get_data(self):
        self.assertEqual("N0", self.gamebook_graph.get_data(0))
        self.assertEqual("A1", self.gamebook_graph.get_data(1))

    def test_connect_nodes(self):
        self.gamebook_graph.connect_nodes(3, 4)
        self.assertEqual([4], self.gamebook_graph.node_lookup[3].children_ids)
        self.assertEqual([2, 3], self.gamebook_graph.parent_lookup[4])

    def test_get_paragraph_list(self):
        expected = ["N0", "N3"]
        self.assertEqual(expected, self.gamebook_graph.get_paragraph_list(3))


if __name__ == "__main__":
    unittest.main()
