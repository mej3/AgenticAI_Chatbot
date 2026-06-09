import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk import Agent
from google.genai.types import GenerateContentConfig, ThinkingConfig
from pydantic import BaseModel
from helpers.file_loader import load_instructions_file
from bot.model import get_model
from bot.tools import inspect_unfamiliar_charge, explain_suspicious_transactions


# class SuspiciousTxExplainOutput(BaseModel):
#     found: bool
#     merchant: str
#     amount: float
#     date: str
#     status: str
#     explanation: str

susp_tx_agent = Agent(
    name="susp_agent",
    model=get_model(),
    description=load_instructions_file("bot/susp_tx_agent/description.md"),
    instruction=load_instructions_file("bot/susp_tx_agent/instructions.md"),
    tools=[inspect_unfamiliar_charge, explain_suspicious_transactions],
    # output_schema=SuspiciousTxExplainOutput,
    # output_key="suspicious_tx_explain",
    generate_content_config=GenerateContentConfig(temperature=0.0, 
                                                #   thinking_config=ThinkingConfig(include_thoughts=True)
                                                  ),
)
