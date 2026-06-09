import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..")))

from google.adk import Agent
from helpers.file_loader import load_instructions_file
from bot.model import get_model
from bot.tools import (
    authenticate_customer,
    get_account_balance,
    get_transaction_history,
    inspect_unfamiliar_charge,
    explain_suspicious_transactions,
)
from bot.intent_agent.agent import intent_agent
from bot.susp_tx_agent.agent import susp_tx_agent


root_agent = Agent(
    name="cust_agent",
    model=get_model(),
    description=load_instructions_file("bot/orchestrator_agent/description.md"),
    instruction=load_instructions_file("bot/orchestrator_agent/instructions.md"),
    tools=[
        authenticate_customer,
        get_account_balance,
        get_transaction_history,
        inspect_unfamiliar_charge,
        explain_suspicious_transactions,
    ],
    sub_agents=[
        intent_agent,
        susp_tx_agent,
    ],
)
