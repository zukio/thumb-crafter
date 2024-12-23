import os
import sys
import tempfile
import signal
import psutil

# PIDファイルのパス
# PID_FILE_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".pid")
# PID_FILE_PATH = onefile_path(".pid")  # PyInstallerでexe化した場合のパス
PID_FILE_PATH = os.path.join(os.getenv(
    'APPDATA', tempfile.gettempdir()), "thumb_crafter.pid")  # APPDATAを使用する場合


def check_previous_instance():
    if os.path.exists(PID_FILE_PATH):
        with open(PID_FILE_PATH, 'r') as f:
            try:
                pid = int(f.read())
                if psutil.pid_exists(pid):  # PIDが存在する場合、多重起動とみなす
                    print("既に別のインスタンスが実行中です。")
                    return True
            except Exception:
                print("PIDファイルが破損しています。再作成します。")
                pass
    return False


def create_pid_file():
    # 新しいPID情報を保存
    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))


def remove_pid_file():
    if os.path.isfile(PID_FILE_PATH):
        os.remove(PID_FILE_PATH)


def exit_handler(signum, frame, app):
    if app:
        app.stop()
    remove_pid_file()
    sys.exit(0)


def block_global_instance(app):
    """全インスタンスの多重起動を防止"""
    # 既存のインスタンスがある場合
    if check_previous_instance():
        # sys.exit(1)  # ここで直接終了
        return True

    # 新しいPIDを記録
    with open(PID_FILE_PATH, 'w') as f:
        f.write(str(os.getpid()))

    # 終了時にPIDファイルを削除するためのシグナルハンドラを登録する
    signal.signal(signal.SIGTERM, lambda s,
                  f: exit_handler(s, f, app))
    signal.signal(signal.SIGINT, lambda s,
                  f: exit_handler(s, f, app))
    return False
