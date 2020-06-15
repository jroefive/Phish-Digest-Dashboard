"""Core Flask app routes."""
from flask import render_template
from flask import current_app as app



@app.route('/')
def home():
    return render_template('index.jinja2',
                           title='Phish Show Digest Dashboard',
                           template='home-template',
                           body="This is an interactive dashboard that allows you to input any Phish and see graphs of how the songs played in that show compare to all other times that song was played.")
