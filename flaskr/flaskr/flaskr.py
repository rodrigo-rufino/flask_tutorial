import os
import sqlite3
from flask import Flask, request, session, g, redirect, url_for, abort, \
     render_template, flash


app = Flask(__name__)  # create the application instance :)
app.config.from_object(__name__)  # load config from this file , flaskr.py
# Load default config and override config from an environment variable
app.config.update(dict(
    DATABASE=os.path.join(app.root_path, 'flaskr.db'),
    SECRET_KEY='development key',
    USERNAME='admin',
    PASSWORD='default'
))
app.config.from_envvar('FLASKR_SETTINGS', silent=True)


def init_db():
    db = get_db()
    with app.open_resource('schema.sql', mode='r') as f:
        db.cursor().executescript(f.read())
    db.commit()


@app.cli.command('initdb')
def initdb_command():
    """Initializes the database."""
    init_db()
    print('Initialized the database.')


def get_db():
    """Opens a new database connection if there is none yet for the
    current application context.
    """
    if not hasattr(g, 'sqlite_db'):
        g.sqlite_db = connect_db()
    return g.sqlite_db


def connect_db():
    """Connects to the specific database."""
    rv = sqlite3.connect(app.config['DATABASE'])
    rv.row_factory = sqlite3.Row
    return rv


@app.teardown_appcontext
def close_db(error):
    """Closes the database again at the end of the request."""
    if hasattr(g, 'sqlite_db'):
        g.sqlite_db.close()


@app.route('/')
def show_entries():
    db = get_db()
    cur = db.execute('select title, text from entries order by id desc')
    entries = cur.fetchall()
    return render_template('index.html', entries=entries)


@app.route('/add', methods=['POST'])
def add_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('insert into entries (title, text) values (?, ?)',
               [request.form['title'], request.form['text']])
    db.commit()
    flash('New entry was successfully posted')
    return redirect(url_for('show_entries'))


@app.route('/signin', methods=['GET', 'POST'])
def sign_in():
    error = None
    render_template('sign_in.html', error=error)
    print request.method

    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        db = get_db()
        db.execute('insert into users (username, password) values (?, ?)',
                   [username, password])
        db.commit()
        return redirect(url_for('show_entries'))
    return render_template('index.html', entries=entries)


@app.route('/remove', methods=['POST'])
def remove_entry():
    if not session.get('logged_in'):
        abort(401)
    db = get_db()
    db.execute('delete from entries where title=? ',
               [request.form['title']])
    db.commit()
    flash('New entry was successfully removed')
    return redirect(url_for('show_entries'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    error = None
    if request.method == 'POST':
        db = get_db()
        username = request.form['username']
        password = request.form['password']
        cur = db.execute('select * from users where username = (?) \
                                                and password = (?)',
                         (username, password))
        try:
            userdata = cur.fetchall()
            user = userdata[0][1]
            psswrd = userdata[0][2]
        except IndexError:
            error = 'Invalid username and password'
            return render_template('login.html', error=error)

        if request.form['username'] != user:
            error = 'Invalid username'
        elif request.form['password'] != psswrd:
            error = 'Invalid password'
        else:
            session['logged_in'] = True
            flash('You were logged in')
            return redirect(url_for('show_entries'))
    return render_template('login.html', error=error)


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    flash('You were logged out')
    return redirect(url_for('show_entries'))


if __name__ == '__main__':
    app.run(host='0.0.0.0',
            port=5555,
            debug=True)
