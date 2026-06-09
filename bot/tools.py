from typing import Optional
from bot.data import TODAY, customers_df, accounts_df, transactions_df
import pandas as pd
from datetime import timedelta
from google.adk.tools import ToolContext


def authenticate_customer(customer_id: str, pin: str, tool_context: ToolContext) -> dict:
    """Authenticates a customer using their customer ID and PIN."""
    row = customers_df[(customers_df["customer_id"] == customer_id) & (customers_df["pin"] == pin)]
    if row.empty:
        return {
            "authenticated": False,
            "message": "Authentication failed. Please check the customer ID or PIN."
        }

    customer = row.iloc[0].to_dict()
    customer_accounts = accounts_df[accounts_df["customer_id"] == customer_id][["acct_type", "acct_last4", "currency"]].to_dict(orient="records")
    if tool_context:
        tool_context.state["customer_id"] = customer["customer_id"]
    return {
        "authenticated": True,
        "customer_id": customer["customer_id"],
        "customer_name": customer["name"],
        "accounts": customer_accounts,
        "message": (
            f"Authenticated customer {customer['name']}. Use this customer_id for subsequent balance, transaction, and charge lookups."
        )
    }


def get_account_balance(customer_id: str, tool_context: ToolContext, acct_last4: Optional[str] = None) -> dict:
    """Returns the current and potential balance for a customer's account(s).

    Args:
        customer_id: The customer's ID.
        acct_last4: Last 4 digits of a specific account (optional).
    """
    cust_accts = accounts_df[accounts_df["customer_id"] == customer_id]
    if cust_accts.empty:
        return {"found": False, "message": "No accounts found for the customer."}

    if not acct_last4:
        curr_balance = round(cust_accts['balance'].sum(), 2)
        in_out = transactions_df[transactions_df["customer_id"] == customer_id]["amount"].sum()
        avail_balance = round(curr_balance + in_out, 2)
        if tool_context:
            tool_context.state["available_balance"] = avail_balance
        return {"found": True, "message": f"Current balance: £{curr_balance}, Potential balance after pending liabilities: £{avail_balance}"}
    else:
        curr_balance = round(cust_accts[cust_accts["acct_last4"] == acct_last4]['balance'].sum(), 2)
        in_out = transactions_df[(transactions_df["customer_id"] == customer_id) & (transactions_df["acct_last4"] == acct_last4)]["amount"].sum()
        avail_balance = round(curr_balance + in_out, 2)
        if tool_context:
            tool_context.state["available_balance"] = avail_balance
        return {"found": True, "message": f"Current balance: £{curr_balance}, Potential balance after pending liabilities: £{avail_balance}"}


def get_transaction_history(
    customer_id: str,
    acct_last4: Optional[str] = None,
    days: int = 30,
    tx_cnt_limit: int = 10,
    category: Optional[str] = None
) -> dict:
    """Returns recent transaction history for a customer.

    Args:
        customer_id: The customer's ID.
        acct_last4: Last 4 digits of account to filter by (optional).
        days: Number of days to look back (default 30).
        tx_cnt_limit: Maximum number of transactions to return (default 10).
        category: Transaction category filter (optional).
    """
    tx = transactions_df[transactions_df["customer_id"] == customer_id]
    if tx.empty:
        return {"found": False, "message": "No transactions found for the customer."}

    if acct_last4:
        tx = tx[tx["acct_last4"] == acct_last4]
        if tx.empty:
            return {"found": False, "message": f"No transactions found for account ending in {acct_last4}."}

    if category:
        tx = tx[tx["category"].str.lower() == category.lower()]
        if tx.empty:
            return {"found": False, "message": f"No transactions found for the category '{category}'."}

    cutoff = TODAY - timedelta(days=days)
    tx = tx[tx["date"] >= pd.Timestamp(cutoff)]
    if tx.empty:
        return {"found": False, "message": f"No transactions found in the last '{days}' days."}

    tx = tx.sort_values("date", ascending=False).head(tx_cnt_limit)
    return {
        "found": True,
        "customer_id": customer_id,
        "transactions": [
            {
                "date": row["date"].strftime("%Y-%m-%d"),
                "acct_last4": row["acct_last4"],
                "merchant": row["merchant"],
                "amount": float(row["amount"]),
                "category": row["category"],
                "channel": row["channel"],
                "status": row["status"],
            }
            for _, row in tx.iterrows()
        ]}


def inspect_unfamiliar_charge(
    customer_id: str,
    merchant_hint: Optional[str] = None,
    amount: Optional[float] = None,
    acct_last4: Optional[str] = None,
    days: int = 90
) -> dict:
    """Identifies and explains potentially unfamiliar charges using simple merchant heuristics.

    Args:
        customer_id: The customer's ID.
        merchant_hint: Partial merchant name to search for (optional).
        amount: Exact charge amount to match (optional).
        acct_last4: Last 4 digits of account to filter by (optional).
        days: Number of days to look back (default 90).
    """
    tx = transactions_df[(transactions_df["customer_id"] == customer_id) & (transactions_df["amount"] < 0)]

    if acct_last4:
        tx = tx[tx["acct_last4"] == acct_last4]
    if merchant_hint:
        merchant_hint_lower = merchant_hint.lower()
        tx = tx[tx["merchant"].str.lower().str.contains(merchant_hint_lower, na=False)]
    if amount:
        tx = tx[tx["amount"].round(2) == round(float(amount), 2)]

    cutoff = TODAY - timedelta(days=days)
    tx = tx[tx["date"] >= pd.Timestamp(cutoff)]

    if tx.empty:
        return {"found": False, "message": "I could not find a matching charge with the details provided."}

    explanations = []
    for _, row in tx.sort_values("date", ascending=False).iterrows():
        merchant = row["merchant"].upper()
        outgoing = 1 if row["amount"] < 0 else 0
        category = row['category'].lower()
        explanation = "This looks like a valid card charge, but I cannot classify it with high confidence."

        if "NETFLIX" in merchant and outgoing == 1:
            explanation = "This is likely a recurring streaming subscription charge."
        elif "UBER" in merchant and outgoing == 1:
            explanation = "This appears to be a ride-share transaction."
        elif "SHELL" in merchant and outgoing == 1:
            explanation = "This looks like fuel purchase."
        elif "TESCO" in merchant and outgoing == 1:
            explanation = "This looks like a grocery purchase."
        elif "AMAZON" in merchant and outgoing == 1:
            explanation = "This looks like an online retail purchase."
        elif category == "fuel" and outgoing == 1 and row["status"] == "pending":
            explanation = "This may be a small fuel pre-authorisation hold that can later be replaced by the final amount."

        explanations.append({
            "date": row["date"].strftime("%Y-%m-%d"),
            "acct_last4": row["acct_last4"],
            "merchant": row["merchant"],
            "amount": float(row["amount"]),
            "status": row["status"],
            "likely_explanation": explanation
        })

    return {"found": True, "customer_id": customer_id, "matches": explanations}


def explain_suspicious_transactions(transactions_text: str) -> str:
    """Uses Gemini directly to explain suspicious transactions in plain language.

    Args:
        transactions_text: Text description of transactions to explain.
    """
    from google import genai
    from bot.model import api_key, model_name

    client = genai.Client(api_key=api_key)
    prompt = f"""
    You are a helpful assistant.
    Explain clearly and concisely why these transactions may be suspicious.

    Transactions:
    {transactions_text}
    """
    response = client.models.generate_content(model=model_name, contents=prompt)
    return response.text
