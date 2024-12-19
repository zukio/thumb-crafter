import os
import sys
import json
import signal
import asyncio
from watchdog.observers import Observer
from modules.filehandler import FileHandler
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
        self.load_config()

        # デフォルトターゲットディレクトリの設定
        if not self.config['target']:
            self.config['target'] = os.path.abspath(
                os.path.join(os.getcwd(), os.pardir))

        # ターゲットディレクトリが存在しない場合は作成
        if not os.path.exists(self.config['target']):
            os.makedirs(self.config['target'])

    def load_config(self):
        config_path = os.path.join(os.path.dirname(__file__), 'config.json')
        default_config = {
            'target': '',
            'exclude_subdirectories': False,
            'protocol': 'none',
            'ip': 'localhost',
            'port': 12345,
            'seconds': 1,
            'delay': 1
        }

        try:
            with open(config_path, 'r') as f:
                self.config = json.load(f)
        except:
            self.config = default_config

    def start(self):
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

            # IPCサーバーの開始
            self.server_task = asyncio.create_task(
                start_server(12321, self.config['target'])
            )

            return True

        except FileNotFoundError:
            print(f"Error: ターゲットディレクトリが見つかりません: {self.config['target']}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False


def main():
    thumb_crafter = ThumbCrafter()
    if thumb_crafter.start():
        tray = TrayIcon(thumb_crafter)
        tray.run()
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
