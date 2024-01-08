from dataclasses import dataclass, field
from enum import Enum


@dataclass
class Player:
    cash: int
    position: int
    in_jail: int
    doubles: int


@dataclass
class Property:
    name: str
    set: 'PropertySet'
    price: int = 0
    rent: list[int] = field(default_factory=lambda: [])
    houses: int = 0
    owner: Player = None
    mortgaged: bool = False

class PropertyType(Enum):
    RESIDENTIAL = 1
    UTILITY = 2
    STATION = 3

@dataclass
class PropertySet:
    color: str
    members: list[Property]
    type: PropertyType
