from dataclasses import dataclass
from monopoly.model import Player, Property, PropertyType


@dataclass
class GameState:
    board: list[Property]
    players: list[Player]
    player: int
    started: bool
    roll: tuple[int, int]

    def must_leave_jail(self) -> bool:
        player = self.players[self.player]
        return player.in_jail == 1

    def get_rent(self) -> int:
        player = self.players[self.player]
        position = player.position
        property = self.board[position]

        def is_full_set_owned():
            return all(member.owner == property.owner for member in property.set)
        
        if property.owner is None or property.owner == player or property.mortgaged:
            return 0
        
        if property.set.type == PropertyType.RESIDENTIAL:
            level = property.houses
            if level >= 1:
                return property.rent[level]
            elif is_full_set_owned(property):
                return 2 * property.rent[0]
            else:
                return property.rent[0]
        elif property.set.type == PropertyType.UTILITY:
            roll = sum(self.roll)
            if is_full_set_owned(property):
                return 10 * roll
            else:
                return 4 * roll
        elif property.set.type == PropertyType.STATION:
            level = sum(1 for member in property.set if member.owner == property.owner) - 1
            return property.rent[level]
        

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
        player.position = 20
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
