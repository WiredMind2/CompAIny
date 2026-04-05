from flask import Flask

app = Flask(__name__)
app.config['SECRET_KEY'] = 'compainy-secret-key'

from . import routes