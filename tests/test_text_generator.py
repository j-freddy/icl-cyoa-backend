import unittest
from unittest import TestCase
from unittest.mock import Mock
from parameterized import parameterized

from src.text_generator import TextGenerator
from src.models.gpt3 import GPT3Model

class TextGeneratorTest(TestCase):

    @classmethod
    def setUpClass(cls) -> None:
        cls.sample_text = "Sample text."
        cls.sample_suffix = "Sample suffix."
        cls.sample_response = "Sample response."

    def setUp(self) -> None:
        self.mock_model = Mock(GPT3Model)
        self.generator = TextGenerator(self.mock_model)

    test_generate_narrative_cases = [
        (False, None, ""),
        (True, None, "\n\nGenerate an ending."),
        (False, "happy", "\n\nGenerate a happy continuation."),
        (True, "happy", "\n\nGenerate a happy ending."),
    ]

    @parameterized.expand(test_generate_narrative_cases)
    def test_generate_narrative(self, is_ending, descriptor, extra_text):

        self.mock_model.complete.return_value = self.sample_response
        paragraph = self.generator.generate_narrative(self.sample_text, 
                is_ending=is_ending, descriptor=descriptor)
        extra_text += "\n\nResult: "
        self.mock_model.complete.assert_called_once_with(self.sample_text + extra_text)
        expected = self.sample_response + (" The end." if is_ending else "")
        self.assertEqual(expected, paragraph)

    def test_action_to_second_person(self):

        self.mock_model.edit.return_value = self.sample_response
        expected_instruction = "Rewrite this as 'You choose ...'"
        edited = self.generator.action_to_second_person(self.sample_text)
        self.mock_model.edit.assert_called_once_with(self.sample_text, expected_instruction)
        self.assertEqual(self.sample_response, edited)
    
    def test_option_prompt(self):
        num_options = 5
        expected_text = "You have 5 options:"
        actual_text = TextGenerator.option_prompt(num_options)
        self.assertEqual(expected_text, actual_text)

    def test_summarise(self):
        self.mock_model.complete.return_value = self.sample_response
        expected_instruction = "Summarize the story in 2nd person:"
        expected_prompt = f"{self.sample_text}\n\n{expected_instruction}"
        actual_response = self.generator.summarise(self.sample_text)
        self.mock_model.complete.assert_called_once_with(expected_prompt)
        self.assertEqual(self.sample_response, actual_response)

    def test_bridge_content(self):
        self.mock_model.insert.return_value = self.sample_response
        actual_response = self.generator.bridge_content(self.sample_text, self.sample_suffix)
        self.mock_model.insert.assert_called_once_with(f"{self.sample_text}\n\n", f"\n\n{self.sample_suffix}")
        self.assertEqual(self.sample_response, actual_response)

    generate_actions_return_values = [
        # Normal
        "\n" + \
        "1) You can eat apples.\n" + \
        "2) You can go home.\n",
        # Without period
        "\n" + \
        "1) You can eat apples\n" + \
        "2) You can go home\n",
        # Alternative numbering
        "\n" + \
        "1. You can eat apples.\n" + \
        "2. You can go home.\n",
        # Extra whitespace
        "  \n" + \
        "  1)  You can eat apples.  \n" + \
        "  2)  You can go home.  \n",
        # Extra content
        "\n" + \
        "1) You can eat apples.\n" + \
        "2) You can go home.\n" + \
        "\n" + \
        "If you choose to go home, you go home.\n"
    ]

    @parameterized.expand(generate_actions_return_values)
    def test_template_generate_actions(self, mock_return: str):
        self.mock_model.complete.return_value = mock_return
        option_text = "You have 2 options:"
        actions = self.generator.generate_actions(self.sample_text)
        self.mock_model.complete.assert_called_once_with(self.sample_text + " " + option_text)
        self.assertEqual(2, len(actions))
        self.assertEqual("You can eat apples.", actions[0])
        self.assertEqual("You can go home.", actions[1])

    def test_new_story(self):
        self.mock_model.complete.return_value = self.sample_response
        initial_values = [
            ("themes", "jolly, fantasy"),
            ("items", ""),
            ("characters", "Talice, Grob")
        ]
        story = self.generator.new_story(initial_values)
        expected_prompt = "Write an adventure story with themes: \"jolly, fantasy\"; " + \
                "items: \"\"; characters: \"Talice, Grob\" in second person:"
        self.mock_model.complete.assert_called_once_with(expected_prompt)
        self.assertEqual(self.sample_response, story)

if __name__ == "__main__":
    unittest.main()
