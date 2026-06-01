"""Evidence domain model definitions."""

from pydantic import BaseModel


class Evidence(BaseModel):
    indicator: str
    description: str
    related_entities: list[str] = []
    data_points: dict = {}
