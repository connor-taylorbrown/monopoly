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
    
    def index_properties(self):
        sets = self.get_sets()

        properties = self.get_properties()
        for property in properties:
            set = sets[property.get('set', 0)]
            if 'members' not in set:
                set['members'] = []
            set['members'].append(property)
            property['set'] = set

        for property in properties:
            property['set'] = PropertySet(**property['set'])
        
        return [Property(**property) for property in properties]


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
        state = GameState(
            board=self.board.index_properties(),
            players=[Player(1200, 0, 0, 0) for i in range(3)],
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
