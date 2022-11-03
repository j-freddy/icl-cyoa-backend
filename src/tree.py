""" Module for the tree representation of the gamebook.
"""
from typing import List, Optional
from dataclasses import dataclass, field

from dataclasses_json import dataclass_json, LetterCase


@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GamebookNodeData:
    """Dataclass which can be converted to and from json-style camelCase using
    to_dict and from_dict"""

    node_id: int

    action: Optional[str]
    paragraph: Optional[str]

    parent_id: Optional[int]
    children_ids: List[int] = field(default_factory=list)

    ending_paragraph: bool = False
    
   


class GamebookTree:
    """Class for representing the tree for a gamebook"""

    def __init__(self, node_data_list: List[GamebookNodeData]):
        self.node_lookup = {
            node_data.node_id: node_data for node_data in node_data_list
        }

        self.next_node_id = max(node_data.node_id for node_data in node_data_list) + 1

    @staticmethod
    def from_nodes_dict_list(node_data_dict_list):
        """Deserializes from json-style dictionary to GamebookTree"""
        node_data_list = [
            GamebookNodeData.from_dict(node_data) for node_data in node_data_dict_list
        ]

        return GamebookTree(node_data_list)

    def to_nodes_dict_list(self):
        """Serializes class data into a json-style dictionary with list of node
        data"""
        return [node_data.to_dict() for node_data in self.node_lookup.values()]

    def _get_node(self, node_id):
        return self.node_lookup[node_id]

    def make_node(self, parent_id, action=None, paragraph=None):
        """Allow editing action and paragraph"""
        parent = self.node_lookup[parent_id]

        new_node = GamebookNodeData(
            node_id=self.next_node_id,
            action=action,
            paragraph=paragraph,
            parent_id=parent_id,
        )

        self.node_lookup[self.next_node_id] = new_node

        parent.children_ids.append(self.next_node_id)
        self.next_node_id += 1

    def edit_node(self, node_id, action=None, paragraph=None, ending_paragraph=False):
        """Allow editing action and paragraph"""
        node = self.node_lookup[node_id]

        if ending_paragraph:
            node.ending_paragraph = True

        if action is not None:
            node.action = action

        if paragraph is not None:
            node.paragraph = paragraph

    def get_action(self, node_id):
        """Get the action at node with the node_id."""
        return self.node_lookup[node_id].action

    def get_paragraph(self, node_id):
        """Get the paragraph at node with the node_id."""
        return self.node_lookup[node_id].paragraph

    def get_paragraph_list(self, end_node_id):
        """Generates a list of paragraph from the root node to end node
        inclusively."""
        rev_paragraphs = []

        # here we need to build the text list in reverse, since we need to
        # traverse the tree using the parent_id field
        node_id = end_node_id

        while node_id is not None:
            node = self.node_lookup[node_id]
            if node.paragraph is not None:
                rev_paragraphs.append(node.paragraph)
            node_id = node.parent_id

        return list(reversed(rev_paragraphs))
