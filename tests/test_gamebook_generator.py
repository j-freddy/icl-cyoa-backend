import unittest
from unittest import TestCase
from unittest.mock import Mock
from unittest.mock import call

from src.gamebook_generator import GamebookGenerator
from src.text_generator import TextGenerator
from src.graph import GamebookGraph

class GamebookGeneratorTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.example_id = 3
        cls.example_id_alt = 5
        cls.sample_text = "Sample text."
        cls.sample_narrative = "Sample narrative."
        cls.sample_action = "Sample action."
        cls.sample_genre_prompt = "Sample genre prompt."
        cls.sample_paragraph_list = ["Paragraph.", "Other."]
    
    def setUp(self) -> None:
        self.mock_text_generator = Mock(TextGenerator)
        self.mock_graph = Mock(GamebookGraph)
        self.generator = GamebookGenerator(self.mock_text_generator)

    def test_generate_narrative_from_action(self):
        self.mock_text_generator.generate_narrative.return_value = self.sample_narrative
        self.mock_graph.is_narrative.return_value = False

        self.mock_graph.get_paragraph_list.return_value = self.sample_paragraph_list

        self.mock_text_generator.action_to_second_person.return_value = self.sample_action

        self.generator.generate_narrative_from_action(
            self.mock_graph, self.example_id)

        self.mock_text_generator.generate_narrative.assert_called_once()
        self.mock_graph.make_narrative_node.assert_called_once_with(
            parent_id=self.example_id,
            narrative=self.sample_action + " " + self.sample_narrative,
            is_ending=False)
        
    def test_generate_actions_from_narrative(self):
        self.mock_text_generator.generate_actions.return_value = [self.sample_action,
            self.sample_text]
        self.mock_graph.is_narrative.return_value = True

        self.mock_graph.get_paragraph_list.return_value = self.sample_paragraph_list

        self.generator.generate_actions_from_narrative(
            self.mock_graph, self.example_id)

        self.mock_text_generator.generate_actions.assert_called_once()
        self.mock_graph.make_action_node.assert_has_calls([
            call(
                parent_id=self.example_id,
                action=self.sample_action
                ),
            call(
                parent_id=self.example_id,
                action=self.sample_text
                ),
            ])
        
    def test_bridge_node(self):
        bridge_id = 7
        self.mock_text_generator.bridge_content.return_value = self.sample_narrative
        self.mock_graph.make_narrative_node.return_value = bridge_id

        self.generator.bridge_node(
            self.mock_graph, self.example_id, self.example_id_alt)

        self.mock_graph.make_narrative_node.assert_called_once_with(
            parent_id=self.example_id, narrative=self.sample_narrative
        )

        self.mock_graph.connect_nodes.assert_called_once_with(bridge_id, self.example_id_alt)


if __name__ == "__main__":
    unittest.main()
