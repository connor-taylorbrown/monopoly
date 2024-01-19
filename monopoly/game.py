import random
from monopoly import actions
from monopoly.model import Player, Property, PropertyType
from monopoly.state import GameState, StateUpdater


def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)


def get_player(state) -> Player:
    return state.players[state.player]


def get_property(state, position) -> Property:
    property = state.board[position]
    set = state.sets[property.get('set', 0)]
    return Property(**property, **set)


def can_pass_go(state, destination) -> bool:
    player = get_player(state)
    return 0 <= destination < player.position


def is_full_set_owned(state, property) -> bool:
    return all(member['owner'] == property.owner for member in state.board if member['set'] == property.set)


def count_set_owned(state, property) -> int:
    return sum(1 for member in state.board if member['set'] == property.set and member['owner'] == property.owner)


def is_purchaseable(property) -> bool:
    return PropertyType(property.type) != PropertyType.NONE and property.owner is None


def is_tax(property) -> bool:
    return PropertyType(property.type) == PropertyType.NONE and property.price > 0


def must_leave_jail(player) -> bool:
    return player.in_jail == 1


def find_next(state: GameState, property_type: int) -> int:
    position = get_player(state).position
    for i in range(len(state.board)):
        position = (position + i) % len(state.board)
        if get_property(state, position).type == property_type:
            break

    return position


class Game:
    def __init__(self, state: GameState, updater: StateUpdater):
        self.state = state
        self.updater = updater

    def roll(self):
        self.state.started = True
        
        self.updater.set_roll(roll_dice())

        a, b = self.state.roll
        doubles, total = a == b, a + b

        player = get_player(self.state)
        if doubles and player.doubles == 3:
            return actions.go_to_jail()
        
        destination = (player.position + total) % len(self.state.board)
        if player.in_jail > 0:
            if doubles:
                return actions.leave_jail(destination=destination)
            elif must_leave_jail(player):
                return actions.leave_jail(destination=destination, amount=50)
            else:
                return actions.serve_time()

        return self.jump(destination)
    
    def jump(self, position):
        if can_pass_go(self.state, position):
            return actions.pass_go(position)
        
        return actions.go_to(position)
    
    def go_to_jail(self):
        self.updater.go_to_jail()
        return actions.end_turn()
    
    def collect_card(self):
        position = get_player(self.state).position
        deck = get_property(self.state, position).name
        self.updater.collect_card(deck)
        return actions.end_turn()
    
    def use_card(self):
        self.updater.use_card()
        self.updater.leave_jail()
        return actions.roll()
    
    def serve_time(self):
        self.updater.serve_time()
        return actions.end_turn()
    
    def leave_jail(self, destination: int | None=None, amount: int | None=None):
        if amount is not None:
            self.updater.pay_bank(amount)
        
        self.updater.leave_jail()
        if destination is not None:
            return actions.go_to(destination)
        
        return actions.roll()
    
    def pass_go(self, destination, amount):
        self.updater.pay_bank(-amount)
        return actions.go_to(destination)
    
    def draw_card(self):
        position = get_player(self.state).position
        deck = get_property(self.state, position).name
        card = self.state.decks[deck][0]
        if card['action'] != 'collectCard':
            self.updater.swap_card(deck)
        if card['action'] == 'jump':
            if 'type' in card:
                return {
                    'action': card['action'],
                    'position': find_next(self.state, card['type'])
                }
            if 'offset' in card:
                return {
                    'action': card['action'],
                    'position': get_player(self.state).position + card['offset']
                }
        if card['action'] == 'generalRepairs':
            return actions.end_turn()
        return card
    
    def go_to(self, position):
        player = self.state.player
        self.updater.go_to(position)

        position = get_player(self.state).position
        property = get_property(self.state, position)
        type = PropertyType(property.type)
        if property.name == 'Go To Jail':
            return actions.go_to_jail()
        if property.name in ['Chance', 'Community Chest']:
            return actions.draw_card()
        if is_tax(property):
            return actions.pay(property.price)
        if is_purchaseable(property):
            return actions.buy_property(position)
        if type == PropertyType.NONE or property.mortgaged:
            return actions.end_turn()
        if property.owner in [None, player]:
            return actions.end_turn()
        if type == PropertyType.RESIDENTIAL:
            if property.houses >= 1:
                amount = property.rent[property.houses]
            elif is_full_set_owned(self.state, property):
                amount = 2 * property.rent[0]
            else:
                amount = property.rent[0]
            return actions.pay_rent(position, amount)
        if type == PropertyType.UTILITY:
            roll = sum(self.state.roll)
            if is_full_set_owned(self.state, property):
                amount = 10 * roll
            else:
                amount = 4 * roll
            return actions.pay_rent(position, amount)
        if type == PropertyType.STATION:
            level = count_set_owned(self.state, property) - 1
            return actions.pay_rent(position, property.rent[level])
            
    def pay_bank(self, amount):
        self.updater.pay_bank(amount)
        return actions.end_turn()
    
    def pay_each_player(self, amount):
        self.updater.pay_each_player(amount)
        return actions.end_turn()
    
    def buy_property(self, position):
        self.updater.buy_property(position)
        return actions.end_turn()
    
    def pay_rent(self, position, amount):
        property = get_property(self.state, position)
        self.updater.pay_player(property.owner, amount)
        return actions.end_turn()
    
    def end_turn(self):
        player = get_player(self.state)
        if player.doubles < 1:
            self.updater.next_player()

        next_player = get_player(self.state)
        if next_player.in_jail:
            get_out_of_jail_free = 'collectCard' in [card['action'] for card in next_player.cards]
            return [
                actions.use_card() if get_out_of_jail_free else actions.leave_jail(amount=50),
                actions.roll()
            ]
        
        return actions.roll()
