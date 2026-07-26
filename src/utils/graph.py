from pydantic import BaseModel, Field
from .hub import Hub


class Graph(BaseModel):
    hubs: list[Hub]
    nb_drones: int = Field(ge=1)
