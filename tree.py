from dataclasses import dataclass

@dataclass
class GamebookNodeData:
    action: str
    paragraph: str

class GamebookTree:
    """Class for representing
    """
    def __init__(self, adjacency_lists, node_data_list):
        self.adjacency_lists = adjacency_lists
        self.node_data_list = node_data_list
