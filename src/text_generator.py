"""Module for the text generator.
"""
from typing import List

from src.models.gpt3 import GPT3Model
from src.tree import GamebookTree


class GamebookTextGenerator:
    """Class for modifying gamebook tree, and generating new text using a model"""

    def __init__(self, model: GPT3Model) -> None:
        self.model = model

    @staticmethod
    def _option_prompt(num_options: int) -> str:
        return f"You have {num_options} options:"

    def _generate_actions(self, full_text: str, num_options=2) -> List[str]:
        prompt = full_text + " " + self._option_prompt(num_options)
        generated = self.model.complete(prompt)
        # Extract only the actions.
        actions = []
        count = 0
        for line in generated.splitlines():
            line = line.strip()
            first_alpha = next(filter(str.isalpha, line), None)
            # Ignore non-alphabetical content at the front
            if first_alpha is not None:
                line = line[line.find(first_alpha) :]
                if line[-1] != ".":
                    line += "."
                actions.append(line)
                count += 1
            if count >= num_options:
                return actions
        return actions

    def _generate_paragraph(self, full_text: str) -> str:
        prompt = full_text
        return self.model.complete(prompt)

    def _action_to_second_person(self, action: str) -> str:
        return self.model.edit(
            text_to_edit=action,
            instruction="Rewrite this as 'You choose ...'",
        )

    @staticmethod
    def _paragraphs_to_prompt(paragraph_list: List[str]) -> str:
        return " ".join(paragraph_list)

    def expand_graph_once(self, tree: GamebookTree, expand_at_node=0) -> None:
        """Expand the graph at the specified node: Generate the paragraph if it
        is missing, and generate the action options for the paragraph otherwise.
        """

        paragraph_list = tree.get_paragraph_list(expand_at_node)
        end_action = tree.get_action(expand_at_node)
        end_paragraph = tree.get_paragraph(expand_at_node)

        previous_text = self._paragraphs_to_prompt(paragraph_list)

        if end_paragraph is None:
            if end_action is None:
                # first node - generate starter paragraph
                raise NotImplementedError

            edited_action = self._action_to_second_person(end_action) + " "

            # then we need to generate paragraph
            generated_paragraph = self._generate_paragraph(
                previous_text + " " + edited_action,
            )
            tree.edit_node(
                expand_at_node,
                paragraph=edited_action + generated_paragraph,
            )
            return

        # else we need to generate new actions given the current text and
        # create new nodes for these actions
        generated_actions = self._generate_actions(previous_text)
        for generated_action in generated_actions:
            tree.make_node(parent_id=expand_at_node, action=generated_action)
