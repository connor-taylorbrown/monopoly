from flask import Flask, render_template
from quotes import FallbackQuoteClient, QuoteClient, QuoteGenerator


app = Flask(__name__)
client = QuoteClient(port=3000)

try:
    quotes = client.get()
except Exception:
    client = FallbackQuoteClient()
    quotes = client.get()

@app.get('/')
def home():
    generator = QuoteGenerator(quotes)
    quote, next = generator.get(0)
    return render_template('index.html', label=quote.label, text=quote.text, next=next)

@app.post('/quotes/<id>')
def get_quote(id):
    generator = QuoteGenerator(quotes)
    quote, next = generator.get(id)
    return render_template('partials/hello.html', label=quote.label, text=quote.text, next=next)
