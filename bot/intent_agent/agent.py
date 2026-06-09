import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk.agents import LlmAgent
from google.genai.types import GenerateContentConfig
from pydantic import BaseModel
from helpers.file_loader import load_instructions_file
from bot.model import get_model


class IntentOutput(BaseModel):
    intent: str
    confidence: str  # high|medium|low
    reasoning: str

intent_agent = LlmAgent(
    name="intent_recognition_agent",
    model=get_model(),
    description=load_instructions_file("bot/intent_agent/description.md"),
    instruction=load_instructions_file("bot/intent_agent/instructions.md"),
    output_schema=IntentOutput,
    output_key="recognized_intent",
    generate_content_config=GenerateContentConfig(temperature=0.0),
)
