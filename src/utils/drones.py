from dataclasses import dataclass
from .hub import Hub
from src.visual.PyQt6 import QEntity


@dataclass
class Drones():
    name: str
    hub_turns: list[Hub]
    entity: QEntity | None
