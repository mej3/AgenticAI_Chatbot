from datetime import datetime, timedelta
import pandas as pd

TODAY = datetime(2026, 6, 4)

customers_df = pd.DataFrame([
    {"customer_id": "CUST1001", "name": "ABC", "pin": "1234"},
    {"customer_id": "CUST1002", "name": "DEF", "pin": "4321"},
])

accounts_df = pd.DataFrame([
    {"customer_id": "CUST1001", "acct_type": "current", "acct_last4": "4321", "currency": "GBP", "balance": 1860.12},
    {"customer_id": "CUST1001", "acct_type": "savings",  "acct_last4": "9988", "currency": "GBP", "balance": 12340.00},
    {"customer_id": "CUST1002", "acct_type": "current", "acct_last4": "1111", "currency": "GBP", "balance": 279.90},
])

transactions_df = pd.DataFrame([
    {"customer_id": "CUST1001", "acct_last4": "4321", "date": TODAY - timedelta(days=1),  "merchant": "TESCO STORES 5842",   "amount": -42.18,  "category": "groceries",    "channel": "card", "status": "posted"},
    {"customer_id": "CUST1001", "acct_last4": "4321", "date": TODAY - timedelta(days=2),  "merchant": "UBER TRIP",           "amount": -18.60,  "category": "transport",    "channel": "card", "status": "posted"},
    {"customer_id": "CUST1001", "acct_last4": "4321", "date": TODAY - timedelta(days=4),  "merchant": "NETFLIX.COM",         "amount": -10.99,  "category": "subscription", "channel": "card", "status": "posted"},
    {"customer_id": "CUST1001", "acct_last4": "4321", "date": TODAY - timedelta(days=5),  "merchant": "SHELL PAY AT PUMP",   "amount": -1.00,   "category": "fuel",         "channel": "card", "status": "pending"},
    {"customer_id": "CUST1001", "acct_last4": "4321", "date": TODAY - timedelta(days=6),  "merchant": "PAYROLL ACME LTD",    "amount": 2500.00, "category": "income",       "channel": "bank", "status": "posted"},
    {"customer_id": "CUST1001", "acct_last4": "9988", "date": TODAY - timedelta(days=12), "merchant": "TRANSFER FROM 4321",  "amount": 500.00,  "category": "transfer",     "channel": "bank", "status": "posted"},
    {"customer_id": "CUST1002", "acct_last4": "1111", "date": TODAY - timedelta(days=1),  "merchant": "AMAZON MKTPLACE",     "amount": -24.99,  "category": "shopping",     "channel": "card", "status": "posted"},
])

transactions_df["date"] = pd.to_datetime(transactions_df["date"])
