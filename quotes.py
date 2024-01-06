from abc import ABC, abstractmethod
from dataclasses import dataclass
import random


@dataclass
class Quote:
    label: int
    text: str


class QuoteClient(ABC):
    @abstractmethod
    def get(self) -> list[Quote]:
        pass
    

class FallbackQuoteClient:
    def __init__(self, client: QuoteClient):
        self.client = client

    def get(self) -> list[Quote]:
        try:
            return self.client.get()
        except Exception:
            return [
                Quote(label=1, text="I said maybe..."),
                Quote(label=2, text="You're gonna be the one that saves me...")
            ]
    

class QuoteGenerator:
    def __init__(self, client: QuoteClient):
        self.quotes = client.get()

    def get(self, quote: str) -> tuple[Quote, int]:
        quote = int(quote)
        return self.quotes[quote], random.randint(0, len(self.quotes) - 1)
