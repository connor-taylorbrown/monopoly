import random
from monopoly.model import Player, Property, PropertyType
from monopoly.state import GameState, StateUpdater


def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)


def get_player(state) -> Player:
    return state.players[state.player]


def get_position(state, player) -> Property:
    return state.board[player.position]


def is_full_set_owned(property) -> bool:
    return all(member.owner == property.owner for member in property.set.members)


def get_rent(property, roll) -> int:    
    if property.set.type == PropertyType.NONE or property.mortgaged:
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
        roll = sum(roll)
        if is_full_set_owned(property):
            return 10 * roll
        else:
            return 4 * roll
    elif property.set.type == PropertyType.STATION:
        level = sum(1 for member in property.set if member.owner == property.owner) - 1
        return property.rent[level]
    

def is_purchaseable(property) -> bool:
    return property.set.type != PropertyType.NONE and property.owner is None


def is_tax(property) -> bool:
    return property.set.type == PropertyType.NONE and property.price > 0


def must_leave_jail(player) -> bool:
    return player.in_jail == 1


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

        player = get_player(self.state)
        if doubles and player.doubles == 2:
            return self.updater.go_to_jail()
        
        destination = (player.position + total) % len(self.state.board)

        if player.in_jail > 0:
            if doubles:
                return self.updater.leave_jail(destination)
            elif must_leave_jail(player):
                self.updater.pay_bank(50)
                return self.updater.leave_jail(destination)
            else:
                return self.updater.serve_time()
        
        return self.updater.go_to(destination, doubles)
    
    def apply_turn(self):
        player = get_player(self.state)
        position = get_position(self.state, player)

        if position.name == 'Go To Jail':
            return self.updater.go_to_jail()
        if is_tax(position):
            return self.updater.pay_bank(position.price)
        if is_purchaseable(position):
            return self.updater.buy_property(position)
        if position.owner not in [None, player]:
            rent = get_rent(position, self.state.roll)
            return self.updater.pay_players([position.owner], rent)
    
    def finalize_turn(self):
        player = get_player(self.state)
        if player.doubles < 1:
            self.updater.next_player()
