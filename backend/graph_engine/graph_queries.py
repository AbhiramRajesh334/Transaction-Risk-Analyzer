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


def find_shortest_path(source: str, target: str, max_hops: int = 5) -> list[dict]:
    """Return the shortest fund-flow path between two accounts."""
    graph = _get_graph()
    if not graph.has_node(source) or not graph.has_node(target):
        return []

    simple_graph = nx.DiGraph()
    for u, v, key, data in graph.edges(keys=True, data=True):
        simple_graph.add_edge(u, v, transaction_id=key, amount=data.get("amount"), timestamp=data.get("timestamp"))

    try:
        node_path = nx.shortest_path(simple_graph, source=source, target=target)
    except (nx.NetworkXNoPath, nx.NodeNotFound):
        return []

    if len(node_path) - 1 > max_hops:
        return []

    path_steps = []
    for index in range(len(node_path) - 1):
        sender = node_path[index]
        receiver = node_path[index + 1]
        edge_data = simple_graph.get_edge_data(sender, receiver) or {}
        path_steps.append(
            {
                "step": index + 1,
                "sender_account": sender,
                "receiver_account": receiver,
                "transaction_id": edge_data.get("transaction_id"),
                "amount": edge_data.get("amount"),
                "timestamp": edge_data.get("timestamp"),
            }
        )
    return path_steps


def account_participates_in_cycle(account_id: str, max_length: int = 3) -> bool:
    """Return True when the account participates in a short directed cycle (e.g. A→B→C→A)."""
    graph = _get_graph()
    if not graph.has_node(account_id):
        return False

    for first_hop in graph.successors(account_id):
        if first_hop == account_id:
            continue
        for second_hop in graph.successors(first_hop):
            if second_hop in {account_id, first_hop}:
                continue
            if graph.has_edge(second_hop, account_id):
                return True

            if max_length >= 4:
                for third_hop in graph.successors(second_hop):
                    if third_hop in {account_id, first_hop, second_hop}:
                        continue
                    if graph.has_edge(third_hop, account_id):
                        return True
    return False


def get_account_timeline(account_id: str, limit: int = 50) -> list[dict]:
    """Return chronological transactions for an account."""
    transactions = get_account_transactions(account_id)
    return sorted(transactions, key=lambda tx: tx.get("timestamp") or "")[:limit]


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
