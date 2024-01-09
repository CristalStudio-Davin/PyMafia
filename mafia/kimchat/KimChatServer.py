import socket
import threading
import json

connList = []
connIDList = []

def worker(conn):
    while True:
        try:
            Bytes = conn.recv(4)
            bytesLen = int(Bytes.decode())
            data = conn.recv(bytesLen)
            dictData = json.loads(data)

            if not data:
                break

            if dictData["request"] == "join":
                connIDList.append(dictData["id"])
                print(connList)
                print(connIDList)
                sendData = dict()
                sendData["id"] = "System"
                sendData["request"] = "message"
                sendData["message"] = "%s님이 서버에 참여하셨습니다!" %dictData["id"]
                sendData["users"] = connIDList
                sendJson = json.dumps(sendData)
                sendBytesLen = len(sendJson.encode())
                message = str(sendBytesLen).rjust(4, '0') + sendJson
                print("[System] %s님이 서버에 참여하셨습니다!" %dictData["id"])

                for b in connList:
                    b.send(message.encode())  # 메세지를 연결된 클라이언트에게 전달

            if dictData["request"] == "chat":
                for b in connList:
                    b.send(Bytes + data)  # 메세지를 연결된 클라이언트에게 전달

            if dictData["request"] == "quit":
                conn.close()
                connIDList.remove(dictData["id"])
                connList.remove(conn)
                print(connList)
                print(connIDList)
                sendData = dict()
                sendData["id"] = "System"
                sendData["request"] = "message"
                sendData["message"] = "%s님이 서버에서 퇴장하셨습니다!" % dictData["id"]
                sendData["users"] = connIDList
                sendJson = json.dumps(sendData)
                sendBytesLen = len(sendJson.encode())
                message = str(sendBytesLen).rjust(4, '0') + sendJson
                print("[System]%s님이 서버에서 퇴장하셨습니다!" % dictData["id"])

                if connList:
                    for b in connList:
                        b.send(message.encode())  # 메세지를 연결된 클라이언트에게 전달
        except (ConnectionResetError, OSError):
            break

def run_server(port=4000):
    host = ''
    # socket.AF_INET 은 IP4v 주소체계(socket.AF_INET6 은 IP6v), socket.SOCK_STREAM은 소켓의 타입
    # socket.AF_INET와 socket.SOCK_STREAM은 디폴트 값이므로 socket.socket() 로 코드를 작성해도 된다.
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((host, port))
        s.listen()

        while True:
            conn, addr = s.accept()  # accept함수의 결과는 튜플형이며, conn은 서버 소켓에 대한 정보, addr은 클라이언트의 정보
            connList.append(conn)
            th = threading.Thread(target=worker, name="[스레드 이름 {}]".format(conn), args=(conn,))
            th.start()  # 생성한 스레드를 시작한다


if __name__ == '__main__':
    run_server()