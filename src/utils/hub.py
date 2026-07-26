from pydantic import BaseModel, Field
from enum import Enum
from .connection import Connection


class HubTypes(Enum):
    START = "start_hub"
    END = "end_hub"
    HUB = "hub"


class ZoneType(Enum):
    NORMAL = "normal"
    BLOCKED = "blocked"
    RESTRICTED = "restricted"
    PRIORITY = "priority"


class Hub(BaseModel):
    type: HubTypes
    name: str
    connections: list[Connection]
    zone: ZoneType
    color: str = Field(default=None)
    max_drones: int = Field(default=1, ge=1)
