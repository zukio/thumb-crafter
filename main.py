import os
import sys
import json
import signal
import asyncio
from PyQt5.QtWidgets import QApplication
from PyQt5.QtCore import QTimer
from watchdog.observers import Observer
from modules.filehandler import FileHandler
from modules.config_manager import ConfigManager
from utils.communication.udp_client import DelayedUDPSender as DelayedUDPSenderUDP, hello_server as hello_server_udp
from utils.communication.tcp_client import DelayedTCPSender as DelayedTCPSenderTCP, hello_server as hello_server_tcp
from utils.communication.ipc_client import check_existing_instance
from utils.communication.ipc_server import start_server
from tray.tray_icon import TrayIcon


class ThumbCrafter:
    def __init__(self):
        self.observer = None
        self.event_handler = None
        self.server_task = None
        self.sender = None
        self.loop = None
        self.config_manager = ConfigManager()
        self.config = self.config_manager.load_config()

        # デフォルトターゲットディレクトリの設定
        if not self.config['target']:
            self.config['target'] = os.path.abspath(
                os.path.join(os.getcwd(), os.pardir))

        # ターゲットディレクトリが存在しない場合は作成
        if not os.path.exists(self.config['target']):
            os.makedirs(self.config['target'])

    async def start(self):
        try:
            if check_existing_instance(12321, self.config['target']):
                print("既に起動しています。")
                return False

            # 通信プロトコルの設定
            if self.config['protocol'] == 'udp':
                self.sender = DelayedUDPSenderUDP(self.config['delay'])
                hello_server = hello_server_udp
            elif self.config['protocol'] == 'tcp':
                self.sender = DelayedTCPSenderTCP(self.config['delay'])
                hello_server = hello_server_tcp
            else:
                self.sender = None
                def hello_server(x): return None

            # FileHandlerの初期化
            self.event_handler = FileHandler(
                self.config['exclude_subdirectories'],
                self.sender,
                self.config['ip'],
                self.config['port'],
                self.config['seconds']
            )

            # サーバー通信の開始
            if self.sender:
                response = hello_server(self.config['target'])
                if response == "overlapping":
                    return False

            # オブザーバーの開始
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.config['target'],
                recursive=not self.config['exclude_subdirectories']
            )
            self.observer.start()

            # IPCサーバーの開始（非同期タスクとして起動し、バックグラウンドで実行）
            self.server_task = asyncio.create_task(
                start_server(12321, self.config['target']))

            return True

        except FileNotFoundError:
            print(f"Error: ターゲットディレクトリが見つかりません: {self.config['target']}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def stop(self):
        if self.observer:
            self.observer.stop()
            self.observer.join()
        if self.event_handler:
            self.event_handler.destroy("[Exit] Normal")
        if self.server_task:
            self.server_task.cancel()

    def restart(self):
        self.stop()
        self.start()


def exit_handler(reason, thumb_crafter):
    thumb_crafter.stop()
    sys.exit(reason)


def main():
    app = QApplication(sys.argv)
    thumb_crafter = ThumbCrafter()

    # シグナルハンドラの設定
    signal.signal(signal.SIGINT, lambda sig, frame: exit_handler(
        "[Exit] Signal Interrupt", thumb_crafter))

    try:
        if asyncio.run(thumb_crafter.start()):
            tray = TrayIcon(thumb_crafter)
            # PyQtのイベントループを使用
            timer = QTimer()
            timer.timeout.connect(lambda: None)  # キープアライブタイマー
            timer.start(100)
            app.exec_()
        else:
            sys.exit(1)
    except KeyboardInterrupt:
        exit_handler("[Exit] Keyboard Interrupt", thumb_crafter)


if __name__ == "__main__":
    main()
