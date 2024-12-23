import os
import sys
import asyncio
from PyQt5.QtWidgets import QApplication, QWidget
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
        self.tray = None  # TrayIconを初期化して保持
        try:
            # JSON設定のロード
            self.config_manager = ConfigManager()
            json_config = self.config_manager.load_config()
            # CLI引数の解析とマージ
            cli_args = self.config_manager.parse_arguments()
            self.config = self.config_manager.merge_config(
                json_config, cli_args)
        except Exception as e:
            print(f"Error during initialization: {e}")
            self.config = {}

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
            if self.config['protocol'] == 'udp' or (self.config['protocol'] is None and self.config.get('ip')):
                self.sender = DelayedUDPSenderUDP(self.config['send_interval'])
                hello_server = hello_server_udp
            elif self.config['protocol'] == 'tcp':
                self.sender = DelayedTCPSenderTCP(self.config['send_interval'])
                hello_server = hello_server_tcp
            else:
                self.sender = None
                def hello_server(x): return None

            # FileHandlerの初期化
            self.event_handler = FileHandler(
                self.sender,
                self.config['ignore_subfolders'],
                self.config['ip'],
                self.config['port'],
                self.config['thumbnail_time_seconds'],
                self.config['convert_slide'],
                self.config['convert_document'],
                self.config['page_duration']
            )

            # サーバー通信の開始
            if self.sender:
                response = hello_server(self.config['target'])
                if response == "overlapping":
                    return False

            # 初期ファイル処理
            print(f"Initializing file handler for directory: {
                self.config['target']}")
            await self.event_handler.list_files(self.config['target'])

            # オブザーバーの開始
            self.observer = Observer()
            self.observer.schedule(
                self.event_handler,
                self.config['target'],
                recursive=not self.config['ignore_subfolders']
            )
            print(f"Starting observer on directory: {self.config['target']}")
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
        asyncio.run(self.start())


def exit_handler(reason, thumb_crafter):
    thumb_crafter.stop()
    if thumb_crafter.tray:
        thumb_crafter.tray.tray_icon.hide()
    sys.exit(reason)


def main():
    app = QApplication(sys.argv)
    app.setQuitOnLastWindowClosed(False)

    # 設定をThumbCrafterに適用
    thumb_crafter = ThumbCrafter()

    thumb_crafter = ThumbCrafter()
    thumb_crafter.tray = TrayIcon(thumb_crafter)  # TrayIconを保持

    try:
        while True:
            if asyncio.run(thumb_crafter.start()):
                print("Tray icon initialized")
                timer = QTimer()
                timer.timeout.connect(lambda: None)  # キープアライブ用タイマー
                timer.start(100)
                exit_code = app.exec_()  # イベントループ開始
                print(f"Main event loop exited with code: {exit_code}")

                if exit_code == 0:  # 通常終了時
                    break
                else:  # 再起動
                    print("Restarting event loop...")
                    thumb_crafter.tray.tray_icon.show()
            else:
                sys.exit(1)
    except KeyboardInterrupt:
        exit_handler("[Exit] Keyboard Interrupt", thumb_crafter)


if __name__ == "__main__":
    main()
