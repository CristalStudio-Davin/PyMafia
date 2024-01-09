import sys
import socket
import threading
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic

startWindowForm = uic.loadUiType("startUI.ui")[0]
messageWindowForm = uic.loadUiType("messageUI.ui")[0]

class StartWindow(QMainWindow, startWindowForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.pushButton.clicked.connect(self.login_button_clicked)
    
    def login_button_clicked(self):
        if not self.lineEdit.text() or not self.lineEdit_2.text() or not self.lineEdit_3.text():
            QMessageBox.information(self, "모든 항목 입력 안됨", "모든 항목이 입력되지 않았습니다.")
        else:
            controller.serverIP = self.lineEdit.text()
            controller.ID = self.lineEdit_2.text()
            controller.port = self.lineEdit_3.text()
            controller.message_page()

class MessageWindow(QMainWindow, messageWindowForm):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup_chat()
        self.pushButton.clicked.connect(self.chat_button_clicked)

    def worker(self, conn):
        while True:
            try:
                getBytes = conn.recv(4)
                lenBytes = int(getBytes.decode())
                gotMessage = conn.recv(lenBytes)
                data = json.loads(gotMessage)

                if "users" in data:
                    self.plainTextEdit_2.setPlainText("")
                    for i in range(0, len(data["users"])):
                        self.plainTextEdit_2.insertPlainText("* %s\n" % data["users"][i])

                message = "[%s] %s" % (data["id"], data["message"])
                self.plainTextEdit.insertPlainText("%s\n" %message)
            except (ValueError,OSError,ConnectionError):
                break

    def setup_chat(self):
        self.clientSocket.connect((controller.serverIP, int(controller.port)))
        th = threading.Thread(target=self.worker, name="[스레드 이름 {}]".format(self.clientSocket), args=(self.clientSocket,))
        th.start()  # 생성한 스레드를 시작한다

        data = dict()
        data["id"] = controller.ID
        data["request"] = "join"
        jsonData = json.dumps(data)
        dataLen = len(jsonData.encode())
        message = str(dataLen).rjust(4, '0') + jsonData
        self.clientSocket.send(message.encode())

        self.label.setText("서버 - %s 아이디 - %s" %(controller.serverIP, controller.ID))


    def chat_button_clicked(self):
        inputMessage = self.lineEdit.text()
        data = dict()
        data["id"] = controller.ID
        data["request"] = "chat"
        data["message"] = inputMessage
        jsonData = json.dumps(data)
        dataLen = len(jsonData.encode())
        message = str(dataLen).rjust(4, '0') + jsonData
        self.clientSocket.send(message.encode())
        self.lineEdit.setText("")

    def closeEvent(self, close):
        offMessageBox = QMessageBox.question(self, "종료 확인", "킴챗을 종료하시겠습니까?", QMessageBox.Yes|QMessageBox.No)

        if offMessageBox == QMessageBox.Yes:
            data = dict()
            data["id"] = controller.ID
            data["request"] = "quit"
            jsonData = json.dumps(data)
            dataLen = len(jsonData.encode())
            message = str(dataLen).rjust(4, '0') + jsonData
            self.clientSocket.send(message.encode())

            # self.clientSocket.close()
            close.accept()
        else:
            close.ignore()

class WindowController:
    def __init__(self):
        self.serverIP = ""
        self.ID = ""
        self.port = ""

    def start_page(self):
        self.startPage = StartWindow()
        self.startPage.show()

    def message_page(self):
        self.messagePage = MessageWindow()
        self.startPage.hide()
        self.messagePage.show()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = WindowController()
    controller.start_page()
    sys.exit(app.exec_())