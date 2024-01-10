import sys
import socket
import threading
import json
from PyQt5.QtWidgets import *
from PyQt5 import uic

startWindow = uic.loadUiType("..\\UI\\ClientStartUI.ui")[0]
mainWindow = uic.loadUiType("..\\UI\\ClientChatUI.ui")[0]


class StartWindow(QMainWindow, startWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.EnterButton.clicked.connect(self.on_room_enter_button_clicked)

    def on_room_enter_button_clicked(self):
        if not self.Server_Address.text() or not self.Server_Port.text() or not self.Nickname.text():
            QMessageBox.information(self, "방 입장 불가능", "방에 입장하기 위한 모든 항목을 입력해야 합니다.")
        else:
            controller.room_address = self.Server_Address.text()
            controller.player_nickname = self.Server_Port.text()
            controller.room_port = self.Nickname.text()
            controller.main_window()


class MessageWindow(QMainWindow, mainWindow):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.setup()
        self.MessageButton.clicked.connect(self.chat_button_clicked)

    def worker(self, conn):
        while True:
            getBytes = conn.recv(4)
            lenBytes = int(getBytes.decode())
            gotMessage = conn.recv(lenBytes)
            data = json.loads(gotMessage)

            if "users" in data:
                self.plainTextEdit_2.setPlainText("")
                for i in range(0, len(data["users"])):
                    self.UserBox.insertPlainText("* %s\n" % data["users"][i])

            message = "[%s] %s" % (data["id"], data["message"])
            self.MessageBox.insertPlainText("%s\n" % message)

    def setup(self):
        self.clientSocket.connect((controller.serverIP, int(controller.port)))
        th = threading.Thread(target=self.worker, name="[스레드 이름 {}]".format(self.clientSocket),
                              args=(self.clientSocket,))
        th.start()

        data = dict()
        data["id"] = controller.ID
        data["request"] = "join"
        jsonData = json.dumps(data)
        dataLen = len(jsonData.encode())
        message = str(dataLen).rjust(4, '0') + jsonData
        self.clientSocket.send(message.encode())
        self.InfoLabel.setText("방의 주소: %s | 닉네임: %s" %(controller.room_address, controller.player_nickname))

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
        offMessageBox = QMessageBox.question(self, "방 퇴장", "방에서 퇴장하고 게임을 종료하시겠습니까?", QMessageBox.Yes | QMessageBox.No)

        if offMessageBox == QMessageBox.Yes:
            data = dict()
            data["id"] = controller.ID
            data["request"] = "quit"
            jsonData = json.dumps(data)
            dataLen = len(jsonData.encode())
            message = str(dataLen).rjust(4, '0') + jsonData
            self.clientSocket.send(message.encode())

            close.accept()
        else:
            close.ignore()


class WindowController:
    def __init__(self):
        self.room_address = ""
        self.player_nickname = ""
        self.room_port = ""

    def start_window(self):
        self.startPage = StartWindow()
        self.startPage.show()

    def main_window(self):
        self.mainPage = MessageWindow()
        self.startPage.hide()
        self.mainPage.show()


if __name__ == '__main__':
    app = QApplication(sys.argv)
    controller = WindowController()
    controller.start_window()
    sys.exit(app.exec_())