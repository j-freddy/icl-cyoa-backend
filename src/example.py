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
                "data": "Write a dystopian story from a second person's perspective.",
                "isEnding": False
            }
        ],
        "actions": [
        ]
    
    }
)
print(tree.to_graph_dict())
generator.expand_graph_once(tree, 0, start_genre=True)
print(tree.to_graph_dict())

#graph = generator.generate_start_from_genre("Write a dystopian story from a second person's perspective.")
#print(graph.to_graph_dict())
