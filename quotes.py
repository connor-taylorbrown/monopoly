from abc import ABC, abstractmethod
from dataclasses import dataclass
from functools import cache
from logging import Logger
import random


@dataclass
class Quote:
    label: int
    text: str


class QuoteClient(ABC):
    @abstractmethod
    def get(self) -> list[dict]:
        pass


class FallbackQuoteClient:
    def __init__(self, client: QuoteClient, logger: Logger):
        self.client = client
        self.logger = logger

    @cache
    def get(self) -> list[dict]:
        try:
            return self.client.get()
        except Exception:
            self.logger.exception("Error reading from database")
            return [
                {"label": "Wisdom #1", "text": "I said maybe..."},
                {"label": "Wisdom #2", "text": "You're gonna be the one that saves me..."}
            ]
    

class QuoteGenerator:
    def __init__(self, client: QuoteClient):
        self.client = client

    def get(self, id: str) -> tuple[Quote, int]:
        id = int(id)
        quotes = self.client.get()
        quote = Quote(**quotes[id])
        return quote, random.randint(0, len(quotes) - 1)
