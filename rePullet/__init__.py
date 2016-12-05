from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config as c

app = Flask(__name__)
app.config['SECRET_KEY']= c.SECRET_KEY

bootstrap = Bootstrap(app)

from rePullet.logic import views

