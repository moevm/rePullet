Env setting

<pre>
sudo apt-get install python3 python3-pip
sudo python3-pip install -r requirements.txt
</pre>

Getting GitHub OAuth

- Go to https://github.com/settings/developers and press "Register a new application"
-- Homepage URL = "http://127.0.0.1:20000/"
-- Authorization callback URL = "http://127.0.0.1:20000/login/authorized"
-- Register Application
- Remember "Client ID" and "Client Secret"

Setting up GitHub OAuth. Create file config.py

<pre>
class Config:
  MONGOHOST = 'localhost'
  MONGOPORT = 27017
  MONGONAME = 'pullet'
  SECRET_KEY = 'your key'
  consumer_key = 'Client ID'
  consumer_secret = 'Client Secret'
  scope = {'scope': 'user:email'}
</pre>

Running

<pre>
python3 __init__.py
</pre>

