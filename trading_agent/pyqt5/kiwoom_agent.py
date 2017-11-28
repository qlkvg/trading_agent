
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
    QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot #, QString

from trading_agent.pyqt5.kiwoom_api import KiwoomAPI

# from hgoldfish.utils import eventlet
from trading_agent.eventlet_pyqt.hgoldfish.utils import eventlet

class KiwoomAgent(QMainWindow):
    # OnEventConnect = pyqtSignal(int)

    def __init__(self, qtapp, flask_app, socketio):
        super().__init__()
        self.operations = eventlet.GreenletGroup()

        self.qtapp = qtapp
        self.flask_app = flask_app
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

        # self.input_edit = QLineEdit(frame)
        self.debug_list = QListWidget(frame)

        login_btn = QPushButton("로그인", frame)
        # current_price_button = QPushButton("종목 현재가", frame)
        # test_btn = QPushButton("테스트", frame)
        quit_btn = QPushButton("종료", frame)

        login_btn.clicked.connect(self.login)
        # current_price_button.clicked.connect(self.get_current_price)
        # test_btn.clicked.connect(self.test)
        quit_btn.clicked.connect(self.quit)

        # grid.addWidget(self.input_edit, 2, 0)
        grid.addWidget(self.debug_list, 4, 0, 8, 0)

        grid.addWidget(login_btn, 13, 0)
        # grid.addWidget(current_price_button, 14, 0)
        # grid.addWidget(test_btn, 15, 0)
        grid.addWidget(quit_btn, 16, 0)

        self.setGeometry(0, 0, 480, 480)  # x, y, w, h
        self.setWindowTitle('Trading Agent for Kiwoom')
        # self.setWindowIcon(QIcon('web.png'))
        self.show()

    def closeEvent(self, event):
        reply = QMessageBox.question(self, 'Message', "Are you sure to quit?", QMessageBox.No|QMessageBox.Yes, QMessageBox.Yes)

        if reply == QMessageBox.Yes:
            self.socketio.stop()
            # event.accept()
        else:
            event.ignore()

    def keyPressEvent(self, e):
        if e.key() == Qt.Key_Escape:
            self.close()

    def quit(self):
        self.socketio.stop()
        # self.qtapp.quit()

    def poweroff(self):
        self.socketio.stop()
        # self.qtapp.quit()

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
        print('In test()', self, self.socketio)
        self.socketio.emit('SSE', {'Hello': 'TEST'})
        self.socketio.send('Blah Blah', namespace='/')
        # self.socketio.sleep(0)
        # pass
        # self.OnEventConnect.emit(1)

    def login(self):
        if self.api.getConnectState() == 1:
            # self.socketio.emit('authentication', {'status': 'logged_in'})
            return True
        else:
            ret = self.api.commConnect()
            return False # not connected yet

    def getConnectState(self):
        if self.api.getConnectState() == 1:
            tags = ["ACCNO", "USER_ID", "USER_NAME"]
            results = {tag: self.api.getLoginInfo(tag) for tag in tags}
            self.socketio.emit('basic-info', results)
            return True
        else:
            return False

    def handleConnect(self, errCode):
        if errCode == 0:  # 0: No Error, others: Error
            state = self.api.getConnectState()
            if state == 1: # 1: 연결 완료, 0: 미연결
                self.socketio.emit('authentication', {'status': 'logged_in'})

                tags = ["ACCNO", "USER_ID", "USER_NAME"]
                # results = list(map(lambda tag: self.api.getLoginInfo(tag), tags))
                results = {tag: self.api.getLoginInfo(tag) for tag in tags}
                self.socketio.emit('basic-info', results)
                # print('Login Info', results)
                return

        self.socketio.emit('authentication', {'status': 'logged_out'})
        self.statusBar().showMessage('Logged out')

    def check_balance(self, account_no):
        self.api.setInputValue('계좌번호', account_no)
        self.api.setInputValue('비밀번호', '')
        self.api.setInputValue('상장폐지조회구분', '0')
        self.api.setInputValue('비밀번호입력매체구분', '00')

        ret = self.api.commRqData('계좌평가현황요청', 'opw00004', 0, '0001')
        return ret

    def handleCheckBalance(self, trCode, rQName, scrNo, recordName):
        itemNames = ["예수금", "D+2추정예수금", "유가잔고평가액", "예탁자산평가액", "추정예탁자산", "누적손익율"]
        results = {itemName: self.api.getCommData(trCode, rQName, recordName, itemName) for itemName in itemNames}
        self.socketio.emit('balance-info', results)
        # print('계좌평가현황요청', results)
        self.handleGetAssets(trCode, rQName, scrNo, recordName)

    def get_assets(self, account_no):
        self.api.setInputValue('계좌번호', account_no)
        self.api.setInputValue('비밀번호', '')
        self.api.setInputValue('상장폐지조회구분', '0')
        self.api.setInputValue('비밀번호입력매체구분', '00')

        ret = self.api.commRqData('보유주식요청', 'opw00004', 0, '0001')
        return ret

    def handleGetAssets(self, trCode, rQName, scrNo, recordName):
        itemNames = ["종목코드", "종목명", "보유수량", "평균단가", "현재가"]
        results = []

        cnts = self.api.getRepeatCnt(trCode, rQName)
        for idx in range(0, cnts):
            results.append({itemName: self.api.getCommData(trCode, rQName, idx, itemName) for itemName in itemNames})

        if len(results) > 0:
            self.socketio.emit('assets-info', results)
            # print('보유주식요청', results)

    def get_conditions(self):
        ret = self.api.getConditionLoad()
        return ret

    def handleGetConditionNameList(self):
        conditionList = self.api.getConditionNameList()
        print('조건검색명', conditionList)

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
