import unittest

from src.tree import GamebookNodeData
from src.tree import GamebookTree

example_node_data = [
    {
        "nodeId": 0,
        "action": None,
        "paragraph": "Paragraph 0 ",
        "parentId": None,
        "childrenIds": [1, 2],
    },
    {
        "nodeId": 1,
        "action": "Action 1 ",
        "paragraph": "Paragraph 1 ",
        "parentId": 0,
        "childrenIds": [],
    },
    {
        "nodeId": 2,
        "action": "Action 2 ",
        "paragraph": "Paragraph 2 ",
        "parentId": 0,
        "childrenIds": [3, 4],
    },
    {
        "nodeId": 3,
        "action": "Action 3 ",
        "paragraph": "Paragraph 3 ",
        "parentId": 2,
        "childrenIds": [],
    },
    {
        "nodeId": 4,
        "action": "Action 4 ",
        "paragraph": "Paragraph 4 ",
        "parentId": 2,
        "childrenIds": [],
    },
]


class GamebookTreeTest(unittest.TestCase):
    def test_node_can_serialise_from_camelcase_and_snakecase(self):
        node = GamebookNodeData.from_dict(
            {
                "node_id": 1,
                "action": "Action!",
                "paragraph": "Paragraph!",
                "parentId": 0,
                "childrenIds": [2, 3, 4],
            },
        )

        self.assertEqual(node.node_id, 1)
        self.assertEqual(node.action, "Action!")
        self.assertEqual(node.paragraph, "Paragraph!")
        self.assertEqual(node.parent_id, 0)
        self.assertEqual(node.children_ids, [2, 3, 4])

    def test_tree_can_serialize_from_and_to_dict(self):
        self.assertEqual(
            GamebookTree.from_nodes_dict_list(example_node_data).to_nodes_dict_list(),
            example_node_data,
        )


if __name__ == "__main__":
    unittest.main()
