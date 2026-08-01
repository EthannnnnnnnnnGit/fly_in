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
    coordinates: tuple[int, int]
    connections: list[Connection] = Field(default=[])
    zone: ZoneType
    color: str = Field(default=None)
    max_drones: int = Field(default=1, ge=1)

    def get_attributes(self) -> None:
        print(f"Type: {self.type}\n"
              f"Name: {self.name}\n"
              f"Coordinates: {self.coordinates}\n"
              f"Connections: {self.connections}\n"
              f"Zone: {self.zone}\n"
              f"Color: {self.color}\n"
              f"Max_drones: {self.max_drones}")

    def __repr__(self):
        return self.name
