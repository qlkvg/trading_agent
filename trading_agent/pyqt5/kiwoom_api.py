import sys
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QMessageBox,
    QGridLayout, QPushButton, QLabel, QLineEdit, QTextEdit,
    QListWidget
)
from PyQt5.QtCore import Qt, QObject, pyqtSignal, pyqtSlot #, QString


class KiwoomAPI(QObject):
    OnEventConnectSignal = pyqtSignal(int)

    def __init__(self, agent):
        super().__init__()

        self.agent = agent

        if sys.platform == 'win32':
            from PyQt5.QAxContainer import QAxWidget
            self.kiwoom = QAxWidget("KHOPENAPI.KHOpenAPICtrl.1")
        else:
            self.kiwoom = None

        if self.kiwoom:
            self.kiwoom.OnEventConnect.connect(self.OnEventConnect)
            self.kiwoom.OnReceiveMsg.connect(self.OnReceiveMsg)
            self.kiwoom.OnReceiveTrData.connect(self.OnReceiveTrData)
            self.kiwoom.OnReceiveConditionVer.connect(self.OnReceiveConditionVer)
        else:
            self.OnEventConnectSignal.connect(self.OnEventConnect)

    ############################################################################

    def OnEventConnect(self, errCode):
        self.agent.debug_list.addItem("<< OnEventConnect({}) is received".format(errCode))
        self.agent.handleConnect(errCode)

    def OnReceiveMsg(self, scrNo, rQName, trCode, msg):
        self.agent.debug_list.addItem("<< OnReceiveMsg({},{},{},{}) is received".format(scrNo, rQName, trCode, msg))

    def OnReceiveTrData(self, scrNo, rQName , trCode, recordName, prevNext, dataLength, errorCode, message, splmMsg):
        self.agent.debug_list.addItem("<< OnReceiveTrData() is received")
        # print("OnReceiveTrData: ", scrNo, rQName , trCode, recordName, prevNext, dataLength, errorCode, message, splmMsg)

        if (trCode == 'opw00004' and rQName == '계좌평가현황요청'):
            self.agent.handleCheckBalance(trCode, rQName, scrNo, recordName)
        elif (trCode == 'opw00004' and rQName == '보유주식요청'):
            self.agent.handleGetAssets(trCode, rQName, scrNo, recordName)

    def OnReceiveConditionVer(self, ret, msg):
        self.agent.debug_list.addItem("<< OnReceiveConditionVer() is received")
        if(ret): # 성공
            self.agent.handleGetConditionNameList()


    ############################################################################

    def commConnect(self):
        self.agent.debug_list.addItem(">> CommConnect() is called")
        if self.kiwoom:
            ret = self.kiwoom.dynamicCall("CommConnect()")
        else:
            self.OnEventConnectSignal.emit(0)  # 0: login, 1: lotout

    # @pyqtSlot(result=int)
    def getConnectState(self):
        self.agent.debug_list.addItem(">> GetConnectState() is called")
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetConnectState()")
        else:
            return 1 # 1: connected, others: not connected

    # @pyqtSlot(str,result=str)
    def getLoginInfo(self, tag):
        self.agent.debug_list.addItem(">> GetLoginInfo({}) is called".format(tag))
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetLoginInfo(str)",[tag])
        else:
            return tag

    # @pyqtSlot(str, str)
    def setInputValue(self, id, value):
        self.agent.debug_list.addItem(">> SetInputValue('{}', {}) is called".format(id, value))
        if self.kiwoom:
            self.kiwoom.dynamicCall("SetInputValue(str, str)", id, value)

    # @pyqtSlot(str, str, int, str, result=int)
    def commRqData(self, rQName, trCode, prevNext, screenNo):
        self.agent.debug_list.addItem(">> CommRqData('{}', '{}', {}, '{}') is called".format(rQName, trCode, prevNext, screenNo))
        if self.kiwoom:
            return self.kiwoom.dynamicCall("CommRqData(str, str, int, str)", rQName, trCode, prevNext, screenNo)

    # @pyqtSlot(str, str, result=int)
    def getRepeatCnt(self, trCode, recordName):
        self.agent.debug_list.addItem(">> GetRepeatCnt('{}', '{}') is called".format(trCode, recordName))
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetRepeatCnt(str, str)", trCode, recordName)
            # return self.kiwoom.dynamicCall("GetRepeatCnt(str, str)", 'opt10001', '주식기본정보')

    # commGetData() 사용 중지 => getCommData() 사용할 것
    # @pyqtSlot(str, str, str, int, str, result=str)
    # def commGetData(self, jongmokCode, realType, fieldName, index, innerFieldName):
    #     self.agent.debug_list.addItem(">> CommGetData('{}', '{}', '{}', {}, '{}') is called".format(jongmokCode, realType, fieldName, index, innerFieldName))
    #     if self.kiwoom:
    #         return self.kiwoom.dynamicCall("CommGetData(str, str, str, int, str)", jongmokCode, realType, fieldName, index, innerFieldName).strip()
    #         # return self.kiwoom.dynamicCall("CommGetData(str, str, str, int, str)", "opt10001", "", "주식기본정보", 0, "종목코드").strip()

    def getCommData(self, trCode, recordName, index, itemName):
        self.agent.debug_list.addItem(">> GetCommData('{}', '{}', '{}', {}) is called".format(trCode, recordName, index, itemName))
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetCommData(str, str, int, str)", trCode, recordName, index, itemName).strip()

    def getConditionLoad(self):
        self.agent.debug_list.addItem(">> getConditionLoad() is called")
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetConditionLoad()")

    def getConditionNameList(self):
        self.agent.debug_list.addItem(">> getConditionNameList() is called")
        if self.kiwoom:
            return self.kiwoom.dynamicCall("GetConditionNameList()")
