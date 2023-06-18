import socket
import pickle
from threading import Timer

def send(port, message, server_address='localhost'):
    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        # オブジェクトをバイト列に変換（シリアライズ）します
        data = pickle.dumps(message)
        sock.sendto(data, (server_address, port))
    finally:
        sock.close()

# 最初の更新から指定した遅延時間（ここでは 1 秒）が経過するまで無更新状態が続いた時点で、一度だけUDPが送信されます。
class DelayedUDPSender:
    def __init__(self, delay=1):
        self.delay = delay
        self.timer = None

    def send_message(self, ip, port, message):
        if self.timer is not None:
            self.timer.cancel()

        self.timer = Timer(self.delay, send, [port, message, ip])
        self.timer.start()
