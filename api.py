from flask import Flask, redirect, render_template, request, url_for
from monopoly import actions
from monopoly.server import GameServer
from monopoly.view import View


def configure_routing(app: Flask, server: GameServer):
    logger = app.logger

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

    @app.post('/<id>/roll')
    def roll(id):
        game, state = server.get(int(id))
        action = game.roll()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/passGo/<position>')
    def pass_go(id, position):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pass_go(int(position), int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/drawCard')
    def draw_card(id):
        game, state = server.get(int(id))
        action = game.draw_card()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/jump/<position>')
    def jump(id, position):
        game, state = server.get(int(id))
        action = game.jump(int(position))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/goTo/<position>')
    def go_to(id, position):
        game, state = server.get(int(id))
        action = game.go_to(int(position))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/buy/<position>')
    def buy(id, position):
        game, state = server.get(int(id))
        action = game.buy_property(int(position))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/rent/<position>')
    def rent(id, position):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pay_rent(int(position), int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/pay')
    def pay(id):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pay_bank(int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/payEachPlayer')
    def pay_each_player(id):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pay_each_player(int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/collect')
    def collect(id):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pay_bank(-int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/collectFromEachPlayer')
    def collect_from_each_player(id):
        game, state = server.get(int(id))
        amount = request.args.get('amount')
        action = game.pay_each_player(-int(amount))

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/goToJail')
    def go_to_jail(id):
        game, state = server.get(int(id))
        action = game.go_to_jail()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/collectCard')
    def collect_card(id):
        game, state = server.get(int(id))
        action = game.collect_card()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/useCard')
    def use_card(id):
        game, state = server.get(int(id))
        action = game.use_card()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/leaveJail')
    def leave_jail(id):
        game, state = server.get(int(id))
        position = request.args.get('position')
        if position is not None:
            position = int(position)
        amount = request.args.get('amount')
        if amount is not None:
            amount = int(amount)
        action = game.leave_jail(position, amount)

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/serveTime')
    def serve_time(id):
        game, state = server.get(int(id))
        action = game.serve_time()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    @app.post('/<id>/endTurn')
    def end_turn(id):
        game, state = server.get(int(id))
        action = game.end_turn()

        view = View.create(id, state, action)
        return render_template('partials/state.html', **view)
    
    return app
