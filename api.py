from functools import wraps
from flask import Flask, redirect, render_template, request, url_for
from monopoly import actions
from monopoly.game import Game
from monopoly.server import GameServer
from monopoly.view import View


def configure_routing(app: Flask, server: GameServer):
    logger = app.logger

    def show_state(func):
        @wraps(func)
        def inner(id, *args, **kwargs):
            game, state = server.get(int(id))
            action = func(game, *args, **kwargs)
            view = View.create(id, state, action)
            return render_template('partials/state.html', **view)
        
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

        actions = game.use_property(int(property))

        view = View.create(id, state, action=actions)
        return render_template('partials/property.html', **view)
    
    @app.post('/<id>/mortgage/<property>')
    def mortgage(id, property):
        id = int(id)
        game, state = server.get(id)

        amount = request.args.get('amount')
        game.mortgage(int(property), int(amount))

        view = View.create(id, state, action=None)
        return render_template('partials/players.html', **view)
    
    @app.post('/<id>/unmortgage/<property>')
    def lift_mortgage(id, property):
        id = int(id)
        game, state = server.get(id)

        amount = request.args.get('amount')
        game.lift_mortgage(int(property), int(amount))

        view = View.create(id, state, action=None)
        return render_template('partials/players.html', **view)
    
    @app.post('/<id>/auction/<property>')
    def auction(id, property):
        id = int(id)
        game, state = server.get(id)

        actions = game.auction(int(property))

        view = View.create(id, state, action=actions)
        return render_template('partials/auction.html', **view)
    
    @app.post('/<id>/bid')
    def bid(id):
        id = int(id)
        game, state = server.get(id)

        price = request.form['price']
        actions = game.bid(int(price))

        view = View.create(id, state, action=actions)
        return render_template('partials/auction.html', **view)
    
    @app.post('/<id>/stay')
    def stay(id):
        id = int(id)
        game, state = server.get(id)

        actions = game.stay()

        view = View.create(id, state, action=actions)
        return render_template('partials/auction.html', **view)
    
    @app.post('/<id>/endAuction')
    @show_state
    def end_auction(game: Game):
        return game.end_auction()

    @app.post('/<id>/roll')
    @show_state
    def roll(game: Game):
        return game.roll()
    
    @app.post('/<id>/passGo/<position>')
    @show_state
    def pass_go(game: Game, position):
        amount = request.args.get('amount')
        return game.pass_go(int(position), int(amount))
    
    @app.post('/<id>/drawCard')
    @show_state
    def draw_card(game: Game):
        return game.draw_card()
    
    @app.post('/<id>/jump/<position>')
    @show_state
    def jump(game: Game, position):
        return game.jump(int(position))
    
    @app.post('/<id>/goTo/<position>')
    @show_state
    def go_to(game: Game, position):
        return game.go_to(int(position))
    
    @app.post('/<id>/buy/<position>')
    @show_state
    def buy(game: Game, position):
        price = request.args.get('price')
        return game.buy_property(int(position), int(price))
    
    @app.post('/<id>/rent/<position>')
    @show_state
    def rent(game: Game, position):
        amount = request.args.get('amount')
        return game.pay_rent(int(position), int(amount))
    
    @app.post('/<id>/pay')
    @show_state
    def pay(game: Game):
        amount = request.args.get('amount')
        return game.pay_bank(int(amount))
    
    @app.post('/<id>/payEachPlayer')
    @show_state
    def pay_each_player(game: Game):
        amount = request.args.get('amount')
        return game.pay_each_player(int(amount))
    
    @app.post('/<id>/collect')
    @show_state
    def collect(game: Game):
        amount = request.args.get('amount')
        return game.pay_bank(-int(amount))
    
    @app.post('/<id>/collectFromEachPlayer')
    @show_state
    def collect_from_each_player(game: Game):
        amount = request.args.get('amount')
        return game.pay_each_player(-int(amount))
    
    @app.post('/<id>/goToJail')
    @show_state
    def go_to_jail(game: Game):
        return game.go_to_jail()
    
    @app.post('/<id>/collectCard')
    @show_state
    def collect_card(game: Game):
        return game.collect_card()
    
    @app.post('/<id>/useCard')
    @show_state
    def use_card(game: Game):
        return game.use_card()
    
    @app.post('/<id>/leaveJail')
    @show_state
    def leave_jail(game: Game):
        position = request.args.get('position')
        if position is not None:
            position = int(position)
        
        amount = request.args.get('amount')
        if amount is not None:
            amount = int(amount)
        
        return game.leave_jail(position, amount)
    
    @app.post('/<id>/serveTime')
    @show_state
    def serve_time(game: Game):
        return game.serve_time()
    
    @app.post('/<id>/endTurn')
    @show_state
    def end_turn(game: Game):
        return game.end_turn()
    
    return app
