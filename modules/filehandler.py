"""
監視対象ディレクトリ内のファイルを監視し、処理を実行、
オプションの指定に応じてUDP/TCPメッセージ送信を行います。
"""
import os
import logging
import json
from watchdog.events import FileSystemEventHandler
from modules.fileGenerate_thumbnail import VideoThumbnailGenerator
from modules.fileConvert_pdf import PDFConverter
from modules.fileConvert_ppt import export_ppt_to_video
from utils.logwriter import setup_logging
import asyncio


# 監視対象の拡張子
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.flv', '.mov']
PDF_EXTENSION = '.pdf'
PPT_EXTENSIONS = ['.pptx', '.ppsx']

# 対象の動画ファイルのパスのリスト
video_files = []

setup_logging()


class FileHandler(FileSystemEventHandler):
    """ファイルの追加や変更を監視し、処理およびUDPメッセージ送信を実行します。"""


# 監視対象の拡張子
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.flv', '.mov']
PDF_EXTENSION = '.pdf'
PPT_EXTENSIONS = ['.pptx', '.ppsx']

# 対象の動画ファイルのパスのリスト
video_files = []
# PDFおよびPPTのシーケンス画像フォルダのリスト
sequence_folders = []
# メインスレッドのイベントループを作成
MAIN_LOOP = asyncio.get_event_loop()

setup_logging()


class FileHandler(FileSystemEventHandler):
    """ファイルの追加や変更を監視し、処理およびUDPメッセージ送信を実行します。"""

    def __init__(self, exclude_subdirectories, sender=None, ip=None, port=None, seconds=1):
        super().__init__()
        self.exclude_subdirectories = exclude_subdirectories
        self.sender = sender
        self.ip = ip
        self.port = port
        self.seconds = seconds
        self.file_converter = PDFConverter()
        self.event_queue = [] if sender else None

    def on_created(self, event):
        """ファイル作成時に呼び出されます。"""
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.handle_created(event), MAIN_LOOP)

    def on_modified(self, event):
        """ファイル変更時に呼び出されます。"""
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.handle_created(event), MAIN_LOOP)

    def on_deleted(self, event):
        """ファイル削除時に呼び出されます。"""
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.handle_deleted(event), MAIN_LOOP)

    async def handle_created(self, event):
        """ファイル作成・変更時に非同期で処理します。"""
        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        logging.info(f"handle_created called with file: {
                     file_path}, extension: {ext}")

        if ext in VIDEO_EXTENSIONS:
            await self.create_thumbnail(file_path)
        elif ext == PDF_EXTENSION:
            await self.convert_pdf_to_images(file_path)
        elif ext in PPT_EXTENSIONS:
            await self.convert_ppt(file_path)

        self.queue_event(event)

    async def handle_deleted(self, event):
        """ファイル削除時に非同期で処理します。"""
        file_path = event.src_path
        logging.info(f"handle_deleted called with file: {file_path}")

        if file_path in video_files:
            video_files.remove(file_path)

        thumb_path = f"{os.path.splitext(file_path)[0]}_thumbnail.png"
        if os.path.isfile(thumb_path):
            os.remove(thumb_path)
            logging.info(f"Thumbnail deleted: {thumb_path}")

        self.queue_event(event)

    async def create_thumbnail(self, file_path):
        """動画ファイルのサムネイル生成"""
        try:
            await VideoThumbnailGenerator().create_thumbnail(file_path, self.seconds)
            if file_path not in video_files:
                video_files.append(file_path)
        except Exception as e:
            logging.error(f"Failed to create video thumbnail: {e}")

    async def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            output_dir = os.path.join(os.path.dirname(pdf_path), f"{
                                      os.path.splitext(os.path.basename(pdf_path))[0]}_sequence")
            await self.file_converter.convert_pdf_to_images(pdf_path)
            if output_dir not in sequence_folders:
                sequence_folders.append(output_dir)
        except Exception as e:
            logging.error(f"Failed to convert PDF: {e}")

    async def convert_ppt(self, ppt_path):
        """PPTX/PPSXを動画に変換します。"""
        try:
            # PPTから動画に変換
            folder_path = os.path.dirname(ppt_path)
            export_ppt_to_video(folder_path, folder_path)

            # 生成された動画のパスを構築
            video_path = os.path.join(
                folder_path, f"{os.path.splitext(os.path.basename(ppt_path))[0]}.mp4")

            # 動画からサムネイルを生成（動画が正常にエクスポートされても、on_createdイベントが発火されないため手動で呼び出す）
            if os.path.exists(video_path):
                await self.create_thumbnail(video_path)
                logging.info(f"Thumbnail created for video: {video_path}")
        except Exception as e:
            logging.error(f"Failed to convert PPT to video: {e}")
            try:
                await self.file_converter.convert_ppt_to_pdf(ppt_path)
            except Exception as e:
                logging.error(f"Failed to convert PPT to PDF: {e}")

    def queue_event(self, event):
        """イベントをキューに追加し、UDPメッセージを送信します。"""
        if self.event_queue is not None:
            self.event_queue.append(event)
            self.send_udp_message()

    def send_udp_message(self):
        """UDPメッセージを送信します。"""
        if self.sender and self.event_queue:
            try:
                events = [{"type": event.event_type, "path": event.src_path}
                          for event in self.event_queue]
                message = json.dumps({
                    "events": events,
                    "files": video_files,
                    "sequence_folders": sequence_folders
                })
                self.sender.send_message(self.ip, self.port, message)
                self.event_queue.clear()
            except Exception as e:
                logging.error(f"Error in sending UDP message: {e}")

    def destroy(self, reason):
        """終了メッセージを送信します。"""
        if self.sender:
            try:
                self.sender.send_message(self.ip, self.port, reason)
            except Exception as e:
                logging.error(f"Error in sending message: {e}")
        logging.info(f"Destroy called with reason: {reason}")

    async def list_files(self, start_path):
        """指定したディレクトリ内のすべてのファイルをリストし、処理します。"""
        # 起動時にファイルを読み込んだときのUDP送信
        logging.info('===============')
        logging.info(f"Listing files in directory: {start_path}")
        await set_filehandle(self, start_path, self.exclude_subdirectories, [])
        # 送信機能がある場合のみイベントを送信
        if self.sender:
            self.sender.send_message(self.ip, self.port, json.dumps({
                "events": [{"type": "Startup", "path": ""}],
                "files": video_files,
                "sequence_folders": sequence_folders
            }))


async def set_filehandle(event_handler, start_path, exclude_subdirectories, filelist):
    """指定したディレクトリ（およびそのサブディレクトリ）内のすべてのファイルに対して `on_created` を呼び出します。"""
    if exclude_subdirectories:
        for file in os.listdir(start_path):
            file_path = os.path.join(start_path, file)
            await event_handler.handle_created(FileMockEvent(file_path))
    else:
        for root, _, files in os.walk(start_path):
            current_depth = root.count(
                os.path.sep) - start_path.count(os.path.sep)
            # サブディレクトリの深さが 4 以下の場合のみ処理を行う（誤使用を想定した暴走ガード）
            if current_depth < 5:
                for file in files:
                    file_path = os.path.join(root, file)
                    await event_handler.handle_created(FileMockEvent(file_path))


class FileMockEvent:
    """on_createdに渡すための擬似イベントクラス"""

    def __init__(self, file_path):
        self.src_path = file_path
        self.is_directory = False
        self.event_type = 'created'
