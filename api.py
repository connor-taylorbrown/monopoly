from flask import Flask, redirect, render_template, url_for
from monopoly.server import GameServer


def configure_routing(app: Flask, server: GameServer):
    logger = app.logger

    @app.get('/')
    def create():
        game = server.create()
        return redirect(url_for('join', id=game))

    @app.get('/<id>')
    def join(id):
        _, state = server.get(int(id))
        result = {
            'game': id,
            'player': state.player
        }
        return render_template('index.html', **result)

    @app.post('/<id>/roll')
    def roll(id):
        game, state = server.get(int(id))
        game.roll()
        
        player_state = state.players[state.player]
        position_state = state.board[player_state.position]
        result = {
            'last_player': state.player,
            'position': position_state,
            'roll': state.roll,
            'cash': player_state.cash
        }
        game.finalize_turn()

        result = {
            **result,
            'player': state.player
        }
        return render_template('partials/update.html', **result)
    
    return app
