from src.models.gpt3 import GPT3Model
from src.text_generator import TextGenerator
from src.gamebook_generator import GamebookGenerator
from src.graph import GamebookGraph

generator = GamebookGenerator(TextGenerator(GPT3Model()))
paragraph = "You are a commoner living in the large kingdom of Garion. Your kingdom has been in bitter war with the neighboring kingdom, Liore, for the past year. You dream of doing something great and going on an adventure. You walk around town and see warning posters about the dangers of the dark forest at the edge of town. You go to the market and see military representatives signing people up for the army."
tree = GamebookGraph.from_graph_dict(
    {
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
)
print(tree.to_graph_dict())
generator.bridge_node(tree, 1, 2)
print(tree.to_graph_dict())
