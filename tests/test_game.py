from unittest.mock import patch

from faker import Faker
from monopoly import actions
from monopoly.game import Game
from monopoly.state import StateUpdater
from tests.utils.serialize import new_player, new_property, new_set, new_state, serialize


@serialize
def state_with_player(board=[], roll=(0,0), position=0, doubles=0, jail_time=0, cash=0):
    return {
        **new_state(),
        'roll': roll,
        'board': board,
        'sets': [new_set(i) for i in range(4)],
        'player': 0,
        'players': [
            player(position, doubles, jail_time, cash)
        ]
    }


@serialize
def state_with_players(board=[], players=[]):
    return {
        **new_state(),
        'board': board,
        'sets': [new_set(0)],
        'player': 0,
        'players': players
    }


@serialize
def player_at_deck(name, deck, board, position=0):
    return {
        **new_state(),
        'player': 0,
        'board': board(name, position),
        'sets': [new_set(i) for i in range(4)],
        'players': [
            {
                **new_player(),
                'position': position
            }
        ],
        'decks': {
            name: deck
        }
    }


@serialize
def player_in_jail_with_card(name, card, deck=[], player=0, doubles=0):
    players = [{
        **new_player(),
        'doubles': doubles,
        'in_jail': 1,
        'cards': [
            {
                'deck': name,
                'action': card
            }
        ]
    } for _ in range(player + 1)]

    return {
        **new_state(),
        'decks': {
            name: deck
        },
        'player': player,
        'players': players
    }


def player(position=0, doubles=0, jail_time=0, cash=0):
    return {
        **new_player(),
        'position': position,
        'doubles': doubles,
        'in_jail': jail_time,
        'cash': cash
    }


def board_with_deck(name, position):
    board = [new_property() for _ in range(40)]
    board[position] = {
        **new_property(),
        'name': name
    }

    return board


def board_with_property(position, price=0, owner=None):
    board = [new_property() for _ in range(40)]
    board[position] = {
        **new_property(),
        'price': price,
        'owner': owner
    }

    return board


def should_go_to_jail():
    return {
        'position': 10,
        'in_jail': 3,
        'doubles': 0
    }


def should_have_time(time):
    return {
        'in_jail': time
    }


def should_have_cash(*amounts):
    return [{
        'cash': amount
    } for amount in amounts]


def should_be_at_position(position):
    return {
        'position': position
    }


def should_update_roll(roll):
    return {
        'started': True,
        'roll': roll
    }


def should_be_at_deck(name, deck):
    return {
        name: deck
    }


def should_collect_card(name, deck):
    return {
        'decks': {
            name: [deck[i] for i in range(1, len(deck))]
        },
        'players': [
            {
                'cards': [deck[0]]
            }
        ]
    }


def should_use_card(name, card, deck):
    return {
        'decks': {
            name: deck + [{
                'action': card,
                'deck': name
            }]
        },
        'players': [
            {
                'in_jail': False,
                'cards': []
            }
        ]
    }


def should_leave_jail_with_cash(cash):
    return {
        'in_jail': 0,
        'cash': cash
    }


def should_buy_property(player, cash):
    return {
        'board': [
            {
                'owner': player
            }
        ],
        'players': [
            {
                'cash': cash
            }
        ]
    }


def should_have_next_player(player):
    return {
        'player': player
    }


def query_player(state, keys):
    player = state.players[state.player]
    return {k: vars(player)[k] for k in keys}


def query_players(state, keys):
    return [
        {k: vars(player)[k] for k in keys}
        for player in state.players
    ]


@patch('monopoly.game.roll_dice')
def test_roll(roll_dice):
    board = [new_property() for _ in range(40)]
    test_cases = [
        (
            state_with_player(doubles=2), (6,6),
            should_update_roll, lambda _: actions.go_to_jail(),
            "Player should go to jail after rolling doubles"
        ),
        (
            state_with_player(board, jail_time=3), (6,6),
            should_update_roll, lambda x: actions.leave_jail(destination=sum(x) % len(board)),
            "Player should get out of jail after rolling doubles"
        ),
        (
            state_with_player(board, jail_time=3), (1,6),
            should_update_roll, lambda _: actions.serve_time(),
            "Player should serve time"
        ),
        (
            state_with_player(board, jail_time=1), (1,6),
            should_update_roll, lambda x: actions.leave_jail(destination=sum(x) % len(board), amount=50),
            "Player should pay to get out of jail"
        ),
        (
            state_with_player(board, position=35), (1,6),
            should_update_roll, lambda x: actions.pass_go(destination=(sum(x) + 35) % len(board)),
            "Player should pass go"
        ),
        (
            state_with_player(board, position=0), (1,6),
            should_update_roll, lambda x: actions.go_to(destination=sum(x) % len(board)),
            "Player should move without passing go"
        )
    ]

    def query(state):
        return {k: vars(state)[k] for k in ['roll', 'started']}

    for state, roll, expectedState, expectedAction, message in test_cases:
        roll_dice.return_value = roll

        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.roll()

        assert query(gotState) == expectedState(roll), message
        assert gotAction == expectedAction(roll), message


def test_jump():
    board = [new_property() for _ in range(40)]
    test_cases = [
        (
            state_with_player(board, position=35), 6,
            lambda x: actions.pass_go(destination=x),
            "Player should pass go"
        ),
        (
            state_with_player(board, position=0), 6,
            lambda x: actions.go_to(destination=x),
            "Player should move without passing go"
        )
    ]

    for state, destination, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        _, gotAction = state, sut.jump(destination)

        assert gotAction == expectedAction(destination), message


def test_go_to_jail():
    test_cases = [
        (
            state_with_player(position=5),
            should_go_to_jail(), actions.end_turn(),
            "Player should go to jail"
        )
    ]

    def query(state):
        player = state.players[state.player]
        return {k: vars(player)[k] for k in ['in_jail', 'position', 'doubles']}
    
    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.go_to_jail()

        assert query(gotState) == expectedState, message
        assert gotAction == expectedAction, message


def test_collect_card():
    name = 'Chance'
    deck = [i for i in range(3)]

    test_cases = [
        (
            player_at_deck(name, deck, board_with_deck),
            should_collect_card(name, deck), actions.end_turn(),
            "Player should collect card"
        )
    ]

    def query(state):
        return {
            'decks': { name: state.decks[name] },
            'players': [
                { 'cards': state.players[state.player].cards }
            ]
        }

    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.collect_card()

        assert query(gotState) == expectedState, message
        assert gotAction == expectedAction, message


def test_use_card():
    name = 'Chance'
    card = 'doesntmatter'
    deck = [i for i in range(3)]

    test_cases = [
        (
            player_in_jail_with_card(name, card, deck),
            should_use_card(name, card, deck), actions.roll(),
            "Player should use card"
        )
    ]

    def query(state):
        player = state.players[state.player]
        return {
            'decks': { name: state.decks[name] },
            'players': [
                {k: vars(player)[k] for k in ['in_jail', 'cards']}
            ]
        }
    
    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.use_card()

        assert query(gotState) == expectedState, message
        assert gotAction == expectedAction, message


def test_serve_time():
    test_cases = [
        (
            state_with_player(jail_time=3),
            should_have_time(time=2), actions.end_turn(),
            "Player should serve time"
        )
    ]

    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.serve_time()

        assert query_player(gotState, ['in_jail']) == expectedState, message
        assert gotAction == expectedAction, message


def test_leave_jail():
    test_cases = [
        (
            state_with_player(jail_time=3, cash=200), None, None,
            should_leave_jail_with_cash(200), lambda _: actions.roll(),
            "Player should get out of jail free"
        ),
        (
            state_with_player(jail_time=3, cash=200), None, 50,
            should_leave_jail_with_cash(150), lambda _: actions.roll(),
            "Player should pay to leave jail"
        ),
        (
            state_with_player(jail_time=3, cash=200), 20, None,
            should_leave_jail_with_cash(200), actions.go_to,
            "Player should get out of jail free and move"
        ),
        (
            state_with_player(jail_time=3, cash=200), 20, 50,
            should_leave_jail_with_cash(150), actions.go_to,
            "Player should pay to leave jail and move"
        )
    ]

    for state, destination, amount, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.leave_jail(destination, amount)

        assert query_player(gotState, ['in_jail', 'cash']) == expectedState, message
        assert gotAction == expectedAction(destination), message


def test_pass_go():
    test_cases = [
        (
            state_with_player(cash=100), 20, 200,
            should_have_cash(300), actions.go_to,
            "Player should pass go and collect 200"
        )
    ]

    for state, destination, amount, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.pass_go(destination, amount)

        assert query_players(gotState, ['cash']) == expectedState, message
        assert gotAction == expectedAction(destination), message


def test_draw_card():
    name = 'Chance'
    deck = [i for i in range(2)]
    collect_card = {'action': 'collectCard'}

    def board_with_utility(utility):
        def inner(name, position):
            board = board_with_deck(name, position)
            board[utility] = {
                **new_property(),
                'set': 2
            }

            return board
        return inner

    def jump_to_offset(offset):
        return {
            'action': 'jump',
            'offset': offset
        }
    
    def jump_to_nearest(type):
        return {
            'action': 'jump',
            'type': type
        }

    def jump_to_position(position):
        return {
            'action': 'jump',
            'position': position
        }

    test_cases = [
        (
            player_at_deck(name, [collect_card] + deck, board_with_deck),
            should_be_at_deck(name, [collect_card] + deck), collect_card,
            "Collect card should not change deck"
        ),
        (
            player_at_deck(name, [jump_to_offset(3)] + deck, board_with_deck, position=5),
            should_be_at_deck(name, deck + [jump_to_offset(3)]), jump_to_position(8),
            "Jump to offset should swap deck and update position"
        ),
        (
            player_at_deck(name, [jump_to_nearest(2)] + deck, board_with_utility(6)),
            should_be_at_deck(name, deck + [jump_to_nearest(2)]), jump_to_position(6),
            "Jump to nearest should swap deck and update position"
        )
    ]

    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.draw_card()

        assert gotState.decks == expectedState, message
        assert gotAction == expectedAction, message


def test_go_to():
    position = 2

    def with_property(name='', set=0, price=0, owner=None, mortgaged=False, houses=0, rent=[], callback=None):
        board = [new_property() for _ in range(40)]
        board[position] = {
            **new_property(),
            'name': name,
            'set': set,
            'price': price,
            'owner': owner,
            'mortgaged': mortgaged,
            'houses': houses,
            'rent': rent
        }

        if callback:
            return callback(board, owner, set)
        return board
    

    def with_partial_set(board, owner, set):
        board[position+1] = {
            **new_property(),
            'owner': owner,
            'set': set
        }

        board[position+2] = {
            **new_property(),
            'owner': owner + 1,
            'set': set
        }

        return board
    

    def with_full_set(board, owner, set):
        board[position+1] = {
            **new_property(),
            'owner': owner,
            'set': set
        }

        return board


    test_cases = [
        (
            state_with_player(board=with_property('Go To Jail')), position,
            should_be_at_position(position), actions.go_to_jail(),
            "Player should go to jail"
        ),
        (
            state_with_player(board=with_property('Community Chest')), position,
            should_be_at_position(position), actions.draw_card(),
            "Player should draw card"
        ),
        (
            state_with_player(board=with_property(set=0, price=200)), position,
            should_be_at_position(position), actions.pay(200),
            "Player should pay tax"
        ),
        (
            state_with_player(board=with_property(set=1, owner=None, price=200), cash=200), position,
            should_be_at_position(position), [actions.buy_property(position, 200), actions.auction(position)],
            "Player should have option to buy property given enough cash"
        ),
        (
            state_with_player(board=with_property(set=1, owner=None, price=200), cash=150), position,
            should_be_at_position(position), actions.auction(position),
            "Player should auction property given insufficient cash"
        ),
        (
            state_with_player(board=with_property(mortgaged=True)), position,
            should_be_at_position(position), actions.end_turn(),
            "Player should not take action on mortgaged property"
        ),
        (
            state_with_player(board=with_property(owner=0)), position,
            should_be_at_position(position), actions.end_turn(),
            "Player should not take action on own property"
        ),
        (
            state_with_player(board=with_property(owner=1, set=1, houses=2, rent=[10, 20, 30])), position,
            should_be_at_position(position), actions.pay_rent(position, 30),
            "Player should pay rent for number of houses"
        ),
        (
            state_with_player(board=with_property(owner=1, set=1, houses=0, rent=[10], callback=with_full_set)), position,
            should_be_at_position(position), actions.pay_rent(position, 20),
            "Player should pay double rent to owner of full set"
        ),
        (
            state_with_player(board=with_property(owner=1, set=1, houses=0, rent=[10], callback=with_partial_set)), position,
            should_be_at_position(position), actions.pay_rent(position, 10),
            "Player should pay base rent to owner of partial set"
        ),
        (
            state_with_player(board=with_property(owner=1, set=2, callback=with_full_set), roll=(1,6)), position,
            should_be_at_position(position), actions.pay_rent(position, 70),
            "Player should pay 10x dice roll to owner of full set of utilities"
        ),
        (
            state_with_player(board=with_property(owner=1, set=2, callback=with_partial_set), roll=(1,6)), position,
            should_be_at_position(position), actions.pay_rent(position, 28),
            "Player should pay 4x dice roll to owner of partial set of utilities"
        ),
        (
            state_with_player(board=with_property(owner=1, set=3, rent=[10, 20, 30], callback=with_partial_set)), position,
            should_be_at_position(position), actions.pay_rent(position, 20),
            "Player should pay rent for number of stations owned"
        )
    ]

    for state, position, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.go_to(position)

        assert query_player(gotState, ['position']) == expectedState, message
        assert gotAction == expectedAction, message


def test_pay_bank():
    test_cases = [
        (
            state_with_player(cash=200), 50,
            should_have_cash(150), actions.end_turn(),
            "Player should pay amount"
        )
    ]

    for state, amount, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.pay_bank(amount)

        assert query_players(gotState, ['cash']) == expectedState, message
        assert gotAction == expectedAction, message


def test_pay_each_player():
    test_cases = [
        (
            state_with_players(players=3 * [player(cash=100)]), 50,
            should_have_cash(0, 150, 150), actions.end_turn(),
            "Player should pay each player amount"
        )
    ]

    for state, amount, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.pay_each_player(amount)

        assert query_players(gotState, ['cash']) == expectedState, message
        assert gotAction == expectedAction, message


def test_buy_property():
    price = 200
    position = 8
    
    test_cases = [
        (
            state_with_player(board=board_with_property(position, price), cash=400), position, price,
            should_buy_property(player=0, cash=200), actions.end_turn(),
            "Player should buy property"
        )
    ]

    def query(state):
        return {
            'board': [
                {k: state.board[position][k] for k in ['owner']}
            ],
            'players': [
                query_player(state, ['cash'])
            ]
        }

    for state, position, price, expectedState, expectedAmount, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.buy_property(position, price)

        assert query(gotState) == expectedState, message
        assert gotAction == expectedAmount, message


def test_pay_rent():
    position = 8
    test_cases = [
        (
            state_with_players(board=board_with_property(position, owner=1), players=2 * [player(cash=100)]), position, 20,
            should_have_cash(80, 120), actions.end_turn(),
            "Player should pay rent to property owner"
        )
    ]

    for state, position, amount, expectedState, expectedAmount, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.pay_rent(position, amount)

        assert query_players(gotState, ['cash']) == expectedState, message
        assert gotAction == expectedAmount, message


def test_end_turn():
    fake = Faker()

    test_cases = [
        (
            state_with_player(doubles=1, jail_time=0),
            should_have_next_player(0), actions.roll(),
            "Player should roll next when rolling doubles"
        ),
        (
            player_in_jail_with_card(fake.pystr(), 'collectCard', doubles=1),
            should_have_next_player(0), [actions.use_card(), actions.roll()],
            "Player should have option to leave jail given card"
        ),
        (
            state_with_player(doubles=1, jail_time=1),
            should_have_next_player(0), [actions.leave_jail(amount=50), actions.roll()],
            "Player should have option to pay to leave jail"
        ),
        (
            state_with_players(players=2 * [player(doubles=0, jail_time=0)]),
            should_have_next_player(1), actions.roll(),
            "New player should roll next when doubles not rolled"
        ),
        (
            player_in_jail_with_card(fake.pystr(), 'collectCard', player=1),
            should_have_next_player(0), [actions.use_card(), actions.roll()],
            "Next player should have option to leave jail given card"
        ),
        (
            state_with_players(players=2 * [player(doubles=0, jail_time=1)]),
            should_have_next_player(1), [actions.leave_jail(amount=50), actions.roll()],
            "Next player should have option to pay to leave jail"
        )
    ]

    def query(state):
        return {k: vars(state)[k] for k in ['player']}

    for state, expectedState, expectedAction, message in test_cases:
        sut = Game(state, StateUpdater(state))

        gotState, gotAction = state, sut.end_turn()

        assert query(gotState) == expectedState, message
        assert gotAction == expectedAction, message
