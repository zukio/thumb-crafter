import os
import sys


def exe_path(relative_path):
    """開発環境とPyInstallerでexe可した後の実行環境の両方に対応"""
    if getattr(sys, 'frozen', False):  # EXE環境では、実行パス（exe）を基準にPIDファイルを設定
        BASE_PATH = os.path.dirname(sys.executable)
    else:
        BASE_PATH = os.path.dirname(os.path.dirname(
            __file__))  # 実行ファイル（main.py）のあるディレクトリ

    full_path = os.path.join(BASE_PATH, relative_path)
    print(f"Resolved path: {full_path}")  # デバッグ用
    return full_path


def onefile_path(relative_path):
    """開発環境とPyInstallerでexe可した後の実行環境の両方に対応（PyInstallerの--onefileモードに対応）"""
    try:
        # exeを実行すると一時フォルダに展開される（一時フォルダのパスはsys._MEIPASSに格納される）
        BASE_PATH = sys._MEIPASS  # PyInstallerの一時フォルダ
    except AttributeError:
        # 開発環境では実行ファイルのあるディレクトリをベースパスとする
        # BASE_PATH = os.path.dirname(os.path.abspath(__file__))  # スクリプトのある場所
        BASE_PATH = os.path.dirname(os.path.dirname(
            __file__))  # 実行ファイル（main.py）のあるディレクトリ

    full_path = os.path.join(BASE_PATH, relative_path)
    print(f"Resolved path: {full_path}")  # デバッグ用
    return full_path
