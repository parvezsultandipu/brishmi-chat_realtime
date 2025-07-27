from flask import Flask, render_template, request, session, redirect, url_for
from flask_socketio import SocketIO, join_room, leave_room, send
from datetime import datetime
import json

app = Flask(__name__)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app)

chat_log = "chat_history.json"

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        username = request.form['username']
        room = request.form['room']
        session['username'] = username
        session['room'] = room
        return redirect(url_for('chat'))
    return render_template('login.html')

@app.route('/chat')
def chat():
    if 'username' not in session:
        return redirect(url_for('index'))
    return render_template('chat.html', username=session['username'], room=session['room'])

@socketio.on('join')
def handle_join(data):
    join_room(data['room'])
    send({'msg': f"{data['username']} has joined the room."}, room=data['room'])

@socketio.on('message')
def handle_message(data):
    time = datetime.now().strftime('%H:%M')
    msg_data = {
        'msg': f"[{time}] {data['username']}: {data['msg']}",
        'room': data['room']
    }
    send(msg_data, room=data['room'])

    try:
        with open(chat_log, 'r', encoding='utf-8') as f:
            history = json.load(f)
    except FileNotFoundError:
        history = []

    history.append(msg_data)
    with open(chat_log, 'w', encoding='utf-8') as f:
        json.dump(history, f, ensure_ascii=False, indent=2)

if __name__ == '__main__':
    socketio.run(app, debug=True)
