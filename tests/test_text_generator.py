from unittest import TestCase
from unittest.mock import Mock

from src.text_generator import GamebookTextGenerator
from src.models.gpt3 import GPT3Model

class GamebookTextGeneratorTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.sample_text = "Sample text."
        cls.sample_response = "Sample response."

    def test_generate_paragraph(self):
        mock_model = Mock(GPT3Model)
        generator = GamebookTextGenerator(mock_model)

        mock_model.complete.return_value = self.sample_response
        paragraph = generator._generate_paragraph(self.sample_text)
        mock_model.complete.assert_called_once_with(self.sample_text)
        self.assertEqual(self.sample_response, paragraph)

    def test_action_to_second_person(self):
        mock_model = Mock(GPT3Model)
        generator = GamebookTextGenerator(mock_model)

        mock_model.edit.return_value = self.sample_response
        expected_instruction = "Rewrite this as 'You choose ...'"
        edited = generator._action_to_second_person(self.sample_text)
        mock_model.edit.assert_called_once_with(text_to_edit=self.sample_text, 
                instruction=expected_instruction)
        self.assertEqual(self.sample_response, edited)
    
    def test_option_prompt(self):
        num_options = 5
        expected_text = "You have 5 options:"
        actual_text = GamebookTextGenerator._option_prompt(num_options)
        self.assertEqual(expected_text, actual_text)

    def test_paragraphs_to_prompt(self):
        paragraphs = ["P1", "P2", "P3"]
        expected_text = "P1 P2 P3"
        actual_text = GamebookTextGenerator._paragraphs_to_prompt(paragraphs)
        self.assertEqual(expected_text, actual_text)

    def test_generate_actions_correct_format(self):
        mock_return = "\n" + \
        "1) You can eat apples.\n" + \
        "2) You can go home.\n"
        self._test_template_generate_actions(mock_return)

    def test_generate_actions_without_period(self):
        mock_return = "\n" + \
        "1) You can eat apples\n" + \
        "2) You can go home\n"
        self._test_template_generate_actions(mock_return)

    def test_generate_actions_extra_alternative_numbering(self):
        mock_return = "\n" + \
        "1. You can eat apples.\n" + \
        "2. You can go home.\n"
        self._test_template_generate_actions(mock_return)

    def test_generate_actions_extra_white_space(self):
        mock_return = "  \n" + \
        "  1)  You can eat apples.  \n" + \
        "  2)  You can go home.  \n"
        self._test_template_generate_actions(mock_return)

    def test_generate_actions_extra_continuation(self):
        mock_return = "\n" + \
        "1) You can eat apples.\n" + \
        "2) You can go home.\n" + \
        "\n" + \
        "If you choose to go home, you go home.\n"
        self._test_template_generate_actions(mock_return)

    def _test_template_generate_actions(self, mock_return: str):
        mock_model = Mock(GPT3Model)
        generator = GamebookTextGenerator(mock_model)

        mock_model.complete.return_value = mock_return
        option_text = "You have 2 options:"
        actions = generator._generate_actions(self.sample_text)
        mock_model.complete.assert_called_once_with(self.sample_text + " " + option_text)
        self.assertEqual(2, len(actions))
        self.assertEqual("You can eat apples.", actions[0])
        self.assertEqual("You can go home.", actions[1])
