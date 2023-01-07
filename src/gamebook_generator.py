"""Module for the gamebook generator.
"""

from src.text_generator import TextGenerator
from src.graph import GamebookGraph, NarrativeNodeData


class GamebookGenerator:
    """Class for modifying gamebook graph, and generating new text using a model"""


    def __init__(self, text_generator: TextGenerator) -> None:
        self.text_generator = text_generator


    def _paragraphs_to_prompt(self, paragraph_list: str):
        return " ".join(paragraph_list)


    def generate_narrative_from_action(self, 
        graph: GamebookGraph, 
        from_node_id: int, 
        is_ending: bool=False, 
        descriptor: str=None,
        details: str=None,
        style: str=None
    ) -> None:

        if graph.is_narrative(from_node_id):
            raise TypeError

        paragraph_list = graph.get_paragraph_list(from_node_id)
        previous_text = self._paragraphs_to_prompt(paragraph_list)

        action = graph.get_data(from_node_id)
        edited_action = self.text_generator.action_to_second_person(action) + " "

        prompt = previous_text + " " + edited_action

        generated_narrative = edited_action + self.text_generator.generate_narrative(
            prompt, 
            is_ending=is_ending,
            descriptor=descriptor,
            details=details,
            style=style
        )

        graph.make_narrative_node(
            parent_id=from_node_id, narrative=generated_narrative, is_ending=is_ending)


    def generate_actions_from_narrative(self, 
        graph: GamebookGraph, 
        from_node_id: int, 
        num_actions: int=2
    ) -> None:
        if not graph.is_narrative(from_node_id):
            raise TypeError
        
        paragraph_list = graph.get_paragraph_list(from_node_id)
        previous_text = self._paragraphs_to_prompt(paragraph_list)

        generated_actions = self.text_generator.generate_actions(previous_text, num_actions)
        for generated_action in generated_actions:
            graph.make_action_node(parent_id=from_node_id, action=generated_action)

    
    def add_actions(self, graph: GamebookGraph, from_node_id: int, num_new_actions: int=1) -> None:
        if not graph.is_narrative(from_node_id):
            raise TypeError

        existing_action_node_ids = graph.get_children(from_node_id)

        if len(existing_action_node_ids) == 0:
            self.generate_actions_from_narrative(graph, from_node_id, num_new_actions)
            return

        paragraph_list = graph.get_paragraph_list(from_node_id)
        previous_text = self._paragraphs_to_prompt(paragraph_list)

        existing_actions = [graph.get_data(node_id) for
            node_id in existing_action_node_ids]
        
        new_actions = self.text_generator.add_actions(previous_text, 
            existing_actions, num_new_actions)

        for action in new_actions:

            graph.make_action_node(parent_id=from_node_id, action=action)


    def bridge_node(self, graph: GamebookGraph, from_node_id: int, to_node_id: int) -> None:
        from_ = graph.get_data(from_node_id)
        to = graph.get_data(to_node_id)

        bridge = self.text_generator.bridge_content(from_, to)
        bridge_node_id = graph.make_narrative_node(parent_id=from_node_id, narrative=bridge)
        
        graph.connect_nodes(bridge_node_id, to_node_id)
    

    def generate_initial_story(self, initial_story_prompt) -> GamebookGraph:
        initial_values = [(elem["attribute"], elem["content"]) for elem in initial_story_prompt]
        generated_narrative = self.text_generator.new_story(initial_values)

        root = NarrativeNodeData(
            node_id= 0,
            data= generated_narrative,
            is_ending= False
        )
        graph = GamebookGraph([root])

        self.generate_actions_from_narrative(graph, 0)

        return graph
