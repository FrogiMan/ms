from email import message
import sys
import json
import sqlite3
import os
from flask import Flask, render_template, request, flash, g
from flask_flatpages import FlatPages, pygments_style_defs
from flask_frozen import Freezer
from FDataBase import FDataBase
import pathlib


script_path = pathlib.Path(sys.argv[0]).parent  # абсолютный путь до каталога, где лежит скрипт
conn = sqlite3.connect(script_path / "mysites.db")  # формируем абсолютный путь до файла базы
DATABASE = '/mysites.db'
DEBUG = False
SECRET_KEY = 'dfgdgergerikjgbnkljghbnmh'
FLATPAGES_AUTO_RELOAD = DEBUG
FLATPAGES_EXTENSION = '.md'
FLATPAGES_ROOT = 'content'
POST_DIR = 'posts'
PORT_DIR = 'portfolio'
app = Flask(__name__)
flatpages = FlatPages(app)
freezer = Freezer(app)
app.config.from_object(__name__)
app.config.update(dict(DATABASE=os.path.join(app.root_path, 'mysites.db')))

def connect_db():
    coon = sqlite3.connect(app.config['DATABASE'])
    coon.row_factory = sqlite3.Row
    return coon

def create_db():
    '''Функция для создания БД'''
    db = connect_db()
    with app.open_resource('sql_db.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()
    db.close()


    @app.teardown_appcontext
    def close_db(error):
        '''Закрытие соединения с БД, если оно было установленно'''
        if hasattr(g, 'link_db'):

            g.link_db.close()



def get_db():
    ''' Соединение с БД '''
    if not hasattr(g, 'link_db'):
        g.link_db = connect_db()
    return g.link_db
    pass


@app.route("/")
def index():
    posts = [p for p in flatpages if p.path.startswith(POST_DIR)]
    posts.sort(key=lambda item: item['date'], reverse=True)
    cards = [p for p in flatpages if p.path.startswith(PORT_DIR)]
    cards.sort(key=lambda item: item['title'])
    with open('settings.txt', encoding='utf8') as config:
        data = config.read()
        settings = json.loads(data)
    tags = set()
    for p in flatpages:
        t = p.meta.get('tag')
        if t:
            tags.add(t.lower())
    return render_template('index.html', posts=posts, cards=cards, bigheader=True, **settings, tags=tags)

@app.route('/admin')
def login():
    username = request.form.get('username')
    password = request.form.get('password')
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
    if username == 'admin' and password == '1234':
        return render_template("login.html")

    return render_template("admin.html", message=message)

@app.route("/login")
def delPost():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('login.html', posts=dbase.delPost())

@app.route("/login", methods=["POST", "GET"])
def log():
    db = get_db()
    dbase = FDataBase(db)
    return render_template('login.html', posts=dbase.getPostsAnonce())

@app.route("/contactsdb", methods=["POST", "GET"])
def addPost():
    with open('settings.txt', encoding='utf8') as config:
        data = config.read()
        settings = json.loads(data)
    tags = set()
    for p in flatpages:
        t = p.meta.get('tag')
        if t:
            tags.add(t.lower())
    db = get_db()
    dbase = FDataBase(db)
    if request.method == 'POST':
        if len(request.form['name']) > 2 and len(request.form['post']) > 2 and len(request.form['message']) > 2:
            res = dbase.addPost(request.form['name'], request.form['email'], request.form['post'],
                                request.form['message'])
            if not res:
                flash('  Ошибка добавления', category='error')
            else:

                flash('', category='success')
        else:
            flash('  Ошибка добавления', category='error')

    return render_template('contactsdb.html', bigheader=True, **settings, tags=tags)



@app.route('/posts/<name>/')
def post(name):
    path = '{}/{}'.format(POST_DIR, name)
    post = flatpages.get_or_404(path)
    return render_template('post.html', post=post)

@app.route('/portfolio/<name>/')
def card(name):
    path = '{}/{}'.format(PORT_DIR, name)
    card = flatpages.get_or_404(path)
    return render_template('card.html', card=card)

@app.route('/pygments.css')
def pygments_css():
    return pygments_style_defs('monokai'), 200, {'Content-Type': 'text/css'}

@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

if __name__ == "__main__":
    # db = connect_db()
    create_db()
    if len(sys.argv) > 1 and sys.argv[1] == "build":
        freezer.freeze()
    else:
        app.run(host='127.0.0.1', port=5000, debug=False)
