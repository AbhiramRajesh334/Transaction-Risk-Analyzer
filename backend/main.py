"""Backend application entry point."""

from fastapi import FastAPI

from api import api_router
from database.database import init_database
from graph_engine.graph_manager import graph_manager

app = FastAPI(title="Explainable Transaction Behavior and Relationship Risk Analyzer")
app.include_router(api_router, prefix="/api")

@app.on_event("startup")
def on_startup():
    init_database()
    graph_manager.build_graph()

@app.get("/")
def health_check():
    return {"status": "ok", "message": "Backend scaffold is ready."}
