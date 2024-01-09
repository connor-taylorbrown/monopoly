from dataclasses import dataclass
from monopoly.model import Player, Property


@dataclass
class GameState:
    board: list[Property]
    players: list[Player]
    player: int
    started: bool
    roll: tuple[int, int]
        

@dataclass
class StateUpdater:
    state: GameState

    def set_roll(self, roll: tuple[int, int]):
        self.state.roll = roll

    def next_player(self):
        self.state.player = (self.state.player + 1) % len(self.state.players)

    def go_to(self, destination: int, doubles: bool):
        player = self.state.players[self.state.player]
        def pass_go():
            if 0 <= destination < player.position:
                player.cash += 200

        pass_go()
        player.position = destination
        if doubles:
            player.doubles += 1
        else:
            player.doubles = 0

    def go_to_jail(self):
        player = self.state.players[self.state.player]
        player.position = 10
        player.in_jail = 3
        player.doubles = 0

    def leave_jail(self, destination: int):
        player = self.state.players[self.state.player]
        player.in_jail = 0
        self.go_to(destination, doubles=False)

    def serve_time(self):
        player = self.state.players[self.state.player]
        if player.in_jail > 0:
            player.in_jail -= 1

    def mortgage_property(self, property: Property):
        player = self.state.players[self.state.player]
        player.cash += property.price // 2
        property.mortgaged = True

    def unmortgage_property(self, property: Property):
        player = self.state.players[self.state.player]
        repayment = int(1.1 * property.price / 2)
        player.cash -= repayment
        property.mortgaged = False

    def pay_bank(self, amount: int):
        player = self.state.players[self.state.player]
        player.cash -= amount

    def buy_property(self, property: Property):
        player = self.state.players[self.state.player]
        player.cash -= property.price
        property.owner = player

    def pay_players(self, players: list['Player'], amount: int):
        player = self.state.players[self.state.player]
        players = [payee for payee in players if payee != player]
        player.cash -= len(players) * amount
        for payee in players:
            payee.cash += amount
