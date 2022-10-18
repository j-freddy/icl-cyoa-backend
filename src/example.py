from backend.src.models.gpt3 import GPT3Model
from backend.src.text_generator import GamebookTextGenerator
from backend.src.tree import GamebookNodeData, GamebookTree

model = GPT3Model()
generator = GamebookTextGenerator(model)
paragraph = "You are a commoner living in the large kingdom of Garion. Your kingdom has been in bitter war with the neighboring kingdom, Liore, for the past year. You dream of doing something great and going on an adventure. You walk around town and see warning posters about the dangers of the dark forest at the edge of town. You go to the market and see military representatives signing people up for the army."
tree = GamebookTree.from_nodes_dict_list([{'nodeId': 0, 'action': None, 'paragraph': 'You are a commoner living in the large kingdom of Garion. Your kingdom has been in bitter war with the neighboring kingdom, Liore, for the past year. You dream of doing something great and going on an adventure. You walk around town and see warning posters about the dangers of the dark forest at the edge of town. You go to the market and see military representatives signing people up for the army.', 'parentId': None, 'childrenIds': []}])
generator.expand_graph_once(tree, 0)

print(tree.to_nodes_dict_list())