from monopoly.game import get_property
from monopoly.state import GameState


class View:
    def __init__(self, state: GameState):
        self.state = state

    def get_player(self):
        state = self.state
        player = state.players[state.player]
        return {
            'id': state.player,
            **vars(player)
        }
    
    def get_players(self):
        return self.state.players
    
    def get_destination(self, destination):
        return get_property(self.state, destination)
    
    def owns_property(self, player):
        properties = ((i, get_property(self.state, i)) for i in range(len(self.state.board)))
        return [i for i, property in properties if property.owner == player]
    
    def last_bid(self):
        return self.state.auction

    def create(game: int, state: GameState, action: dict):
        view = {
            'game': game,
            'state': View(state),
            'action': action
        }

        if 'message' in action:
            view = {
                **view,
                'message': action['message']
            }

        return view
