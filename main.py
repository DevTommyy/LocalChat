from flask import Flask, render_template, request, redirect, session, jsonify
from flask_socketio import SocketIO, emit
import sqlite3

import re
from uuid import uuid4

app = Flask(__name__, static_folder="./html_assets", template_folder="./html_templates")
app.config['SECRET_KEY'] = 'secret'
socketio = SocketIO(app)

# Create SQLite database for user authentication
conn = sqlite3.connect('users.db')
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS users
             (username text, password text)''')
conn.commit()
conn.close()

""" 
***************
ROUTES CREATION
***************
"""
# Home page
@app.route('/')
def home():
    return render_template('home.html')

@app.route('/signup')
def signup():
    return render_template('signup.html')

# Chatroom page
@app.route('/chatroom')
def chatroom():
    return render_template('chatroom.html')

@app.route('/get_unique_id')
def get_unique_id():
    username = session.get('username')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT id FROM users WHERE username=?", (username,))
    unique_id : str = str(c.fetchone()[0])[:8]

    return jsonify({'unique_id': unique_id})

""" 
*************
FORM HANDLING
*************
"""    
# Login page
@app.route('/login', methods=['POST'])
def login():
    username = request.form['username']
    password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users WHERE username=? AND password=?", (username, password))
    user = c.fetchone()
    if user:
        # User is authenticated, redirect to chatroom page
        session["username"] = username
        id : str = user[0][:8]

        return redirect(f'chatroom?id={id}')

    else:
        # Authentication failed, show error message
        return render_template('home.html', error='Invalid username or password')

# Sign up page
@app.route('/addToTable', methods=['POST'])
def addToTable():
    username = request.form['username']
    password = request.form['password']

    if not re.match("^(?=.*[a-z])(?=.*\d)[a-zA-Z\d]{6,30}$", password):
        return render_template('signup.html', error='Invalid password')

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Controlla se l'utente esiste già nella tabella
    c.execute("SELECT * FROM users WHERE username=?", (username, ))
    user = c.fetchone()

    if user:
        conn.close()
        return render_template('signup.html', error='Username already exist')

    else:
        id = str(uuid4())
        c.execute("INSERT INTO users (id, username, password) VALUES (?, ?, ?)", (id, username, password))
        conn.commit()
        conn.close()

        return render_template('home.html', msg='Sign up successsful')

""" 
**************
EVENT HANDLING
**************
"""
# Chatroom event handlers
connected_clients = 0

@socketio.on('connect')
def handle_connect():
    if session.get("username"):
        global connected_clients
        connected_clients += 1
        emit('message', f'{session.get("username")} connected', broadcast=True)
    else:
        emit('redir', 'MUST LOGIN')

@socketio.on('disconnect')
def handle_disconnect():
    global connected_clients
    connected_clients -= 1
    if connected_clients == 0:
        emit('clear', broadcast=True)
    else:
        emit('message', f'{session.get("username")} disconnected', broadcast=True)

@socketio.on('message')
def handle_message(message):
    if message == "":
        emit('emptyMessage')
    else: 
        message = f'{session["username"]}: {message}'
        emit('message', message, broadcast=True)

@socketio.on('setUsername')
def handle_setUsername(id):
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    c.execute("SELECT * FROM users")
    users = c.fetchall()
    
    for user in users:
        if str(user[0][:8]) == id:
            session["username"] = user[1]

    handle_connect()

# Run the app
if __name__ == '__main__':
    socketio.run(app, host="0.0.0.0", port="8000", debug=True) #run this for non local, only same network
    # socketio.run(app, debug=True) #run this for testing