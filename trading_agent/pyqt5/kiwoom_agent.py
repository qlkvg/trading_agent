
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
    QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot #, QString

from trading_agent.pyqt5.kiwoom_api import KiwoomAPI

class KiwoomAgent(QMainWindow):
    # OnEventConnect = pyqtSignal(int)

    def __init__(self, qtapp, flask_app, socketio):
        super().__init__()


        self.qtapp = qtapp
        # self.flask_app = flask_app
        self.socketio = socketio
        self.initUI()

        self.api = KiwoomAPI(agent=self)

    def initUI(self):
        frame = QWidget(self)
        self.setCentralWidget(frame)
        grid = QGridLayout()
        grid.setSpacing(10)
        frame.setLayout(grid)

        self.statusBar() #.showMessage('Ready')

        self.input_edit = QLineEdit(frame)
        self.debug_list = QListWidget(frame)

        login_btn = QPushButton("로그인", frame)
        current_price_button = QPushButton("종목 현재가", frame)
        test_btn = QPushButton("테스트", frame)
        quit_btn = QPushButton("종료", frame)

        login_btn.clicked.connect(self.login)
        current_price_button.clicked.connect(self.get_current_price)
        test_btn.clicked.connect(self.test)
        quit_btn.clicked.connect(self.quit)

        grid.addWidget(self.input_edit, 2, 0)
        grid.addWidget(self.debug_list, 4, 0, 8, 0)

        grid.addWidget(login_btn, 13, 0)
        grid.addWidget(current_price_button, 14, 0)
        grid.addWidget(test_btn, 15, 0)
        grid.addWidget(quit_btn, 16, 0)

        self.setGeometry(0, 0, 480, 480)  # x, y, w, h
        self.setWindowTitle('Trading Agent for Kiwoom')
        # self.setWindowIcon(QIcon('web.png'))
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.Yes | QMessageBox.No, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def quit(self):
        self.qtapp.quit()

    def poweroff(self):
        self.qtapp.quit()

    def get_platform(self):
        platforms = {
            'linux1' : 'Linux',
            'linux2' : 'Linux',
            'darwin' : 'OS X',
            'win32' : 'Windows'
        }
        if sys.platform not in platforms:
            return sys.platform

        return platforms[sys.platform]

    def test(self):
        pass
        # self.OnEventConnect.emit(1)

    def login(self):
        ret = self.api.commConnect()

    def handleConnect(self, errCode):
        if errCode == 0:  # 0: No Error, others: Error
            state = self.api.getConnectState()
            if state == 1: # 1: 연결 완료, 0: 미연결
                tags = ["ACCNO", "USER_ID", "USER_NAME"]
                results = list(map(lambda tag: self.api.getLoginInfo(tag), tags))
                print('Login Info', results)
                # self.socketio.send()
                self.statusBar().showMessage('Logged in')
                return
                # account_no = self.api.getLoginInfo("ACCNO")
                # user_id = self.api.getLoginInfo("USER_ID")
                # user_name = self.api.getLoginInfo("USER_NAME")
        # self.socketio.send()
        self.statusBar().showMessage('Logged out')

    def get_current_price(self, stock_code):
        val = self.input_edit.text()
        if val != "":
            stock_code = val
        else:
            stock_code = '005930'

        self.api.setInputValue("종목코드", stock_code)

        # rQName = '주식기본정보'.encode('utf-8')
        # trCode = 'opt10001'
        # prevNext = 0
        # screenNo = '0001'
        ret = self.api.commRqData("주식기본정보", "opt10001", 0, "0001");
