import os
import random

import openai
from dotenv import load_dotenv
from time import sleep

from src.constants import MAX_RATE_LIMIT_ERRORS, REQ_FAILURE_TIMEOUT_SECS

load_dotenv()


class OpenAIUnavailableError(Exception):

    pass

class OpenAIRateLimitError(Exception):

    pass

class APIKeyRoundRobinSelector:
    def __init__(self, user_api_key=None):
        self.curr_index: int = 0
        self.user_api_key = user_api_key
        self.keys: list[str] = [x.strip() for x in os.getenv("OPENAI_API_KEY").split(",")]

    def update_round_robin_index(self):
        if self.curr_index == len(self.keys) - 1:
            self.curr_index = 0
            return
        self.curr_index += 1

    def get_api_key(self) -> str:
        # roundrobin scheduler
        if self.user_api_key:
            return self.user_api_key
        next_key = self.keys[self.curr_index]
        self.update_round_robin_index()
        return next_key
        

def error_handling(func):
    def wrapper(self, *args, unavailable_count=0, rate_limit_count=0, **kwargs):
        self.rate_limited = False

        try:
            return func(self, *args, **kwargs)

        except openai.error.RateLimitError:
            # key didn't work - sleep and try a different one from round robin
            print("timeout error")

            if rate_limit_count >= MAX_RATE_LIMIT_ERRORS:
                raise OpenAIRateLimitError

            self.rate_limited = True
            sleep(REQ_FAILURE_TIMEOUT_SECS)

            return wrapper(self, *args, **kwargs, 
                unavailable_count=unavailable_count, rate_limit_count=rate_limit_count+1)

        except (openai.error.ServiceUnavailableError, openai.error.APIConnectionError):
            # these errors indicate a problem with the openai service

            raise OpenAIUnavailableError

    return wrapper


class GPT3Model:

    def __init__(self, api_key=None, temperature=0.5, max_tokens=256, presence_penalty=2,
            frequency_penalty = 2) -> None:

        self.api_key = api_key
        self.api_key_generator = self._api_key_generator()
        self.rate_limited = False

        self.round_robin_scheduler = APIKeyRoundRobinSelector()

        self.temperature = temperature
        self.max_tokens = max_tokens
        self.presence_penalty = presence_penalty
        self.frequency_penalty = frequency_penalty


    def _api_key_generator(self):
        while True:
            if self.api_key is None or self.rate_limited:
                yield self.round_robin_scheduler.get_api_key()

            yield self.api_key

    @error_handling
    def complete(self, prompt: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            api_key=self.next_api_key,
        )
        return response.choices[0].text

    @error_handling
    def insert(self, prompt: str, suffix: str) -> str:
        response = openai.Completion.create(
            model="text-davinci-003",
            prompt=prompt,
            suffix=suffix,
            temperature=self.temperature,
            max_tokens=self.max_tokens,
            presence_penalty=self.presence_penalty,
            frequency_penalty=self.frequency_penalty,
            api_key=self.next_api_key,
        )
        return response.choices[0].text

    @error_handling
    def edit(self, text_to_edit: str, instruction: str) -> str:
        response = openai.Edit.create(
            model="text-davinci-edit-001",
            input=text_to_edit,
            instruction=instruction,
            temperature=self.temperature,
            api_key=self.next_api_key,
        )
        return response.choices[0].text
    
    @property
    def next_api_key(self):
        return next(self.api_key_generator)
