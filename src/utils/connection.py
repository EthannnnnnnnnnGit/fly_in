from pydantic import BaseModel, Field
from typing import Any


class Connection(BaseModel):
    """
    Connection objects
    """
    name: str
    hub1: Any
    hub2: Any
    capacity: int = Field(default=1, ge=1)

    def __repr__(self) -> str:
        """Class representation"""
        return self.name
