from functools import cached_property
from google.genai import Client, types
from google.adk.models.google_llm import Gemini
import os

api_key = "<api-key-here>"
model_name = "<model-name-here>"


class GeminiWithApiKey(Gemini):
    api_key: str

    @cached_property
    def api_client(self) -> Client:
        return Client(
            api_key=self.api_key,
            http_options=types.HttpOptions(headers=self._tracking_headers()),
        )


def get_model(model_name: str = model_name, api_key: str = api_key) -> GeminiWithApiKey | str:
    if api_key:
        return GeminiWithApiKey(model=model_name, api_key=api_key)
    return model_name
