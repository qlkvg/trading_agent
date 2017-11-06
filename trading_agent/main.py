import sys

from flask import Flask
app = Flask(__name__)

from flask_socketio import SocketIO
socketio = SocketIO(app)
# socketio = SocketIO(app, async_mode='eventlet')

from trading_agent.eventlet_pyqt.hgoldfish.utils import eventlet
from PyQt5.QtWidgets import QApplication
qtapp = QApplication(sys.argv)

from trading_agent.pyqt5.kiwoom_agent import KiwoomAgent
kiwoom_agent = KiwoomAgent(qtapp=qtapp, flask_app=app, socketio=socketio)

from trading_agent import routes

# from PyQt5.QtCore import QThread
# class FlaskThread(QThread):
#     def __init__(self, socketio, flask_app):
#         QThread.__init__(self, objectName='flaskThread')
#         self.socketio = socketio
#         self.flask_app = flask_app
#
#     def __del__(self):
#         self.wait()
#
#     def run(self):
#         # self.flask_app.run(host='0.0.0.0', port=5000)
#         self.socketio.run(self.flask_app, host='0.0.0.0', port=5000)
#
# flask_thread = FlaskThread(socketio=socketio, flask_app=app)
# flask_thread.start()

# sys.exit(qtapp.exec_())

socketio.run(app, host='0.0.0.0', port=5000)
eventlet.start_application()
# sys.exit(qtapp.exec_())
