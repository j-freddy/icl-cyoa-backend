from typing import List
from backend.src.tree import GamebookTree
from backend.src.models.gpt3 import GPT3Model

class GamebookTextGenerator:
    """Class for modifying gamebook tree, and generating new text using a model"""

    def __init__(self, model: GPT3Model) -> None:
        self.model = model

    def _option_prompt(self, num_options: int) -> str:
        return f"You have {num_options} options:"

    def _generate_actions(self, paragraph: str, num_options=2) -> List[str]:
        prompt = paragraph + " " + self._option_prompt(num_options)
        generated = self.model.complete(prompt)
        # Extract only the sentences.
        actions = [line[line.find(next(filter(str.isalpha, line))):] for 
                line in generated.splitlines() if line != ""]
        return actions

    def expand_graph(self, graph: GamebookTree, expand_at_node=0) -> None:
        raise NotImplementedError
