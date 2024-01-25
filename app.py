from api import configure_routing
from flask import Flask

from monopoly.server import Board, GameServer


def create_app():
    ''' Default factory method for Flask CLI runner '''
    app = Flask(__name__)
    board = Board(3000)
    server = GameServer(board)
    return configure_routing(app, server)
