from PyQt5.QtWidgets import QSystemTrayIcon, QMenu, QAction
import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon
from .config_dialog import ConfigDialog


class TrayIcon:
    def __init__(self, thumb_crafter):
        self.thumb_crafter = thumb_crafter
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("./icon.png"))
        self.tray_icon.setVisible(True)

        self.menu = QMenu()
        self.create_actions()
        self.tray_icon.setContextMenu(self.menu)

    def create_actions(self):
        config_action = QAction("Settings")
        config_action.triggered.connect(self.show_config)
        self.menu.addAction(config_action)

        exit_action = QAction("Exit")
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

    def show_config(self):
        dialog = ConfigDialog()
        if dialog.exec_():
            config = dialog.get_config()
            self.thumb_crafter.update_config(config)

    def exit_app(self):
        self.thumb_crafter.stop()
        self.tray_icon.hide()
        sys.exit()

    def run(self):
        self.app.exec_()
