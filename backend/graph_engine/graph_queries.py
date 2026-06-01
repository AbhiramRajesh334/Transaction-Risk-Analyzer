"""Reusable transaction graph query helpers."""

import networkx as nx
from graph_engine.graph_manager import graph_manager


def _get_graph() -> nx.MultiDiGraph:
    return graph_manager.get_graph()


def get_account_neighbors(account_id: str) -> list[str]:
    """Return unique neighbor account IDs connected to the account."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return []

    neighbors = set(graph.predecessors(account_id)) | set(graph.successors(account_id))
    return sorted(neighbors)


def get_incoming_neighbors(account_id: str) -> list[str]:
    """Return account IDs that send money into the given account."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return []
    return sorted(set(graph.predecessors(account_id)))


def get_outgoing_neighbors(account_id: str) -> list[str]:
    """Return account IDs that receive money from the given account."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return []
    return sorted(set(graph.successors(account_id)))


def get_account_degree(account_id: str) -> int:
    """Return total degree (incoming + outgoing) for the account."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return 0
    return graph.degree(account_id)


def get_account_transactions(account_id: str) -> list[dict]:
    """Return transaction metadata for all edges connected to the account."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return []

    transactions = []
    for sender, _, key, data in graph.in_edges(account_id, keys=True, data=True):
        transactions.append(
            {
                "transaction_id": key,
                "sender_account": sender,
                "receiver_account": account_id,
                "amount": data.get("amount"),
                "timestamp": data.get("timestamp"),
                "direction": "incoming",
            }
        )

    for _, receiver, key, data in graph.out_edges(account_id, keys=True, data=True):
        transactions.append(
            {
                "transaction_id": key,
                "sender_account": account_id,
                "receiver_account": receiver,
                "amount": data.get("amount"),
                "timestamp": data.get("timestamp"),
                "direction": "outgoing",
            }
        )

    return sorted(transactions, key=lambda tx: tx["timestamp"])


def get_graph_statistics() -> dict:
    """Return summary statistics for the current transaction graph."""
    graph = _get_graph()
    node_count = graph.number_of_nodes()
    edge_count = graph.number_of_edges()
    average_degree = sum(dict(graph.degree()).values()) / node_count if node_count else 0.0
    density = nx.density(graph)

    return {
        "total_nodes": node_count,
        "total_edges": edge_count,
        "average_degree": average_degree,
        "graph_density": density,
    }
