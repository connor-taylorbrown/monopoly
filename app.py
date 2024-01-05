from flask import Flask, render_template
from quotes import QuoteClient, QuoteGenerator


app = Flask(__name__)
client = QuoteClient(port=3000)
quotes = QuoteGenerator(client.get())

@app.get('/')
def home():
    quote, next = quotes.get(0)
    return render_template('index.html', label=quote.label, text=quote.text, next=next)

@app.post('/quotes/<id>')
def get_quote(id: str):
    quote, next = quotes.get(id)
    return render_template('partials/hello.html', label=quote.label, text=quote.text, next=next)
