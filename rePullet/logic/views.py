from rePullet import app
from flask import render_template

from rePullet.logic.jsongen import *


@app.route('/')
def start_page():
    return render_template('index.html')

@app.route('/g/', methods=['GET', 'POST'])
def go_test():
    return render_template('result.html')

@app.route('/t/')
def go_tl():
    return render_template('testtimeline.html')

@app.route('/api/groups/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/groups/<urluser>/<urlrepo>/<ending>')
def get_groups(urluser,urlrepo,ending):
    return group_gen(urluser,urlrepo)

@app.route('/api/items/<urluser>/<urlrepo>',defaults={'ending': None})
@app.route('/api/items/<urluser>/<urlrepo>/<ending>')
def get_items(urluser,urlrepo,ending):
    return items_gen(urluser,urlrepo)