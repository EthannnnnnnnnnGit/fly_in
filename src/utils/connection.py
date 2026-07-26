from pydantic import BaseModel, Field
from .hub import Hub


class Connection(BaseModel):
    hub1: Hub
    hub2: Hub
    capacity: int = Field(default=1, ge=1)
