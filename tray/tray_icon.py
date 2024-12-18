import sys
from PyQt5.QtWidgets import QApplication, QSystemTrayIcon, QMenu, QAction
from PyQt5.QtGui import QIcon

class TrayIcon:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.tray_icon = QSystemTrayIcon()
        self.tray_icon.setIcon(QIcon("path/to/icon.png"))  # アイコンのパスを指定
        self.tray_icon.setVisible(True)

        self.menu = QMenu()
        self.create_actions()
        self.tray_icon.setContextMenu(self.menu)

    def create_actions(self):
        exit_action = QAction("Exit", self.app)
        exit_action.triggered.connect(self.exit_app)
        self.menu.addAction(exit_action)

    def exit_app(self):
        self.tray_icon.hide()
        sys.exit()

    def run(self):
        self.app.exec_()

if __name__ == "__main__":
    tray_icon = TrayIcon()
    tray_icon.run()