from functools import wraps
from flask import Flask, redirect, render_template, request, url_for
from monopoly import actions
from monopoly.game import Game
from monopoly.server import GameServer
from monopoly.view import View


def configure_routing(app: Flask, server: GameServer):
    logger = app.logger

    def update_state(func):
        @wraps(func)
        def inner(id, *args, **kwargs):
            game, state = server.get(int(id))
            action = func(game, *args, **kwargs)

            state.action = action if action else game.resume()
            view = View.create(id, state, state.action)
            return render_template('partials/state.html', **view)
        
        return inner
    
    def update_property(func):
        @wraps(func)
        def inner(id, property, *args, **kwargs):
            game, state = server.get(int(id))

            func(game, property, *args, **kwargs)

            view = View.create(id, state, action=None)
            return render_template('partials/view/players.html', **view)
        
        return inner
    
    def update_auction(func):
        @wraps(func)
        def inner(id, *args, **kwargs):
            game, state = server.get(int(id))

            actions = func(game, *args, **kwargs)

            view = View.create(id, state, action=actions)
            return render_template('partials/auction.html', **view)
        
        return inner

    @app.get('/')
    def create():
        game = server.create()
        return redirect(url_for('join', id=game))

    @app.get('/<id>')
    def join(id):
        id = int(id)
        if not server.exists(id):
            return redirect(url_for('create'))
        
        _, state = server.get(id)

        view = View.create(id, state, action=actions.roll())
        return render_template('index.html', **view)
    
    @app.get('/<id>/properties/<property>')
    def get_property(id, property):
        id = int(id)
        game, state = server.get(id)

        property_actions = game.use_property(int(property))

        view = View.create(id, state, action=None)
        return render_template('partials/property.html', property_actions=property_actions, **view)
    
    @app.post('/<id>/mortgage/<property>')
    @update_property
    def mortgage(game: Game, property):
        amount = request.args.get('amount')
        game.mortgage(int(property), int(amount))
    
    @app.post('/<id>/unmortgage/<property>')
    @update_property
    def lift_mortgage(game: Game, property):
        amount = request.args.get('amount')
        game.lift_mortgage(int(property), int(amount))
    
    @app.post('/<id>/auction/<property>')
    @update_auction
    def auction(game: Game, property):
        return game.auction(int(property))
    
    @app.post('/<id>/bid')
    @update_auction
    def bid(game: Game):
        price = request.form['price']
        return game.bid(int(price))
    
    @app.post('/<id>/stay')
    @update_auction
    def stay(game: Game):
        return game.stay()
    
    @app.post('/<id>/endAuction')
    @update_state
    def end_auction(game: Game):
        return game.end_auction()

    @app.post('/<id>/roll')
    @update_state
    def roll(game: Game):
        return game.roll()
    
    @app.post('/<id>/passGo/<position>')
    @update_state
    def pass_go(game: Game, position):
        amount = request.args.get('amount')
        return game.pass_go(int(position), int(amount))
    
    @app.post('/<id>/drawCard')
    @update_state
    def draw_card(game: Game):
        return game.draw_card()
    
    @app.post('/<id>/jump/<position>')
    @update_state
    def jump(game: Game, position):
        return game.jump(int(position))
    
    @app.post('/<id>/goTo/<position>')
    @update_state
    def go_to(game: Game, position):
        return game.go_to(int(position))
    
    @app.post('/<id>/buy/<position>')
    @update_state
    def buy(game: Game, position):
        price = request.args.get('price')
        return game.buy_property(int(position), int(price))
    
    @app.post('/<id>/rent/<position>')
    @update_state
    def rent(game: Game, position):
        amount = request.args.get('amount')
        return game.pay_rent(int(position), int(amount))
    
    @app.post('/<id>/pay')
    @update_state
    def pay(game: Game):
        amount = request.args.get('amount')
        return game.pay_bank(int(amount))
    
    @app.post('/<id>/payEachPlayer')
    @update_state
    def pay_each_player(game: Game):
        amount = request.args.get('amount')
        return game.pay_each_player(int(amount))
    
    @app.post('/<id>/collect')
    @update_state
    def collect(game: Game):
        amount = request.args.get('amount')
        return game.pay_bank(-int(amount))
    
    @app.post('/<id>/collectFromEachPlayer')
    @update_state
    def collect_from_each_player(game: Game):
        amount = request.args.get('amount')
        return game.pay_each_player(-int(amount))
    
    @app.post('/<id>/goToJail')
    @update_state
    def go_to_jail(game: Game):
        return game.go_to_jail()
    
    @app.post('/<id>/collectCard')
    @update_state
    def collect_card(game: Game):
        return game.collect_card()
    
    @app.post('/<id>/useCard')
    @update_state
    def use_card(game: Game):
        return game.use_card()
    
    @app.post('/<id>/leaveJail')
    @update_state
    def leave_jail(game: Game):
        position = request.args.get('position')
        if position is not None:
            position = int(position)
        
        amount = request.args.get('amount')
        if amount is not None:
            amount = int(amount)
        
        return game.leave_jail(position, amount)
    
    @app.post('/<id>/serveTime')
    @update_state
    def serve_time(game: Game):
        return game.serve_time()
    
    @app.post('/<id>/endTurn')
    @update_state
    def end_turn(game: Game):
        return game.end_turn()
    
    return app
