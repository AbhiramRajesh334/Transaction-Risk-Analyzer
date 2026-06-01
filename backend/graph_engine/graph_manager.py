"""Maintain a singleton transaction graph and support dynamic updates."""

import networkx as nx
from graph_engine.graph_builder import build_graph


class GraphManager:
    """A dynamic graph manager for transaction graph lifecycle operations."""

    def __init__(self):
        self._graph: nx.MultiDiGraph = nx.MultiDiGraph()
        self._is_built = False

    def build_graph(self) -> nx.MultiDiGraph:
        """Build the graph from the current database state."""
        self._graph = build_graph()
        self._is_built = True
        return self._graph

    def refresh_graph(self) -> nx.MultiDiGraph:
        """Refresh the graph by rebuilding it from the database."""
        return self.build_graph()

    def add_transaction(self, transaction: dict) -> None:
        """Add a single transaction edge to the existing graph without full rebuild."""
        if not self._is_built:
            self.build_graph()

        sender = transaction["sender_account"]
        receiver = transaction["receiver_account"]

        if not self._graph.has_node(sender) or not self._graph.has_node(receiver):
            raise ValueError("Both sender and receiver accounts must exist in the graph before adding a transaction.")

        self._graph.add_edge(
            sender,
            receiver,
            key=transaction["transaction_id"],
            transaction_id=transaction["transaction_id"],
            amount=transaction["amount"],
            timestamp=transaction["timestamp"],
        )

    def remove_transaction(self, transaction_id: str) -> bool:
        """Remove a transaction edge from the graph by its transaction ID."""
        if not self._is_built:
            self.build_graph()

        removed = False
        for u, v, key in list(self._graph.edges(keys=True)):
            if key == transaction_id:
                self._graph.remove_edge(u, v, key=key)
                removed = True
                break

        return removed

    def get_graph(self) -> nx.MultiDiGraph:
        """Return the current graph instance."""
        if not self._is_built:
            self.build_graph()
        return self._graph


graph_manager = GraphManager()
