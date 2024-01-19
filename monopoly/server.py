import random
from cachetools import cached
import requests
from monopoly.game import Game
from monopoly.model import Player, Property, PropertySet
from monopoly.state import GameState, StateUpdater


class Board:
    def __init__(self, port: int):
        self.address = f'http://localhost:{port}'

    def get_sets(self):
        response = requests.get(f'{self.address}/sets')
        return response.json()
    
    def get_properties(self):
        response = requests.get(f'{self.address}/properties')
        return response.json()
    
    def get_chance(self):
        response = requests.get(f'{self.address}/chance')
        return response.json()
    
    def get_community_chest(self):
        response = requests.get(f'{self.address}/communityChest')
        return response.json()


class GameServer:
    def __init__(self, board: Board):
        self.board = board
        self.games = []

    def exists(self, id: int) -> bool:
        return id < len(self.games)

    def get(self, id: int) -> tuple[Game, GameState]:
        return self.games[id]

    def create(self) -> int:
        next_id = len(self.games)
        chance = self.board.get_chance()
        community_chest = self.board.get_community_chest()
        state = GameState(
            board=self.board.get_properties(),
            sets=self.board.get_sets(),
            decks={
                'Chance': random.sample(chance, len(chance)),
                'Community Chest': random.sample(community_chest, len(community_chest))
            },
            players=[Player(1200, 0, 0, 0, []) for i in range(3)],
            player=0,
            started=False,
            roll=0
        )
        game = Game(
            state,
            StateUpdater(state)
        )

        self.games.append((game, state))
        return next_id
