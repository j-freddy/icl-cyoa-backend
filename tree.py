from dataclasses import dataclass, asdict
from dataclasses_json import dataclass_json, LetterCase
from typing import List, Optional

@dataclass_json(letter_case=LetterCase.CAMEL)
@dataclass
class GamebookNodeData:
    node_id: int

    action: Optional[str]
    paragraph: str

    parent_id: Optional[int]
    children_ids: List[int]

class GamebookTree:
    """Class for representing the tree for a gamebook"""

    def __init__(self, node_data_list: List[GamebookNodeData]):
        self.node_lookup = {node_data.node_id: node_data for node_data in node_data_list}

    def from_nodes_dict_list(node_data_dict_list):
        node_data_list = [GamebookNodeData.from_dict(node_data) for node_data in node_data_dict_list]

        return GamebookTree(node_data_list)

    def to_nodes_dict_list(self):
        return [node_data.to_dict() for node_data in self.node_lookup.values()]

    def get_text_up_to_node(self, end_node_id):
        rev_text = []
        node_id = self.node_lookup[end_node_id].parent_id

        while node_id is not None:
            node = self.node_lookup[node_id]

            rev_text.append(node.paragraph)
            if node.action is not None:
                rev_text.append(node.action)

            node_id = node.parent_id

        return "".join(reversed(rev_text))
