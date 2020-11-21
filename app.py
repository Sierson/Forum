from flask import Flask, render_template, redirect, request, url_for, session
import mysql.connector
from werkzeug.security import generate_password_hash, check_password_hash
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)


def get_current_user():
    user_results = None
    if 'user' in session:
        user = session['user']

        db = get_db()
        curr_user = db.cursor(dictionary=True)
        curr_user.execute('SELECT id, login, password FROM users WHERE login = %s', (user, ))
        user_results = curr_user.fetchone()

    return user_results

def get_db():
    my_db = None
    my_db = mysql.connector.connect(
        host = "localhost",
        user = "root",
        passwd = "passwd",
        database = "social",
    )
    return my_db



@app.route('/')
def index():
    user = get_current_user()
    return render_template('index.html', user=user)

@app.route('/login', methods=['GET', 'POST'])
def login():
    user = get_current_user()
    db = get_db()
    if request.method == 'POST':

        login = request.form['login']
        password = request.form['password']

        curr = db.cursor(dictionary=True)
        curr.execute('SELECT * FROM users WHERE login = %s', (login, ))
        user_results = curr.fetchone()
        if user_results:
            if check_password_hash(user_results['password'], password):
                session['user'] = user_results['login']
                return redirect(url_for('index'))
            else: 
                passwd_error = "Password is incorrect"
                return render_template('login.html', error=passwd_error, user=user)
        else:
            login_error = "Login is incorrect"
            return render_template('login.html', error=login_error, user=user)

    return render_template('login.html', user=user)

@app.route('/register', methods=['GET', 'POST'])
def register():
    user = get_current_user()
    db = get_db()
    curr = db.cursor()
    if request.method == 'POST':
        login = request.form['login']
        password = generate_password_hash(request.form['password'], method='sha256')

        curr.execute("INSERT INTO users (login, password) VALUES (%s, %s)", (login, password, ))
        db.commit()
        return redirect(url_for('index'))
    return render_template('register.html', user=user)

@app.route('/entry')
def entry():
    user = get_current_user()
    db = get_db()
    curr = db.cursor(dictionary=True)
    curr.execute('SELECT posts.user_id, posts.title, posts.content, users.login from posts INNER JOIN users ON posts.user_id = users.id ORDER BY posts.id DESC')
    entries = curr.fetchall()
    return render_template('entry.html', user=user, entries=entries)

@app.route('/add-entry', methods=['GET', 'POST'])
def add_entry():
    user = get_current_user()
    db = get_db()
    curr = db.cursor(dictionary=True)
    if request.method == 'POST':
        curr.execute('INSERT INTO posts (user_id, title, content) VALUES (%s, %s, %s)', (user['id'], request.form['title'], request.form['content_entry']))
        db.commit()
    return render_template('add_entry.html', user=user)

@app.route('/my-entry', methods=['GET', 'POST'])
def my_entry():
    user = get_current_user()
    db = get_db()
    curr = db.cursor(dictionary=True)
    curr.execute('SELECT posts.user_id, posts.title, posts.content, users.login from posts INNER JOIN users ON posts.user_id = users.id WHERE posts.user_id = %s ORDER BY posts.id DESC', (user['id'], ))
    my_entries = curr.fetchall()
    return render_template('my_entry.html', user=user, entries=my_entries)

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))
if __name__ == '__main__':
    app.run(debug=True)