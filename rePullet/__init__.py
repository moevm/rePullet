from flask import Flask
from flask_bootstrap import Bootstrap
from config import Config as c

app = Flask(__name__)
app.config['SECRET_KEY'] = c.SECRET_KEY
app.config['GITHUB'] = {
    'consumer_key': c.consumer_key,
    'consumer_secret': c.consumer_secret
}

bootstrap = Bootstrap(app)

from rePullet.logic import views
from rePullet.logic.views import oauth

oauth.init_app(app)
# if __name__ == '__main__':
#     app.run()