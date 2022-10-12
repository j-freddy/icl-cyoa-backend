from dataclasses import dataclass, asdict

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

    def to_dict(self):
        return {"adjacencyLists": self.adjacency_lists, "nodes": [asdict(node_data) for node_data in self.node_data_list]}
