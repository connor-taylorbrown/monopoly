import json
import logging
from api import configure_routing
from flask import Flask
from google.cloud import storage
from quotes import QuoteClient


class CloudStorageQuoteClient(QuoteClient):
    def __init__(self, bucket_name: str, object_name: str):
        self.bucket_name = bucket_name
        self.object_name = object_name

    def get(self) -> list[dict]:
        client = storage.Client()
        bucket = client.bucket(self.bucket_name)
        blob = bucket.blob(self.object_name)
        quotes = blob.download_as_string()

        return json.loads(quotes)['quotes']


gunicorn_logger = logging.getLogger('gunicorn.error')
config = {
    'bucket_name': 'lboc-quotes',
    'object_name': 'quotes.json'
}
app = Flask(__name__)
app.logger.handlers = gunicorn_logger.handlers
app.logger.setLevel(gunicorn_logger.level)

configure_routing(app, CloudStorageQuoteClient(**config))
