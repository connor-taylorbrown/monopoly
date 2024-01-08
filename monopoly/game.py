import random
from monopoly.state import GameState, StateUpdater


def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)


class Game:
    def __init__(self, state: GameState, updater: StateUpdater):
        self.state = state
        self.updater = updater

    def before_roll(self):
        pass

    def roll(self):
        self.state.started = True
        
        self.updater.set_roll(roll_dice())

        a, b = self.state.roll
        doubles, total = a == b, a + b

        player = self.state.players[self.state.player]
        if doubles and player.doubles == 2:
            return self.updater.go_to_jail()
        
        destination = (player.position + total) % len(self.state.board)

        if player.in_jail > 0:
            if doubles:
                return self.updater.leave_jail(destination)
            elif self.state.must_leave_jail():
                self.updater.pay_bank(50)
                return self.updater.leave_jail(destination)
            else:
                return self.updater.serve_time()
        
        return self.updater.go_to(destination, doubles)
    
    def finalize_turn(self):
        player = self.state.players[self.state.player]
        if player.doubles < 1:
            self.updater.next_player()
