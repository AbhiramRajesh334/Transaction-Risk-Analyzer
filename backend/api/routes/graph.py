"""Graph-related API routes."""

from fastapi import APIRouter, HTTPException
from graph_engine.graph_manager import graph_manager
from graph_engine.graph_queries import (
    find_shortest_path,
    get_account_degree,
    get_account_neighbors,
    get_account_timeline,
    get_account_transactions,
    get_graph_statistics,
    get_incoming_neighbors,
    get_outgoing_neighbors,
)

router = APIRouter(prefix="/graph", tags=["graph"])


@router.get("/stats")
def get_graph_stats():
    return {"statistics": get_graph_statistics()}


@router.get("/account/{account_id}")
def get_account_graph(account_id: str):
    graph = graph_manager.get_graph()
    if not graph.has_node(account_id):
        raise HTTPException(status_code=404, detail="Account not found in graph.")

    node_data = graph.nodes[account_id]
    transactions = get_account_transactions(account_id)
    incoming_transactions = [tx for tx in transactions if tx["direction"] == "incoming"]
    outgoing_transactions = [tx for tx in transactions if tx["direction"] == "outgoing"]

    return {
        "account_id": account_id,
        "account_type": node_data.get("account_type"),
        "incoming_neighbors": get_incoming_neighbors(account_id),
        "outgoing_neighbors": get_outgoing_neighbors(account_id),
        "degree": get_account_degree(account_id),
        "incoming_transactions": len(incoming_transactions),
        "outgoing_transactions": len(outgoing_transactions),
        "recent_transactions": sorted(transactions, key=lambda tx: tx["timestamp"], reverse=True)[:6],
    }


@router.get("/neighbors/{account_id}")
def get_neighbors(account_id: str):
    graph = graph_manager.get_graph()
    if not graph.has_node(account_id):
        raise HTTPException(status_code=404, detail="Account not found in graph.")
    return {"neighbors": get_account_neighbors(account_id)}


@router.get("/incoming/{account_id}")
def get_incoming(account_id: str):
    graph = graph_manager.get_graph()
    if not graph.has_node(account_id):
        raise HTTPException(status_code=404, detail="Account not found in graph.")
    return {"incoming_neighbors": get_incoming_neighbors(account_id)}


@router.get("/outgoing/{account_id}")
def get_outgoing(account_id: str):
    graph = graph_manager.get_graph()
    if not graph.has_node(account_id):
        raise HTTPException(status_code=404, detail="Account not found in graph.")
    return {"outgoing_neighbors": get_outgoing_neighbors(account_id)}


@router.get("/timeline/{account_id}")
def get_timeline(account_id: str, limit: int = 50):
    graph = graph_manager.get_graph()
    if not graph.has_node(account_id):
        raise HTTPException(status_code=404, detail="Account not found in graph.")
    return {"account_id": account_id, "timeline": get_account_timeline(account_id, limit=limit)}


@router.get("/path/{source}/{target}")
def get_fund_flow_path(source: str, target: str, max_hops: int = 5):
    graph = graph_manager.get_graph()
    if not graph.has_node(source) or not graph.has_node(target):
        raise HTTPException(status_code=404, detail="Source or target account not found in graph.")

    path = find_shortest_path(source, target, max_hops=max_hops)
    if not path:
        return {
            "source": source,
            "target": target,
            "found": False,
            "path": [],
            "path_accounts": [],
        }

    path_accounts = [source]
    for step in path:
        if step["receiver_account"] not in path_accounts:
            path_accounts.append(step["receiver_account"])

    return {
        "source": source,
        "target": target,
        "found": True,
        "path": path,
        "path_accounts": path_accounts,
        "hop_count": len(path),
    }


@router.get("/full")
def get_full_graph():
    """Return the full graph as a frontend-friendly JSON structure.

    Nodes: list of {id, account_type, created_at}
    Edges: list of {source, target, transaction_id, amount, timestamp}
    """
    graph = graph_manager.get_graph()

    nodes = [
        {
            "id": n,
            "account_type": data.get("account_type"),
            "created_at": data.get("created_at"),
        }
        for n, data in graph.nodes(data=True)
    ]

    edges = [
        {
            "source": u,
            "target": v,
            "transaction_id": key,
            "amount": data.get("amount"),
            "timestamp": data.get("timestamp"),
        }
        for u, v, key, data in graph.edges(keys=True, data=True)
    ]

    return {"nodes": nodes, "edges": edges}
