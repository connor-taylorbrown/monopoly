from api import api
import requests
from quotes import Quote, QuoteClient


class MockClient(QuoteClient):
    def __init__(self, port: int):
        self.address = f'http://localhost:{port}'

    def get(self) -> list[Quote]:
        response = requests.get(f'{self.address}/quotes')
        json = response.json()

        return [Quote(label=i + 1, text=q['quote']) for i, q in enumerate(json)]


def create_app():
    ''' Default factory method for Flask CLI runner '''
    return api(MockClient(3000))
