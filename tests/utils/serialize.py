from faker import Faker
from monopoly.model import Player, Property
from monopoly.state import GameState


fake = Faker()


def new_player():
    return {
        'doubles': 0,
        'cash': 0,
        'position': 0,
        'in_jail': False,
        'cards': []
    }


def new_state():
    return {
        'started': False,
        'roll': (0, 0),
        'player': 0,
        'players': [],
        'board': [],
        'sets': [],
        'decks': {},
    }


def new_property():
    return {
        'name': fake.pystr(),
        'set': 0
    }


def new_set(type):
    return {
        'type': type
    }


def serialize(func):
    def inner(*args, **kwargs):
        state = func(*args, **kwargs)
        state['players'] = [Player(**player) for player in state['players']]
        return GameState(**state)
    
    return inner
