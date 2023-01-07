from src.models.gpt3 import GPT3Model
from typing import List, Tuple
import json

class TextGenerator:
    """Class for text manipulation and generation using a model"""

    def __init__(self, model: GPT3Model) -> None:
        self.model = model
    
    @staticmethod
    def option_prompt(num_options: int) -> str:
        return f'Generate {num_options} different choices for action in ' +\
            'gamebook style as a json list of strings:'

    def action_to_second_person(self, action: str) -> str:
        instruction="Rewrite this as 'You choose ...'"
        return self.model.edit(action, instruction)

    def generate_actions(self, full_text: str, num_actions=2) -> List[str]:
        if num_actions <= 1:
            prompt = full_text + \
                '\n\nGenerate only 1 choice for action in gamebook style:'
            return [self.model.complete(prompt).strip()]

        prompt = full_text + "\n\n" + self.option_prompt(num_actions)
        generated = self.model.complete(prompt)
        try:
            actions = [item.strip() for item in json.loads(generated)]
        except:
            actions = []
        return actions

    def add_actions(self, full_text: str, existing_actions: List[str], num_new_actions=1) -> List[str]:
        connector = "\n"
        text_and_existing_actions = full_text + \
            f'\n\nYou already have the following choices for action: {connector.join(existing_actions)}'

        if num_new_actions <= 1:
            prompt = text_and_existing_actions + \
                '\n\nAdd another choice for action: '
            return [self.model.complete(prompt).strip()]

        prompt = text_and_existing_actions + \
            f'\n\nAdd {num_new_actions} more choice for action as a json list of string: '
        generated = self.model.complete(prompt)
        try:
            actions = [item.strip() for item in json.loads(generated)]
        except:
            actions = []
        return actions

    def generate_narrative(self, 
        full_text: str, 
        is_ending: bool=False,
        descriptor: str=None,
        details: str=None,
        style: str=None
    ) -> str:
        prompt = full_text

        if descriptor is not None:
            prompt += f"\n\nGenerate a {descriptor} {'ending' if is_ending else 'continuation'}."
        elif is_ending:
            prompt += "\n\nGenerate an ending."

        if details is not None:
            prompt += f"\n\nImportant details: {details}"
        if style is not None:
            prompt += f"\n\nWriting style: {style}"

        prompt += "\n\nResult: "

        response = self.model.complete(prompt)

        if is_ending:
            response += " The end."

        return response

    def summarise(self, content: str) -> str:
        instruction = "Summarize the story in 2nd person:"
        prompt = f"{content}\n\n{instruction}"
        return self.model.complete(prompt)

    def bridge_content(self, from_: str, to: str) -> str:
        return self.model.insert(f"{from_}\n\n", f"\n\n{to}")

    def new_story(self, initial_values: List[Tuple[str, str]]) -> str:
        description = "; ".join([f"{attribute}: \"{content}\"" for
                (attribute, content) in initial_values])
        prompt = f"Write an adventure story with {description} in second person:"
        return self.model.complete(prompt)
