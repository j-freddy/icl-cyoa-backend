from src.models.gpt3 import GPT3Model
from typing import List

class TextGenerator:
    """Class for text manipulation and generation using a model"""

    def __init__(self, model: GPT3Model) -> None:
        self.model = model
    
    @staticmethod
    def option_prompt(num_options: int) -> str:
        return f"You have {num_options} options:"

    def action_to_second_person(self, action: str) -> str:
        instruction="Rewrite this as 'You choose ...'"
        return self.model.edit(action, instruction)

    def generate_actions(self, full_text: str, num_options=2) -> List[str]:
        prompt = full_text + " " + self.option_prompt(num_options)
        generated = self.model.complete(prompt)
        # Extract only the actions.
        actions = []
        count = 0
        for line in generated.splitlines():
            line = line.strip()
            first_alpha = next(filter(str.isalpha, line), None)
            # Ignore non-alphabetical content at the front
            if first_alpha is not None:
                line = line[line.find(first_alpha):]
                if line[-1] != ".":
                    line += "."
                actions.append(line)
                count += 1
            if count >= num_options:
                return actions
        return actions

    def generate_paragraph(self, full_text: str) -> str:
        prompt = full_text
        return self.model.complete(prompt)

    def summarise(self, content: str) -> str:
        instruction = "Summarize the story in 2nd person:"
        prompt = f"{content}\n\n{instruction}"
        return self.model.complete(prompt)

    def bridge_content(self, from_: str, to: str) -> str:
        return self.model.insert(f"{from_}\n\n", f"\n\n{to}")
