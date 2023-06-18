import os
import time
import argparse
from watchdog.observers import Observer
from modules.filehandler import VideoFileHandler

if __name__ == "__main__":
    # 引数 --exclude_subdirectories が指定された場合、ルートディレクトリのみが監視されます。引数が指定されていない場合、サブディレクトリも監視します。
    parser = argparse.ArgumentParser(description='Monitor a directory and create thumbnails for video files.')
    parser.add_argument('--exclude_subdirectories', action='store_true',
                        help='Exclude subdirectories in monitoring and thumbnail creation.')
    parser.add_argument('--target', default='', type=str, help='Directory path to monitor')
    parser.add_argument('--seconds', default=1, type=int, help='Specify the seconds of the frame to be used for thumbnail generation')
    args = parser.parse_args()

    event_handler = VideoFileHandler(args.exclude_subdirectories, args.seconds)
    observer = Observer()

    # 監視するディレクトリパスは、Pythonプロジェクトフォルダが置かれたディレクトリ（およびそのサブディレクトリ）
    path = os.path.abspath(args.target) if args.target else os.path.abspath(os.path.join(os.getcwd(), os.pardir))
    
    event_handler.list_files(path)

    observer.schedule(event_handler, path, recursive=not args.exclude_subdirectories)
    observer.start()

    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        observer.stop()
    observer.join()


