""" Module for the tree representation of the gamebook.
"""
from collections import defaultdict
from typing import List, Union
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class NarrativeNodeData:
    """Dataclass which can be converted to and from json-style camelCase using
    to_dict and from_dict"""

    node_id: int

    data: str

    children_ids: List[int] = field(default_factory=list)

    is_ending: bool = False

    type: str = "narrative"
    

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class ActionNodeData:
    """Dataclass which can be converted to and from json-style camelCase using
    to_dict and from_dict"""

    node_id: int

    data: str

    children_ids: List[int] = field(default_factory=list)

    type: str = "action"
    

class GamebookGraph:
    """Class for representing the graph for a gamebook"""

    def __init__(self, node_data_list: List[Union[NarrativeNodeData,  ActionNodeData]]):
        self.node_lookup = {
            node_data.node_id: node_data for node_data in node_data_list
        }

        self.parent_lookup = defaultdict(list)
        for node in node_data_list:
            for child_id in node.children_ids:
                self.parent_lookup[child_id].append(node.node_id)

        self.next_node_id = max(node_data.node_id for node_data in node_data_list) + 1


    @staticmethod
    def from_graph_dict(graph):
        """Deserializes from json-style dictionary to GamebookTree"""
        narrative_nodes = [
            NarrativeNodeData.from_dict(node_data) for node_data in graph["nodes"] if node_data["type"] == "narrative"
        ]
        action_nodes = [
            ActionNodeData.from_dict(
                node_data) for node_data in graph["nodes"] if node_data["type"] == "action"
        ]

        return GamebookGraph(narrative_nodes + action_nodes)

    def to_graph_dict(self):
        """Serializes class data into a json-style dictionary with list of node
        data"""
        return {
            "nodes": [node_data.to_dict() for node_data in self.node_lookup.values()]
        }

    def _get_node(self, node_id):
        return self.node_lookup[node_id]

    def make_action_node(self, parent_id, action) -> int:
        new_node = ActionNodeData(
            node_id=self.next_node_id,
            data=action
        )
        return self._add_node(parent_id, new_node)

    def make_narrative_node(self, parent_id, narrative, is_ending=False) -> int:
        new_node = NarrativeNodeData(
            node_id=self.next_node_id,
            data=narrative,
            is_ending=is_ending
        )
        return self._add_node(parent_id, new_node)

    def _add_node(self, parent_id, new_node) -> int:
        """Allow editing action and paragraph"""
        node_id = self.next_node_id
        self.next_node_id += 1

        self.node_lookup[node_id] = new_node

        parent = self.node_lookup[parent_id]
        parent.children_ids.append(node_id)
        self.parent_lookup[node_id].append(parent_id)
        
        return new_node.node_id
    
    def connect_nodes(self, parent_id: int, child_id: int) -> None:
        parent = self.node_lookup[parent_id]
        parent.children_ids.append(child_id)

        self.parent_lookup[child_id].append(parent_id)

    def set_ending_narrative(self, node_id, is_ending):
        node = self.node_lookup[node_id]
        if self.is_narrative(node_id):
            node.is_ending = is_ending

    def set_data(self, node_id, new_data):
        """Allow editing action and paragraph"""
        self.node_lookup[node_id].data = new_data

    def get_data(self, node_id):
        """Get the data at node with the node_id."""
        return self.node_lookup[node_id].data

    def is_narrative(self, node_id):
        node = self.node_lookup[node_id]
        return node.type == "narrative"

    def is_action(self, node_id):
        node = self.node_lookup[node_id]
        return node.type == "action"

    def is_ending(self, node_id):
        node = self.node_lookup[node_id]

        if node.type != "narrative":
            return False

        return node.is_ending
    
    def get_paragraph_list(self, end_node_id):
        """Generates a list of paragraph from the root node to end node
        inclusively."""
        rev_paragraphs = []

        # here we need to build the text list in reverse, since we need to
        # traverse the tree using the parent_id field
        node_id = end_node_id

        while node_id is not None:
            node = self.node_lookup[node_id]
            if self.is_narrative(node_id) and node.data is not None:
                rev_paragraphs.append(node.data)
            node_id = self.parent_lookup[node_id][0] if self.parent_lookup[node_id] != [] else None

        return list(reversed(rev_paragraphs))

    def get_actions_list(self, end_node_id):
        actions = []

        node_id = end_node_id

        while node_id is not None:
            node = self.node_lookup[node_id]
            if self.is_action(node_id) and node.data is not None:
                actions.append(node.data)
            node_id = self.parent_lookup[node_id][0] if self.parent_lookup[node_id] != [] else None

        return actions
        
    def get_children(self, node_id: int) -> List[int]:
        node = self.node_lookup[node_id]
        return node.children_ids
