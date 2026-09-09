from dataclasses import dataclass
from src.utils.hub import Hub
from src.visual.PyQt6 import QEntity
from src.utils.connection import Connection


@dataclass
class Drones():
    name: str
    hub_turns: list[Hub | Connection]
    entity: QEntity | None
