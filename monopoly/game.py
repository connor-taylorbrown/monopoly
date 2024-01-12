import random
from monopoly import actions
from monopoly.model import Player, Property, PropertyType
from monopoly.state import GameState, StateUpdater


def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)


def get_player(state) -> Player:
    return state.players[state.player]


def get_property(state) -> Property:
    player = get_player(state)
    return state.board[player.position]


def can_pass_go(state, destination) -> bool:
    player = get_player(state)
    return 0 <= destination < player.position


def is_full_set_owned(property) -> bool:
    return all(member.owner == property.owner for member in property.set.members)


def is_purchaseable(property) -> bool:
    return property.set.type != PropertyType.NONE and property.owner is None


def is_tax(property) -> bool:
    return property.set.type == PropertyType.NONE and property.price > 0


def must_leave_jail(player) -> bool:
    return player.in_jail == 1


def find_next(state: GameState, property_type: PropertyType) -> int:
    player = get_player(state)
    position = player.position
    while state.board[position].set.type != property_type:
        position = (position + 1) % len(state.board)

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
        if doubles and player.doubles == 2:
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
        deck = get_property(self.state).name
        self.updater.collect_card(self.state.decks[deck])
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
        deck = get_property(self.state).name
        card = self.state.decks[deck][0]
        if card['action'] != 'collectCard':
            self.updater.swap_card(deck)
        if card['action'] == 'jump':
            if 'type' in card:
                card['position'] = find_next(self.state, PropertyType(card['type']))
            if 'offset' in card:
                card['position'] = get_player(self.state).position - card['offset']
            return card
        if card['action'] == 'generalRepairs':
            return actions.end_turn()
        return card
    
    def go_to(self, position):
        player = self.state.player
        self.updater.go_to(position)

        property = get_property(self.state)
        if property.name == 'Go To Jail':
            return actions.go_to_jail()
        if property.name in ['Chance', 'Community Chest']:
            return actions.draw_card()
        if is_tax(property):
            return actions.pay(property.price)
        if is_purchaseable(property):
            return actions.buy_property(position)
        if property.set.type == PropertyType.NONE or property.mortgaged:
            return actions.end_turn()
        if property.owner in [None, player]:
            return actions.end_turn()
        if property.set.type == PropertyType.RESIDENTIAL:
            if property.houses >= 1:
                amount = property.rent[property.houses]
            elif is_full_set_owned(property):
                amount = 2 * property.rent[0]
            else:
                amount = property.rent[0]
            return actions.pay_rent(position, amount)
        if property.set.type == PropertyType.UTILITY:
            roll = sum(self.state.roll)
            if is_full_set_owned(property):
                amount = 10 * roll
            else:
                amount = 4 * roll
            return actions.pay_rent(position, amount)
        if property.set.type == PropertyType.STATION:
            level = sum(1 for member in property.set.members if member.owner == property.owner) - 1
            return actions.pay_rent(position, property.rent[level])
            
    def pay_bank(self, amount):
        self.updater.pay_bank(amount)
        return actions.end_turn()
    
    def pay_each_player(self, amount):
        self.updater.pay_each_player(amount)
        return actions.end_turn()
    
    def buy_property(self, position):
        property = self.state.board[position]
        self.updater.buy_property(property)
        return actions.end_turn()
    
    def pay_rent(self, position, amount):
        property = self.state.board[position]
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
