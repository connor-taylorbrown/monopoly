from flask import Flask, redirect, render_template, url_for
from monopoly.server import GameServer
from monopoly.state import GameState


def show_player(state: GameState):
    player = state.players[state.player]
    return {
        'id': state.player,
        **vars(player)
    }


def show_position(state: GameState):
    player = state.players[state.player]
    return state.board[player.position]


def do_roll():
    return {
        'id': 'roll',
        'text': 'Roll'
    }


def do_update():
    return {
        'id': 'update',
        'text': 'Update'
    }


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
        result = {
            'game': id,
            'state': state,
            'player': show_player(state),
            'action': do_roll()
        }
        return render_template('index.html', **result)

    @app.post('/<id>/roll')
    def roll(id):
        game, state = server.get(int(id))
        
        game.roll()
        result = {
            'game': id,
            'state': state,
            'player': show_player(state),
            'position': show_position(state),
            'action': do_update()
        }
        
        return render_template('partials/roll.html', **result)
    
    @app.post('/<id>/update')
    def take_action(id):
        game, state = server.get(int(id))

        game.apply_turn()
        result = {
            'game': id,
            'state': state,
            'last_player': show_player(state),
            'position': show_position(state)
        }

        game.finalize_turn()
        result = {
            **result,
            'player': show_player(state),
            'action': do_roll()
        }

        return render_template('partials/update.html', **result)

    
    return app
