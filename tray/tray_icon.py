import os
from PyQt5.QtCore import QCoreApplication
from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QCursor, QIcon
from .config_dialog import ConfigDialog
from modules.config_manager import ConfigManager


class TrayIcon:
    def __init__(self, thumb_crafter):
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
        dialog = ConfigDialog()
        if dialog.exec_():
            config = dialog.get_config()
            self.thumb_crafter.config_manager.update_config(config)
            print("Config updated:", self.thumb_crafter.config)

    def exit_app(self):
        self.thumb_crafter.stop()
        self.tray_icon.hide()
        QCoreApplication.quit()

    def run(self):
        # self.app.exec_() # QApplication の初期化は main.py で行う
        self.tray_icon.show()
