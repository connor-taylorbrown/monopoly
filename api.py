from flask import Flask, render_template
from quotes import FallbackQuoteClient, QuoteClient, QuoteGenerator


def api(client: QuoteClient):
    app = Flask(__name__)
    quotes = QuoteGenerator(FallbackQuoteClient(client))

    @app.get('/')
    def home():
        quote, next = quotes.get(0)
        return render_template('index.html', label=quote.label, text=quote.text, next=next)

    @app.post('/quotes/<id>')
    def get_quote(id):
        quote, next = quotes.get(id)
        return render_template('partials/hello.html', label=quote.label, text=quote.text, next=next)
    
    return app
