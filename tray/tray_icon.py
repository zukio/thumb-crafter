import os
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction, QDialog
from PyQt5.QtGui import QCursor, QIcon
from .config_dialog import ConfigDialog
from modules.config_manager import ConfigManager


class TrayIcon:
    def __init__(self, thumb_crafter):
        print("Initializing TrayIcon")
        self.thumb_crafter = thumb_crafter
        self.tray_icon = QSystemTrayIcon()
        icon_path = os.path.abspath("tray/icon.png")
        self.tray_icon.setIcon(QIcon(icon_path))
        self.tray_icon.setVisible(True)

        # メニューの作成
        self.menu = QMenu()
        self.create_actions()
        self.tray_icon.setContextMenu(self.menu)

        # クリックイベントの設定
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()

    def create_actions(self):
        config_action = QAction("Settings", self.menu)  # 親として self.menu を渡す
        config_action.triggered.connect(self.show_config)
        self.menu.addAction(config_action)

        exit_action = QAction("Exit", self.menu)  # 親として self.menu を渡す
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.Trigger:  # 左クリック
            self.menu.exec_(QCursor.pos())  # マウスの現在位置にコンテキストメニューを表示

    def show_config(self):
        print("Settings clicked")
        self.dialog = ConfigDialog(
            self.thumb_crafter.config)  # 現在のパスを渡してダイアログを初期化
        # モーダル表示
        if self.dialog.exec_():  # OKボタンが押された場合
            config = self.dialog.get_config()
            self.thumb_crafter.config_manager.update_config(
                config)  # 設定を更新
            self.thumb_crafter.config = config  # ローカルの設定も更新
            print("Config updated:", self.thumb_crafter.config)
            self.thumb_crafter.restart()  # 再起動して設定を反映
        else:  # Cancelボタンが押された場合
            print("Dialog cancelled")

    def exit_app(self):
        print("exit_app called")
        self.thumb_crafter.stop()
        self.tray_icon.hide()
        QCoreApplication.quit()
