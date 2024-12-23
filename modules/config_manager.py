from PyQt5.QtWidgets import QMessageBox
import os
import json
import argparse
import sys
from pathlib import Path
from utils.solvepath import exe_path


class ConfigManager:
    DEFAULT_CONFIG = {
        'target': '',
        'ignore_subfolders': False,
        'protocol': 'none',
        'ip': 'localhost',
        'port': 12345,
        'send_interval': 1,  # UDP送信の間隔
        'thumbnail_time_seconds': 1,  # 動画の何秒目をサムネイルに書き出すか
        "convert_slide": "none",      # スライド（PPT）を処理しない "none", または "video", "sequence" に変換
        "convert_document": "none",  # 電子文書（PDF）を処理しない "none", または "video", "sequence" に変換
        "page_duration": 5
    }

    def __init__(self, app_name="thumb-crafter"):
        self.app_name = app_name
        self.default_config = self.DEFAULT_CONFIG
        self.config = {}
        # 設定ファイルのパス （PyInstallerでexe化した場合に対応）
        self.config_path = exe_path(f"{self.app_name}_config.json")

    def load_config(self):
        if not os.path.exists(self.config_path):
            msg = QMessageBox()
            msg.setIcon(QMessageBox.Information)
            msg.setText("設定ファイルが見つかりません")
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
        """現在の設定をファイルに保存"""
        try:
            with open(self.config_path, 'w', encoding='utf-8') as f:
                json.dump(self.config, f, ensure_ascii=False, indent=4)
            print(f"設定ファイルが保存されました: {self.config_path}")
        except Exception as e:
            print(f"設定ファイルの保存に失敗しました: {e}")

    def update_config(self, new_config):
        self.config.update(new_config)
        self.save_config()

    @staticmethod
    def parse_arguments():
        parser = argparse.ArgumentParser(description='Thumb Crafter EX')
        parser.add_argument('--ignore_subfolders', default=None, action='store_true',
                            help='Exclude subdirectories in monitoring and thumbnail creation.')
        parser.add_argument('--target', default=None, type=str,
                            help='Directory path to monitor')
        parser.add_argument('--thumbnail_time_seconds', default=None, type=int,
                            help='Specify the seconds of the frame to be used for thumbnail generation')
        parser.add_argument('--ip', default=None, type=str,
                            help='IP address to send the messages')
        parser.add_argument('--port', default=None, type=int,
                            help='Port number to send the messages')
        parser.add_argument('--send_interval', default=None, type=int,
                            help='Delay in seconds for sending messages')
        parser.add_argument('--protocol', choices=['none', 'udp', 'tcp'], default=None,
                            help='Communication protocol to use (none, udp, tcp)')
        parser.add_argument('--convert_slide', choices=['none', 'video', 'sequence'],
                            default=None,  help='Process slides as video or sequence')
        parser.add_argument('--convert_document', choices=['none', 'video', 'sequence'],
                            default=None,  help='Process documents as video or sequence')
        parser.add_argument('--page_duration', default=None,
                            type=int,  help='Duration of each page in seconds')

        return vars(parser.parse_args())

    @staticmethod
    def merge_config(json_config, cli_args):
        for key, value in cli_args.items():
            if value is not None:  # CLI引数が指定されている場合はそれを優先
                json_config[key] = value
        return json_config
