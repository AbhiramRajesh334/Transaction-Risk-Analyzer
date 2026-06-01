"""Builds a directed transaction graph from the SQLite dataset."""

import networkx as nx
from services.account_service import list_accounts
from services.transaction_service import list_transactions


def build_graph() -> nx.MultiDiGraph:
    """Construct a directed MultiDiGraph from accounts and transactions."""
    graph = nx.MultiDiGraph()

    # Add account nodes and preserve account metadata for explainability.
    for account in list_accounts():
        graph.add_node(
            account["account_id"],
            account_id=account["account_id"],
            account_type=account["account_type"],
            created_at=account["created_at"],
        )

    # Add transaction edges with transaction metadata stored on each directed edge.
    for transaction in list_transactions():
        graph.add_edge(
            transaction["sender_account"],
            transaction["receiver_account"],
            key=transaction["transaction_id"],
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"],
            timestamp=transaction["timestamp"],
        )

    return graph
