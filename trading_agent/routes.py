# from flask import Flask, request, session, g, redirect, url_for, abort, render_template, flash
from flask import render_template, flash, redirect, request
from datetime import datetime
from flask_json import FlaskJSON, JsonError, json_response, as_json

from .main import app
from .main import kiwoom_agent

# from .main import qtapp
# from .main import socketio
# from trading_agent.pyqt5.kiwoom_agent import KiwoomAgent
# kiwoom_agent = KiwoomAgent(qtapp=qtapp, flask_app=app, socketio=socketio)


from flask_cors import CORS
CORS(app)

json = FlaskJSON(app)
# app.config['JSON_ADD_STATUS'] = False
app.config['JSON_DATETIME_FORMAT'] = '%d/%m/%Y %H:%M:%S'

@app.route('/')
@app.route('/index')
def index():
    return render_template('index.html')

@app.route('/login', methods=['POST'])
def login():
    ret = kiwoom_agent.login()
    return json_response(connected=ret, status_=202)
    # return render_template('index.html')

@app.route('/poweroff')
def poweroff():
    # socketio.stop()
    kiwoom_agent.poweroff()
    # # return "<h1>Poweroff</h1>"
    return render_template('index.html')

@app.route('/test')
def test():
    res = kiwoom_agent.test()
    # return res
    return render_template('index.html')

@app.route('/get_time')
def get_time():
    now = datetime.utcnow()
    return json_response(time=now)

@app.route('/increment_value', methods=['POST'])
def increment_value():
    # We use 'force' to skip mimetype checking to have shorter curl command.
    data = request.get_json(force=True)
    print(data)
    try:
        value = int(data['value'])
    except (KeyError, TypeError, ValueError):
        raise JsonError(description='Invalid value.')
    return json_response(value=value + 1, status_=202)

@app.route('/get_value')
@as_json
def get_value():
    return dict(value=12)

###########################################################################

from flask_socketio import send, emit
from .main import socketio

@socketio.on('connect')
def connected():
    print("Connected...")
    # emit('SSE', {'connected': 'yep'}, broadcast=True)
    ret = kiwoom_agent.login()
    if ret:
        emit('authentication', {'status': 'logged_in'})
    else:
        emit('authentication', {'status': 'logged_out'})

@socketio.on('disconnect')
def disconnected():
    print("Disonnected...")

@socketio.on('message')
def handle_message(message):
    print('received message: ' + str(message))

@socketio.on('CSE')
def handle_my_custom_event(json):
    print('received CSE: ' + str(json))
    # emit('SSE', json)
