import random
from monopoly import actions
from monopoly.model import Auction, Player, Property, PropertyType
from monopoly.state import GameState, StateUpdater


def roll_dice():
    return random.randint(1, 6), random.randint(1, 6)


def get_player(state) -> Player:
    return state.players[state.player]


def get_next_player(state) -> int:
    return (state.player + 1) % len(state.players)


def get_auction(state) -> Auction:
    return Auction(**state.auction)


def get_next_order(auction) -> int:
    return (auction.order + 1) % len(auction.orders)


def get_property(state, position) -> Property:
    property = state.board[position]
    set = state.sets[property.get('set', 0)]
    return Property(**property, **set)


def can_pass_go(state, destination) -> bool:
    player = get_player(state)
    return 0 <= destination < player.position


def property_set(state, position) -> list[Property]:
    property = get_property(state, position)
    properties = (get_property(state, i) for i in range(len(state.board)))
    return (member for member in properties if member.set == property.set)


def is_full_set_owned(state, position, owner):
    return all(member.owner == owner for member in property_set(state, position))


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

    def resume(self):
        return self.updater.resume(actions.end_turn())

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
        return None
    
    def collect_card(self):
        position = get_player(self.state).position
        deck = get_property(self.state, position).name
        self.updater.collect_card(deck)
        return None
    
    def use_card(self):
        self.updater.use_card()
        self.updater.leave_jail()
        return actions.roll()
    
    def serve_time(self):
        self.updater.serve_time()
        return None
    
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
            return None
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
            auction = actions.auction(position, False)
            if get_player(self.state).cash >= property.price:
                return [actions.buy_property(position, property.price), auction]
            else:
                return auction
        if type == PropertyType.NONE or property.mortgaged:
            return None
        if property.owner in [None, player]:
            return None
        if type == PropertyType.RESIDENTIAL:
            if property.houses >= 1:
                amount = property.rent[property.houses]
            elif is_full_set_owned(self.state, position, property.owner):
                amount = 2 * property.rent[0]
            else:
                amount = property.rent[0]
            return actions.pay_rent(position, amount)
        if type == PropertyType.UTILITY:
            roll = sum(self.state.roll)
            if is_full_set_owned(self.state, position, property.owner):
                amount = 10 * roll
            else:
                amount = 4 * roll
            return actions.pay_rent(position, amount)
        if type == PropertyType.STATION:
            level = sum(1 for member in property_set(self.state, position) if member.owner == property.owner) - 1
            return actions.pay_rent(position, property.rent[level])
            
    def pay_bank(self, amount):
        self.updater.pay_bank(amount)
        return None
    
    def pay_each_player(self, amount):
        self.updater.pay_each_player(amount)
        return None
    
    def buy_property(self, position, amount):
        property = get_property(self.state, position)
        if property.owner is None:
            self.updater.pay_bank(amount)
        else:
            self.updater.pay_player(property.owner, amount)
            if property.mortgaged:
                self.updater.encumber(position)
        
        self.updater.acquire_property(position)
        return None
    
    def pay_rent(self, position, amount):
        property = get_property(self.state, position)
        self.updater.pay_player(property.owner, amount)
        return None
    
    def use_property(self, position):
        property = get_property(self.state, position)
        owner = self.state.players[property.owner]

        result = [actions.auction(position, True)]
        if property.mortgaged:
            interest = 1.1 if not property.encumbered else 1.2
            cost = int(interest * property.price / 2)
            if cost > owner.cash:
                return result
            
            return [
                *result,
                actions.lift_mortgage(position, cost)
            ]
        elif property.houses < 1:
            result = [
                *result,
                actions.mortgage(position, property.price // 2)
            ]

        if PropertyType(property.type) == PropertyType.RESIDENTIAL and is_full_set_owned(self.state, position, property.owner):
            can_afford_building = property.building <= owner.cash
            can_build = property.houses < 5
            is_least_built = property.houses == min(property.houses for property in property_set(self.state, position))
            is_mortgage_free = all(not property.mortgaged for property in property_set(self.state, position))
            if can_afford_building and can_build and is_least_built and is_mortgage_free:
                result = [
                    *result,
                    actions.develop(position, property.building)
                ]

            can_demolish = property.houses > 0
            is_most_built = property.houses == max(property.houses for property in property_set(self.state, position))
            if can_demolish and is_most_built:
                result = [
                    *result,
                    actions.demolish(position, property.building // 2)
                ]

        return result
    
    def mortgage(self, position, amount):
        self.updater.mortgage_property(position, amount)

    def lift_mortgage(self, position, amount):
        self.updater.unmortgage_property(position, amount)

    def develop(self, position, amount):
        self.updater.develop(position, amount)

    def demolish(self, position, amount):
        self.updater.demolish(position, amount)
    
    def auction(self, position, interrupt):
        self.updater.save(interrupt)

        property = get_property(self.state, position)
        orders = [
            {'action': 'endAuction', 'article': position, 'value': property.price, 'attendee': i}
            for i, _ in enumerate(self.state.players)
        ]
        self.updater.auction(orders, self.state.player)
        return [actions.bid(), actions.stay()]
    
    def bid(self, amount):
        auction = get_auction(self.state)
        if amount <= auction.amount:
            return [actions.bid(), actions.stay()]
        
        self.updater.bid(amount)

        self.updater.set_order(get_next_order(auction))
        return [actions.bid(), actions.stay()]
    
    def stay(self):
        auction = get_auction(self.state)
        self.updater.set_order(get_next_order(auction))

        player = self.state.player
        last_bidder = auction.bidder
        if player == last_bidder:
            return [auction.orders[auction.order]]

        return [actions.bid(), actions.stay()]
    
    def end_auction(self, position):
        bid = get_auction(self.state).amount
        property = get_property(self.state, position)
        if property.owner == self.state.player:
            return None

        action = actions.buy_property(position, bid)
        if property.mortgaged:
            cost = int(1.1 * property.price // 2)
            buyer = get_player(self.state)
            if buyer.cash >= cost + bid:
                return [action, actions.lift_mortgage(position, cost)]
        
        return action
    
    def end_turn(self):
        player = get_player(self.state)
        if player.doubles < 1:
            self.updater.set_player(get_next_player(self.state))

        next_player = get_player(self.state)
        if next_player.in_jail:
            get_out_of_jail_free = 'collectCard' in [card['action'] for card in next_player.cards]
            return [
                actions.use_card() if get_out_of_jail_free else actions.leave_jail(amount=50),
                actions.roll()
            ]
        
        return actions.roll()
