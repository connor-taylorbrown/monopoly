from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Player:
    cash: int
    position: int
    in_jail: int
    doubles: int
    cards: list[dict]


@dataclass
class Property:
    name: str
    type: int
    set: int = 0
    color: str = ''
    price: int = 0
    rent: list[int] = field(default_factory=lambda: [])
    houses: int = 0
    owner: int | None = None
    mortgaged: bool = False


class PropertyType(Enum):
    NONE = 0
    RESIDENTIAL = 1
    UTILITY = 2
    STATION = 3


class PropertySet:
    color: str
    type: int
