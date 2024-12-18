"""
監視対象ディレクトリ内のファイルを監視し、処理を実行します。
"""
from watchdog.events import FileSystemEventHandler
from modules.video_thumbGenerator import VideoThumbnailGenerator
from modules.pdf_converter import PDFConverter
from modules.ppt_to_video import export_ppt_to_video
from utils.logwriter import setup_logging
import os
import logging
import socket

# 監視対象の拡張子
VIDEO_EXTENSIONS = ['.mp4', '.avi', '.mkv', '.flv', '.mov']
PDF_EXTENSION = '.pdf'
PPT_EXTENSIONS = ['.pptx', '.ppsx']

setup_logging()


def send_udp_message(ip, port, message):
    """UDPメッセージを送信します。"""
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        sock.sendto(message.encode(), (ip, port))
        sock.close()
    except Exception as e:
        logging.error(f"Error in sending UDP message: {e}")


class FileHandler(FileSystemEventHandler):
    """ファイルの追加や変更を監視し、処理を実行します。"""

    def __init__(self, exclude_subdirectories, sender=None, ip=None, port=None, seconds=1):
        super().__init__()
        self.exclude_subdirectories = exclude_subdirectories
        self.sender = sender
        self.ip = ip
        self.port = port
        self.seconds = seconds
        self.file_converter = PDFConverter()  # PDFConverterをselfで初期化

    def on_created(self, event):
        """ファイル作成時に呼び出されます。"""
        if event.is_directory:
            return

        file_path = event.src_path
        ext = os.path.splitext(file_path)[1].lower()
        logging.info(f"on_created called with file: {
                     file_path}, extension: {ext}")

        if ext in VIDEO_EXTENSIONS:
            logging.info(f"Processing video file: {file_path}")
            self.create_thumbnail(file_path)
        elif ext == PDF_EXTENSION:
            logging.info(f"Processing PDF file: {file_path}")
            self.convert_pdf_to_images(file_path)
        elif ext in PPT_EXTENSIONS:
            logging.info(f"Processing PPT file: {file_path}")
            try:
                self.convert_ppt_to_video(file_path)
            except Exception as e:
                logging.error(f"Failed to convert PPT to video: {e}")
                self.convert_ppt_to_pdf(file_path)

        if self.sender:
            try:
                self.sender.send_message(
                    self.ip, self.port, f"File created: {file_path}")
            except Exception as e:
                logging.error(f"Error in sending message: {e}")
        else:
            send_udp_message(self.ip, self.port, f"File created: {file_path}")

    def create_thumbnail(self, file_path):
        """動画のサムネイルを生成します。"""
        try:
            thumbnail_path = VideoThumbnailGenerator().create_thumbnail(file_path, self.seconds)
            logging.info(f"Thumbnail generated: {thumbnail_path}")
        except Exception as e:
            logging.error(f"Failed to create video thumbnail: {e}")

    def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            output_dir = os.path.join(os.path.dirname(pdf_path), "sequence")
            images = self.file_converter.convert_pdf_to_images(
                pdf_path, output_dir)
            if images:
                thumbnail_path = os.path.join(
                    os.path.dirname(pdf_path), "thumbnail.png")
                os.rename(images[0], thumbnail_path)
                logging.info(f"PDF thumbnail generated: {thumbnail_path}")
        except Exception as e:
            logging.error(f"Failed to convert PDF: {e}")

    def convert_ppt_to_pdf(self, ppt_path):
        """PPTX/PPSXをPDFに変換します。"""
        try:
            self.file_converter.convert_ppt_to_pdf(ppt_path)
        except Exception as e:
            logging.error(f"Failed to convert PPT to PDF: {e}")

    def convert_ppt_to_video(self, ppt_path):
        """PPTX/PPSXを動画に変換します。"""
        try:
            folder_path = os.path.dirname(ppt_path)
            export_ppt_to_video(folder_path, folder_path)
        except Exception as e:
            logging.error(f"Failed to convert PPT to video: {e}")

    def destroy(self, reason):
        """終了時のクリーンアップ処理を行います。"""
        if self.sender:
            try:
                self.sender.send_message(self.ip, self.port, reason)
            except Exception as e:
                logging.error(f"Error in sending message: {e}")
        else:
            send_udp_message(self.ip, self.port, reason)
        logging.info(f"Destroy called with reason: {reason}")
        return 0

    def list_files(self, path):
        """指定したディレクトリ内のすべてのファイルをリストします。"""
        for root, _, files in os.walk(path):
            for file in files:
                file_path = os.path.join(root, file)
                logging.info(f"Found file: {file_path}")


def set_filehandle(event_handler, start_path, exclude_subdirectories, filelist):
    """指定したディレクトリ内のすべての動画ファイルに処理を実行します。"""
    if exclude_subdirectories:
        for file in os.listdir(start_path):
            if file.endswith(tuple(VIDEO_EXTENSIONS)):
                file_path = os.path.join(start_path, file)
                filelist.append(file_path)
                event_handler.create_thumbnail(file_path)
    else:
        for root, _, files in os.walk(start_path):
            for file in files:
                if file.endswith(tuple(VIDEO_EXTENSIONS)):
                    file_path = os.path.join(root, file)
                    filelist.append(file_path)
                    event_handler.create_thumbnail(file_path)


class FileMockEvent:
    """モックイベントクラス"""

    def __init__(self, src_path):
        self.src_path = src_path
        self.is_directory = False
