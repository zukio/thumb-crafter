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
from modules.fileConvert_ppt import PowerPointConverter
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

    def __init__(self, ignore_subfolders, sender=None, ip=None, port=None, thumbnail_time_seconds=1, convert_slide=None, convert_document=None, page_duration=5):
        super().__init__()
        self.ignore_subfolders = ignore_subfolders
        self.sender = sender
        self.ip = ip
        self.port = port
        self.thumbnail_time_seconds = thumbnail_time_seconds
        self.page_duration = page_duration
        self.convert_slide = convert_slide
        self.convert_document = convert_document
        self.pdf_converter = PDFConverter()
        self.ppt_converter = PowerPointConverter()
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
        print(f"File created event: {event.src_path}")
        if not event.is_directory:
            asyncio.run_coroutine_threadsafe(
                self.handle_deleted(event), MAIN_LOOP)

    async def handle_created(self, event):
        """ファイル作成・変更時に非同期で処理します。"""
        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        logging.info(f"handle_created called with file: {
                     file_path}, extension: {ext}")

        # 動画ファイルの場合、サムネイルを作成
        if ext in VIDEO_EXTENSIONS:
            await self.create_thumbnail(file_path)

        # PDFファイルの場合
        elif ext == PDF_EXTENSION:
            mode = self.convert_document.lower()
            if mode == "video":
                await self.convert_pdf_to_video(file_path)
            elif mode == "sequence":
                await self.convert_pdf_to_images(file_path)
            else:
                logging.info(f"Ignoring PDF file: {
                             file_path} (convert_document={mode})")

        # PowerPointファイルの場合
        elif ext in PPT_EXTENSIONS:
            mode = self.convert_slide.lower()
            if mode == "video":
                await self.convert_ppt_to_video(file_path)
            elif mode == "sequence":
                await self.convert_ppt_to_images(file_path)
            else:
                logging.info(f"Ignoring PowerPoint file: {
                             file_path} (convert_slide={mode})")

        # その他のファイル
        else:
            logging.info(f"Ignoring file: {file_path} (unsupported extension)")

        # イベントをキューに追加
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
            await VideoThumbnailGenerator().create_thumbnail(file_path, self.thumbnail_time_seconds)
            if file_path not in video_files:
                video_files.append(file_path)
        except Exception as e:
            logging.error(f"Failed to create video thumbnail: {e}")

    async def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            output_dir = await self.pdf_converter.convert_pdf_to_images(pdf_path)

            if output_dir not in sequence_folders:
                sequence_folders.append(output_dir)
                return output_dir
        except Exception as e:
            logging.error(f"Failed to convert PDF: {e}")

    async def convert_pdf_to_video(self, pdf_path):
        """PDFを動画に変換します。"""
        try:
            # PDFから動画に変換
            folder_path = os.path.dirname(pdf_path)
            output_video = os.path.join(folder_path, os.path.splitext(
                os.path.basename(pdf_path))[0] + ".mp4")
            await self.pdf_converter.convert_pdf_to_video(
                pdf_path, output_video, self.page_duration
            )

            # 動画からサムネイルを生成（on_createdイベントが発火されないため手動で呼び出す）
            await self.create_thumbnail(output_video)
        except Exception as e:
            logging.error(f"Failed to convert PDF to video: {e}")

    async def convert_ppt_to_video(self, ppt_path):
        """PPTX/PPSXを動画に変換します。"""
        folder_path = os.path.dirname(ppt_path)
        video_path = os.path.join(
            folder_path, f"{os.path.splitext(os.path.basename(ppt_path))[0]}.mp4")

        try:
            # PPTから動画に変換
            self.ppt_converter.export_ppt_to_video(
                folder_path, folder_path, self.page_duration)

        except Exception as e:
            logging.error(f"Failed to convert PPT to video: {e}")
            try:
                # PPTをPDFに変換
                pdf_path = await self.pdf_converter.convert_ppt_to_pdf(ppt_path)
                # PDFを動画に変換
                await self.pdf_converter.convert_pdf_to_video(
                    pdf_path, video_path, self.page_duration)
            except Exception as e:
                logging.error(f"Failed to convert PPT to PDF: {e}")

        if video_path is None:
            logging.error("Video path was not created successfully.")

        if os.path.exists(video_path):
            # 動画からサムネイルを生成（動画が正常にエクスポートされても、on_createdイベントが発火されないため手動で呼び出す）
            await self.create_thumbnail(video_path)
            logging.info(f"Thumbnail created for video: {video_path}")

    async def convert_ppt_to_images(self, ppt_path):
        """PPTX/PPSXをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            # PPTをシーケンス画像に変換
            output_dir = await self.ppt_converter.convert_ppt_to_images(ppt_path)

            if output_dir not in sequence_folders:
                sequence_folders.append(output_dir)
                return output_dir
        except Exception as e:
            logging.error(f"Failed to convert PPT to images: {e}")

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
        print(f"Listing files in directory: {start_path}")
        await set_filehandle(self, start_path, self.ignore_subfolders, [])
        # 送信機能がある場合のみイベントを送信
        if self.sender:
            self.sender.send_message(self.ip, self.port, json.dumps({
                "events": [{"type": "Startup", "path": ""}],
                "files": video_files,
                "sequence_folders": sequence_folders
            }))


async def set_filehandle(event_handler, start_path, ignore_subfolders, filelist):
    """指定したディレクトリ（およびそのサブディレクトリ）内のすべてのファイルに対して `on_created` を呼び出します。"""
    if ignore_subfolders:
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
