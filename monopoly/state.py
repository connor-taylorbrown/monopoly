from dataclasses import dataclass
from monopoly.model import Player, Property


@dataclass
class GameState:
    board: dict
    sets: dict
    decks: dict
    players: list[Player]
    player: int
    started: bool
    roll: tuple[int, int]
        

@dataclass
class StateUpdater:
    state: GameState

    def set_roll(self, roll: tuple[int, int]):
        player = self.state.players[self.state.player]
        self.state.roll = roll

        a, b = roll
        if a == b:
            player.doubles += 1
        else:
            player.doubles = 0

    def set_player(self, player):
        self.state.player = player

    def swap_card(self, deck: str):
        card = self.state.decks[deck].pop(0)
        self.state.decks[deck].append(card)

    def go_to(self, destination: int):
        player = self.state.players[self.state.player]
        player.position = destination

    def go_to_jail(self):
        player = self.state.players[self.state.player]
        player.position = 10
        player.in_jail = 3
        player.doubles = 0

    def collect_card(self, name):
        player = self.state.players[self.state.player]
        deck = self.state.decks[name]
        card, self.state.decks[name] = deck[0], deck[1:]
        player.cards += [card]

    def use_card(self):
        player = self.state.players[self.state.player]
        card = player.cards.pop(0)
        self.state.decks[card['deck']].append(card)

    def leave_jail(self):
        player = self.state.players[self.state.player]
        player.in_jail = 0

    def serve_time(self):
        player = self.state.players[self.state.player]
        if player.in_jail > 0:
            player.in_jail -= 1

    def mortgage_property(self, position: int, amount: int):
        property = self.state.board[position]
        player = self.state.players[property['owner']]
        player.cash += amount
        property['mortgaged'] = True

    def unmortgage_property(self, position: int, repayment: int):
        property = self.state.board[position]
        player = self.state.players[property['owner']]
        player.cash -= repayment
        property['mortgaged'] = False

    def pay_bank(self, amount: int):
        player = self.state.players[self.state.player]
        player.cash -= amount

    def pay_player(self, payee: int, amount: int):
        player = self.state.players[self.state.player]
        payee = self.state.players[payee]
        player.cash -= amount
        payee.cash += amount
    
    def pay_each_player(self, amount: int):
        player = self.state.players[self.state.player]
        player.cash -= amount * (len(self.state.players) - 1)

        for i in range(len(self.state.players)):
            if i == self.state.player:
                continue
            payee = self.state.players[i]
            payee.cash += amount

    def buy_property(self, position: int, price: int):
        player = self.state.players[self.state.player]
        property = self.state.board[position]
        
        player.cash -= price
        property['owner'] = self.state.player


    def auction(self, position):
        self.state.auction = {
            'position': position,
            'auctioneer': self.state.player,
            'bidder': None,
            'amount': 0
        }


    def bid(self, amount):
        player = self.state.player
        self.state.auction = {
            **self.state.auction,
            'bidder': player,
            'amount': amount
        }
