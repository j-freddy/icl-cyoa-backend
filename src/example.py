from src.models.gpt3 import GPT3Model
from src.text_generator import TextGenerator
from src.gamebook_generator import GamebookGenerator, GenerationProgressFeedback


def main():
    generator = GamebookGenerator(TextGenerator(GPT3Model()))
    genre_prompt = "Write the beginning of a dystopian story from a second person perspective."

    progress_feedback = GenerationProgressFeedback()

    graph = generator.generate_start_from_genre(genre_prompt)
    generator.generate_many(graph, 1, 2, progress_feedback, ending_chance_per_node=0.25, debug=True)

    for i in range(0, 100):
        print("============================================================")
        print(i)
        try:
            print(graph.get_data(i))
        except KeyError:
            print("===============ending reached======================")
            break


if __name__ == '__main__':
    main()
