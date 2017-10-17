
import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
    QListWidget
)
from PyQt5.QtCore import Qt, pyqtSignal, pyqtSlot #, QString

if sys.platform == 'win32':
    from PyQt5.QAxContainer import QAxWidget


class KiwoomAgent(QMainWindow):
    OnEventConnect = pyqtSignal(int)

    def __init__(self, qtapp, flask_app, socketio):
        super().__init__()

        if sys.platform == 'win32':
            self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        else:
            self.kiwoom = None

        self.qtapp = qtapp
        self.flask_app = flask_app
        self.socketio = socketio
        self.initUI()

        if self.kiwoom:
            self.kiwoom.OnEventConnect.connect(self._OnEventConnect)
            self.kiwoom.OnReceiveMsg.connect(self._OnReceiveMsg)
            self.kiwoom.OnReceiveTrData.connect(self._OnReceiveTrData)

        self.OnEventConnect.connect(self._OnEventConnect)

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

    def login(self):
        self.debug_list.addItem(">> CommConnect() is called")
        if self.kiwoom:
            ret = self.kiwoom.dynamicCall("CommConnect()")
        else:
            self.OnEventConnect.emit(0)

    def test(self):
        self.OnEventConnect.emit(1)
        # return("<h1>TEST</h1>")

    def quit(self):
        self.qtapp.quit()

    def poweroff(self):
        self.qtapp.quit()

    def get_current_price(self):
        stock_code = self.input_edit.text()
        if stock_code == "":
            stock_code = '039490'
        # print(stock_code)

        self.debug_list.addItem(">> SetInputValue('종목코드', {}) is called".format(stock_code))
        self.debug_list.addItem(">> CommRqData('주식기본정보', 'opt10001', 0, '0001') is called")
        if self.kiwoom:
            self.setInputValue("종목코드", stock_code)
            ret = self.commRqData("주식기본정보", "opt10001", 0, "0001");
            # rQName = '주식기본정보'.encode('utf-8')
            # trCode = 'opt10001'
            # prevNext = 0
            # screenNo = '0001'
            # # self.kiwoom.dynamicCall("CommRqData({},{},{},{})".format(rQName, trCode, prevNext, screenNo))
            # ret = self.kiwoom.dynamicCall("CommRqData(str, str, int, str)", rQName, trCode, prevNext, screenNo)
            # print('commRqData: ', ret)

    def _OnEventConnect(self, errCode):
        self.debug_list.addItem("<< OnEventConnect({}) is received".format(errCode))
        if self.kiwoom:
            if errCode == 0:
                state = self.getConnectState()
                self.debug_list.addItem(">> GetConnectState() is called")
                if state == 1:
                    self.statusBar().showMessage('Logged in')
                    self.debug_list.addItem(">> GetLoginInfo() is called")
                    self.debug_list.addItem(self.getLoginInfo("ACCNO"))
                    # self.debug_list.addItem(self.kiwoom.getLoginInfo("ACCNO").replace(/;$/, "").split(";"))
                    self.debug_list.addItem(self.getLoginInfo("USER_ID"))
                    self.debug_list.addItem(self.getLoginInfo("USER_NAME"))

                else:
                    self.statusBar().showMessage('Logged out')
            else:
                self.statusBar().showMessage('Logged out')
        else:
            self.statusBar().showMessage(str(errCode))

    def _OnReceiveMsg(self, scrNo, rQName, trCode, msg):
        print(scrNo, rQName, trCode, msg)
        self.debug_list.addItem("<< OnReceiveMsg() is received")

    def _OnReceiveTrData(self, scrNo, rQName , trCode, recordName, prevNext, dataLength, errorCode, message, splmMsg):
        len = self.getRepeatCnt(trCode, rQName)
        print("OnReceiveTrData: ", scrNo, rQName, trCode, recordName, len)
        print(self.commGetData(trCode, "", rQName, 0, "종목명"))
        print(self.kiwoom.CommGetData(trCode, "", rQName, 0, "시가총액"))
        print(self.kiwoom.CommGetData(trCode, "", rQName, 0, "거래량"))
        print(self.commGetData(trCode, "", rQName, 0, "현재가"))
        self.debug_list.addItem("<< OnReceiveTrData() is received")

    # @pyqtSlot(result=int)
    def getConnectState(self):
        return self.kiwoom.dynamicCall("GetConnectState()")

    # @pyqtSlot(str,result=str)
    def getLoginInfo(self, tag):
        return self.kiwoom.dynamicCall("GetLoginInfo(str)",[tag])

    # @pyqtSlot(str, str)
    def setInputValue(self, id, value):
        # self.kiwoom.dynamicCall("SetInputValue(str, str)", "종목코드", "039490")
        self.kiwoom.dynamicCall("SetInputValue(str, str)", id, value)

    # @pyqtSlot(str, str, int, str, result=int)
    def commRqData(self, rQName, trCode, prevNext, screenNo):
        return self.kiwoom.dynamicCall("CommRqData(str, str, int, str)", rQName, trCode, prevNext, screenNo)

    # @pyqtSlot(str, str, result=int)
    def getRepeatCnt(self, trCode, recordName):
        # return self.kiwoom.dynamicCall("GetRepeatCnt(str, str)", trCode, recordName)
        return self.kiwoom.dynamicCall("GetRepeatCnt(str, str)", 'opt10001', '주식기본정보')

    # @pyqtSlot(str, str, str, int, str, result=str)
    def commGetData(self, jongmokCode, realType, fieldName, index, innerFieldName):
        # return self.kiwoom.dynamicCall("CommGetData(str, str, str, int, str)", "opt10001", "", "주식기본정보", 0, "종목코드").strip()
        return self.kiwoom.dynamicCall("CommGetData(str, str, str, int, str)", jongmokCode, realType, fieldName, index, innerFieldName).strip()
