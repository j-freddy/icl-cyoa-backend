"""Module for the gamebook generator.
"""

import math
import random
from typing import List

from src.analyser import is_duplicate
from src.text_generator import TextGenerator
from src.graph import GamebookGraph, NarrativeNodeData, ActionNodeData


class GenerationProgressFeedback:
    def send_generation_update(
        self,
        num_nodes_generated: int,
        percentage: float,
    ):
        pass


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
    ) -> int:

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

        return graph.make_narrative_node(
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

        actions_ids = []

        generated_actions = self.text_generator.generate_actions(previous_text, num_actions)
        for generated_action in generated_actions:
            actions_ids.append(graph.make_action_node(parent_id=from_node_id, action=generated_action))
        
        return actions_ids

    
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


    def generate_many(
        self,
        graph: GamebookGraph,
        from_node_id: int,
        max_depth: int,
        progress_feedback: GenerationProgressFeedback,
        ending_chance_per_node: float=0.25
    ):
        # Add a narrative node if current node is an action node
        if not graph.is_narrative(from_node_id):
            from_node_id = self.generate_narrative_from_action(
                graph,
                from_node_id
            )

        # Current node is always now narrative node
        assert graph.is_narrative(from_node_id)

        def find_exp_num_nodes(depth):
            if depth == 0:
                return 0

            val_if_end = 1
            val_if_no_end = 2+find_exp_num_nodes(depth-1)

            return ending_chance_per_node*val_if_end + 2*(1-ending_chance_per_node)*val_if_no_end

        exp_num_nodes = 1+find_exp_num_nodes(max_depth)

        num_nodes_generated = [0]

        curr_ids = [from_node_id]

        def update_progress():
            # Update progress
            percentage = min(100, 100 * num_nodes_generated[0] / exp_num_nodes)
            progress_feedback.send_generation_update(graph, num_nodes_generated[0], percentage)

        # Repeat @max_depth times
        for i in range(max_depth):
            new_ids = []

            # Generate continuation per narrative node in current depth
            for curr_id in curr_ids:
                # Do not generate continuation on ending
                last_paragraph_text = graph.get_data(curr_id)
                story_ended = self.text_generator.has_story_ended(last_paragraph_text)

                if graph.is_ending(curr_id) or story_ended:
                    continue

                # TODO: use the is_duplicate from analyser.py to check if the duplication has occurred and end
                # Generate actions per narrative node
                actions_ids = self.generate_actions_from_narrative(
                    graph,
                    curr_id
                )
                num_nodes_generated[0] += len(actions_ids)
                update_progress()

                # Generate narrative node per generated action
                for action_id in actions_ids:
                    actions = graph.get_actions_list(action_id)
                    duplicates = [is_duplicate(x, y) for x in actions for y in actions if x != y]
                    if any(duplicates):
                        node_id = self.generate_narrative_from_action(
                            graph,
                            action_id,
                            is_ending=True
                        )
                        continue
                    to_end = random.random() < ending_chance_per_node

                    node_id = self.generate_narrative_from_action(
                        graph,
                        action_id,
                        is_ending=to_end
                    )
                    num_nodes_generated[0] += 1
                    new_ids.append(node_id)
                    update_progress()
            
            # Next batch of narrative nodes
            curr_ids = new_ids

        return graph
