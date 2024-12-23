import os
import sys
import asyncio
import logging
from utils.logwriter import setup_logging
from PyQt5.QtWidgets import QApplication, QMessageBox
from PyQt5.QtCore import QTimer
from watchdog.observers import Observer
from modules.filehandler import FileHandler
from modules.config_manager import ConfigManager
from utils.communication.udp_client import DelayedUDPSender as DelayedUDPSenderUDP, hello_server as hello_server_udp
from utils.communication.tcp_client import DelayedTCPSender as DelayedTCPSenderTCP, hello_server as hello_server_tcp
from utils.communication.ipc_client import check_existing_instance
from utils.communication.ipc_server import start_server
from utils.multiple_pid import block_global_instance
from tray.tray_icon import TrayIcon

setup_logging()


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
            if self.config.get('single_instance_only', True):  # 重複起動を禁止
                if block_global_instance(self):
                    self.show_error_dialog(
                        "シングル起動モードです",
                        None,
                        2000,
                        exit_handler
                    )
                    return False

            if check_existing_instance(12321, self.config['target']):
                self.show_error_dialog(
                    "既に同じターゲットで動作中です",
                    None,
                    2000,
                    exit_handler
                )
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
            self.show_error_dialog(
                "見つかりません",
                f"{self.config['target']}",
                2000,
                exit_handler
            )
            print(f"Error: ターゲットディレクトリが見つかりません: {self.config['target']}")
            return False
        except Exception as e:
            print(f"Error: {str(e)}")
            return False

    def show_error_dialog(self, message, details=None, timeout=2000, exit_handler=None):
        """エラーダイアログを表示"""
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Warning)  # エラーアイコン
        msg.setWindowTitle("エラー")
        msg.setText(message)
        if details:
            msg.setInformativeText(details)  # 詳細な説明

        msg.setStandardButtons(QMessageBox.Ok)

        # ダイアログが閉じられたときにexit_handlerを呼び出す
        if exit_handler:
            msg.finished.connect(lambda: exit_handler(message, self))

        # タイマーで自動閉じを設定
        QTimer.singleShot(timeout, msg.close)
        msg.exec_()

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
                exit_handler("start() returned False", thumb_crafter)
    except KeyboardInterrupt:
        exit_handler("[Exit] Keyboard Interrupt", thumb_crafter)


if __name__ == "__main__":
    main()
