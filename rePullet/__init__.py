from flask import Flask
from flask_bootstrap import Bootstrap
from flask_login import LoginManager

from config import Config as c

app = Flask(__name__)
#app.url_map.strict_slashes = False
# app._static_folder = '/static'
app.config['SECRET_KEY'] = c.SECRET_KEY
app.config['GITHUB'] = {
    'consumer_key': c.consumer_key,
    'consumer_secret': c.consumer_secret
}

bootstrap = Bootstrap(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'
login_manager.session_protection = "strong"

from rePullet.logic import views
from rePullet.logic.views import oauth

oauth.init_app(app)
# if __name__ == '__main__':
#     app.run()
