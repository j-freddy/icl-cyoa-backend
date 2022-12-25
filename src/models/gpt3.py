import openai
from dotenv import load_dotenv

load_dotenv()

class GPT3Model:
    
    def __init__(self, api_key, temperature=0.5, max_tokens=256, presence_penalty=2,
            frequency_penalty = 2) -> None:
        openai.api_key = api_key
        self.temperature = temperature
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty

    def complete(self, prompt: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
        )
        return response.choices[0].text

    def insert(self, prompt: str, suffix: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            suffix=suffix,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
        )
        return response.choices[0].text

    def edit(self, text_to_edit: str, instruction: str) -> str:
        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=text_to_edit,
            instruction=instruction,
            temperature=self.temperature,
        )
        return response.choices[0].text
