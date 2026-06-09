import os, sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from fastmcp import FastMCP
from bot.tools import (
    get_transaction_history,
    inspect_unfamiliar_charge,
    explain_suspicious_transactions,
)
import bot.tools as _tools

mcp = FastMCP("banking-tools")


def authenticate_customer(customer_id: str, pin: str) -> dict:
    """Authenticates a customer using their customer ID and PIN."""
    return _tools.authenticate_customer(customer_id, pin, tool_context=None)


def get_account_balance(customer_id: str, acct_last4: str = None) -> dict:
    """Returns the current and potential balance for a customer's account(s).

    Args:
        customer_id: The customer's ID.
        acct_last4: Last 4 digits of a specific account (optional).
    """
    return _tools.get_account_balance(customer_id, tool_context=None, acct_last4=acct_last4)


mcp.tool()(authenticate_customer)
mcp.tool()(get_account_balance)
mcp.tool()(get_transaction_history)
mcp.tool()(inspect_unfamiliar_charge)
mcp.tool()(explain_suspicious_transactions)

if __name__ == "__main__":
    mcp.run(transport="stdio")
