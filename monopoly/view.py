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
        return self.state.board[destination]
    
    def create(game: int, state: GameState, action: dict):
        return {
            'game': game,
            'state': View(state),
            'action': action
        }
