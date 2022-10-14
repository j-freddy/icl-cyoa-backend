from backend.src.models.gpt3 import GPT3Model
from backend.src.text_generator import GamebookTextGenerator

model = GPT3Model()
generator = GamebookTextGenerator(model)
paragraph = "You are a commoner living in the large kingdom of Garion. Your kingdom has been in bitter war with the neighboring kingdom, Liore, for the past year. You dream of doing something great and going on an adventure. You walk around town and see warning posters about the dangers of the dark forest at the edge of town. You go to the market and see military representatives signing people up for the army."
print(generator._generate_actions(paragraph))
