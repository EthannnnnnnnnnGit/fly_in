from pydantic import BaseModel, Field
from enum import Enum
from src.utils.connection import Connection


class HubTypes(Enum):
    """
    Different types of hub
    """
    START = "start_hub"
    END = "end_hub"
    HUB = "hub"


class ZoneType(Enum):
    """
    Different types of access of a hub
    """
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    """
    Hub object
    """
    type: HubTypes
    name: str
    coordinates: tuple[int, int]
    connections: list[Connection] = Field(default=[])
    zone: ZoneType
    color: str | None = Field(default=None)
    max_drones: int = Field(default=1, ge=1)

    def __repr__(self) -> str:
        """Class representation"""
        return self.name
