from dataclasses import dataclass
import random
import requests


@dataclass
class Quote:
    label: int
    text: str


class QuoteClient:
    def __init__(self, port: int):
        self.address = f'http://localhost:{port}'

    def get(self) -> list[Quote]:
        response = requests.get(f'{self.address}/quotes')
        json = response.json()

        return [Quote(label=i + 1, text=q['quote']) for i, q in enumerate(json)]
    

class QuoteGenerator:
    def __init__(self, quotes: list[Quote]):
        self.quotes = quotes

    def get(self, quote: str) -> tuple[Quote, int]:
        quote = int(quote)
        return self.quotes[quote], random.randint(0, len(self.quotes) - 1)
