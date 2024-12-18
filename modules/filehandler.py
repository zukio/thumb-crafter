""" 
監視対象ディレクトリ内のファイルを監視し、処理を実行、
オプションの指定に応じてUDP/TCPメッセージ送信を行います。
"""
import os
import logging
import json
from watchdog.events import FileSystemEventHandler
from modules.video_thumbGenerator import VideoThumbnailGenerator
from modules.pdf_converter import PDFConverter
from modules.ppt_to_video import export_ppt_to_video
from utils.logwriter import setup_logging
import asyncio


# 監視対象の拡張子
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.flv', '.mov']
PDF_EXTENSION = '.pdf'
PPT_EXTENSIONS = ['.pptx', '.ppsx']

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

    async def on_created(self, event):
        """ファイル作成時に呼び出されます。"""
        if event.is_directory:
            return

        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        logging.info(f"on_created called with file: {
                     file_path}, extension: {ext}")

        if ext in VIDEO_EXTENSIONS:
            await self.create_thumbnail(file_path)
        elif ext == PDF_EXTENSION:
            await self.convert_pdf_to_images(file_path)
        elif ext in PPT_EXTENSIONS:
            await self.convert_ppt(file_path)
        # 送信機能がある場合のみイベントを送信
        if self.sender:
            self.queue_event(event)

    async def create_thumbnail(self, file_path):
        """動画ファイルのサムネイル生成"""
        try:
            await VideoThumbnailGenerator().create_thumbnail(file_path, self.seconds)
        except Exception as e:
            logging.error(f"Failed to create video thumbnail: {e}")

    async def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            await self.file_converter.convert_pdf_to_images(pdf_path)
        except Exception as e:
            logging.error(f"Failed to convert PDF: {e}")

    async def convert_ppt(self, ppt_path):
        """PPTX/PPSXを動画に変換します。"""
        try:
            folder_path = os.path.dirname(ppt_path)
            export_ppt_to_video(folder_path, folder_path)
        except Exception as e:
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
                message = json.dumps({"events": events})
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
        logging.info(f"Listing files in directory: {start_path}")
        await set_filehandle(self, start_path, self.exclude_subdirectories, [])


async def set_filehandle(event_handler, start_path, exclude_subdirectories, filelist):
    """指定したディレクトリ（およびそのサブディレクトリ）内のすべてのファイルに対して `on_created` を呼び出します。"""
    if exclude_subdirectories:
        for file in os.listdir(start_path):
            file_path = os.path.join(start_path, file)
            await event_handler.on_created(FileMockEvent(file_path))
    else:
        for root, _, files in os.walk(start_path):
            current_depth = root.count(
                os.path.sep) - start_path.count(os.path.sep)
            if current_depth < 5:
                for file in files:
                    file_path = os.path.join(root, file)
                    await event_handler.on_created(FileMockEvent(file_path))


class FileMockEvent:
    """on_createdに渡すための擬似イベントクラス"""

    def __init__(self, file_path):
        self.src_path = file_path
        self.is_directory = False
        self.event_type = 'created'
