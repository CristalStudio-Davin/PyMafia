import sys
from PyQt5.QtWidgets import *
from PyQt5 import uic
from PyQt5.QtCore import *
import socket
import threading
import time
import random
import json
form = uic.loadUiType("create_room.ui")[0]
form2 = uic.loadUiType("server_log.ui")[0]
class GameManager:
    def __init__(self,user):
        self.users=int(user)
        self.jobdict={'mafia':0,'police':1,'medic':2,'person':3}
        self.joblist=[]
        self.usertojob={8:[0,0,1,2,3,3,3,3],9:[0,0,1,2,2,3,3,3,3],10:[0,0,0,1,2,2,3,3,3,3],11:[0,0,0,1,1,2,2,3,3,3,3],12:[0,0,0,1,1,2,2,3,3,3,3,3]}
    def jobsel(self):
        self.joblist=self.usertojob[self.users]
        random.shuffle(self.joblist)
        print(self.joblist)
    def meetingtime(self,second):
        time.sleep(second)
    def nighttime(self,second):
        time.sleep(second)
    def votetime(self,second):
        time.sleep(second)
    def yesornotime(self,second):
        time.sleep(second)

class CreateRoom(QMainWindow, form):
    def __init__(self):
        super().__init__()
        self.setupUi(self)
        self.initUI()
    def initUI(self):
        self.startbtn.clicked.connect(self.inputTest)
    def inputTest(self):
        if self.IPedit.text().strip()=='' or self.PORTedit.text().strip()=='':
            QMessageBox.warning(self, 'NoneTextError', 'IP와 PORT칸을 채워주세요.')
        else:
            ip = self.IPedit.text()
            port = self.PORTedit.text()
            self.logw=logWindow(ip,port)
            self.logw.show()
            self.logw.createsocket()
            self.hide()
class logWindow(QMainWindow, form2):
    def __init__(self,ip,port):
        super().__init__()

        self.setupUi(self)
        self.setWindowFlags(Qt.WindowTitleHint | Qt.WindowMinimizeButtonHint | Qt.WindowMaximizeButtonHint)
        self.messageview.setReadOnly(True)
        self.User.setReadOnly(True)
        self.createw=CreateRoom()
        self.ip=ip
        self.port=port
        self.initUI()
    def initUI(self):
        self.connList = list()
        self.connIDList = list()

    def worker(self, conn):
        while True:
            try:
                Bytes = conn.recv(4)
                bytesLen = int(Bytes.decode())
                data = conn.recv(bytesLen)
                dictData = json.loads(data)

                if not data:
                    break

                if dictData["request"] == "join":
                    self.connIDList.append(dictData["id"])
                    print(self.connList)
                    print(self.connIDList)
                    sendData = dict()
                    sendData["id"] = "System"
                    sendData["request"] = "message"
                    sendData["message"] = "%s님이 서버에 참여하셨습니다!\n" % dictData["id"]
                    sendData["users"] = self.connIDList
                    sendJson = json.dumps(sendData)
                    sendBytesLen = len(sendJson.encode())
                    message = str(sendBytesLen).rjust(4, '0') + sendJson
                    for b in self.connList:
                        b.send(message.encode())
                    self.messageview.insertPlainText("{System} [%s]님이 서버에 참여하셨습니다!\n" % dictData["id"])
                    self.User.setPlainText("")
                    for i in range(0, len(self.connIDList)):
                        self.User.insertPlainText("* %s\n" % self.connIDList[i])
                    # 메세지를 연결된 클라이언트에게 전달

                if dictData["request"] == "chat":
                    for b in self.connList:
                        b.send(Bytes + data)
                    self.messageview.insertPlainText("[%s] %s\n" % (dictData["id"],dictData["message"]))
                    # 메세지를 연결된 클라이언트에게 전달

                if dictData["request"] == "quit":
                    conn.close()
                    self.connIDList.remove(dictData["id"])
                    self.connList.remove(conn)
                    print(self.connList)
                    print(self.connIDList)
                    sendData = dict()
                    sendData["id"] = "System"
                    sendData["request"] = "message"
                    sendData["message"] = "%s님이 서버에서 퇴장하셨습니다!" % dictData["id"]
                    sendData["users"] = self.connIDList
                    sendJson = json.dumps(sendData)
                    sendBytesLen = len(sendJson.encode())
                    message = str(sendBytesLen).rjust(4, '0') + sendJson
                    self.messageview.insertPlainText("{System} [%s]님이 서버에서 퇴장하셨습니다" % dictData["id"])
                    if self.connList:
                        for b in self.connList:
                            b.send(message.encode())
                    self.User.setPlainText("")
                    for i in range(0, len(self.connIDList)):
                        self.User.insertPlainText("* %s\n" % self.connIDList[i])
            except (ConnectionResetError, OSError):
                break
    def createsocket(self):
        try:
            self.s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            self.s.bind((self.ip, int(self.port)))
            self.threadddd()
        except:
            self.hide()
            self.createw.show()
            QMessageBox.warning(self, 'IPandPORTerror', 'IP와 PORT를 다시 입력해 주세요')
    def threadddd(self):
        th = threading.Thread(target=self.run_server)
        th.start()
    def run_server(self):
        try:
            self.s.listen()
            while True:
                self.conn, addr = self.s.accept()  # accept함수의 결과는 튜플형이며, conn은 서버 소켓에 대한 정보, addr은 클라이언트의 정보
                print("서버 소켓정보 : ", self.conn)
                print("연결된 클라이언트 정보 : ", addr)
                self.connList.append(self.conn)
                th2 = threading.Thread(target=self.worker, name="[스레드 이름 {}]".format(self.conn), args=(self.conn,))
                th2.start()
        except Exception as e:
            pass


if __name__ == '__main__':
    app = QApplication(sys.argv)
    window = CreateRoom()
    window.show()
    sys.exit(app.exec_())
