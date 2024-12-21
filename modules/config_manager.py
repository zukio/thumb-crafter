from PyQt5.QtWidgets import QMessageBox
import os
import json


class ConfigManager:
    def __init__(self, app_name="thumb-crafter"):
        self.app_name = app_name
        self.default_config = {
            'target': '',
            'exclude_subdirectories': False,
            'protocol': 'none',
            'ip': 'localhost',
            'port': 12345,
            'seconds': 1,
            'send_interval': 1
        }
        self.config = {}
        self.config_path = os.path.join(os.path.dirname(
            os.path.dirname(__file__)), 'config.json')

    def load_config(self):
        if not os.path.exists(self.config_path):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("見つかりません")
            msg.setInformativeText("設定ファイルを新規作成")
            msg.setWindowTitle("設定ファイル作成")
            msg.exec_()

            self.config = self.default_config.copy()
            self.save_config()
        else:
            try:
                with open(self.config_path, 'r', encoding='utf-8') as f:
                    self.config = json.load(f)
            except:
                msg = QMessageBox()
                msg.setIcon(QMessageBox.Warning)
                msg.setText("読み込みエラー")
                msg.setInformativeText("初期設定で上書きします")
                msg.setWindowTitle("設定ファイルエラー")
                msg.exec_()

                self.config = self.default_config.copy()
                self.save_config()
        return self.config

    def save_config(self):
        with open(self.config_path, 'w', encoding='utf-8') as f:
            json.dump(self.config, f, indent=4, ensure_ascii=False)

    def update_config(self, new_config):
        self.config.update(new_config)
        self.save_config()
