from pydantic import BaseModel, Field
from typing import Any


class Connection(BaseModel):
    name: str
    hub1: Any
    hub2: Any
    capacity: int = Field(default=1, ge=1)
