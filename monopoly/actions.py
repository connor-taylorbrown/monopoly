def roll():
    return {
        'action': 'roll'
    }


def go_to_jail():
    return {
        'action': 'goToJail'
    }


def leave_jail(destination: int | None=None, amount: int | None=None):
    return {
        'action': 'leaveJail',
        'position': destination,
        'amount': amount
    }


def use_card():
    return {
        'action': 'useCard'
    }


def serve_time():
    return {
        'action': 'serveTime'
    }


def pass_go(destination: int):
    return {
        'action': 'passGo',
        'position': destination,
        'amount': 200
    }


def draw_card():
    return {
        'action': 'drawCard'
    }


def go_to(destination: int):
    return {
        'action': 'goTo',
        'position': destination
    }


def pay(amount: int):
    return {
        'action': 'pay',
        'amount': amount
    }


def buy_property(property: int, price: int):
    return {
        'action': 'buy',
        'position': property,
        'price': price
    }


def pay_rent(property: int, amount: int):
    return {
        'action': 'rent',
        'position': property,
        'amount': amount
    }


def end_turn():
    return {
        'action': 'endTurn'
    }


def mortgage(position, amount):
    return {
        'action': 'mortgage',
        'position': position,
        'amount': amount
    }


def lift_mortgage(position, amount):
    return {
        'action': 'liftMortgage',
        'position': position,
        'amount': amount
    }


def develop(position, amount):
    return {
        'action': 'develop',
        'position': position,
        'amount': amount
    }


def demolish(position, amount):
    return {
        'action': 'demolish',
        'position': position,
        'amount': amount
    }


def auction(position, interrupt):
    return {
        'action': 'auction',
        'position': position,
        'interrupt': 'interrupt' if interrupt else None
    }


def bid():
    return {
        'action': 'bid'
    }


def stay():
    return {
        'action': 'stay'
    }
