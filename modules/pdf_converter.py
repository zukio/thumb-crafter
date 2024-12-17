""" 
PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。
imageMagick（PDFを画像に変換するためのコマンドラインツール）を使用してPDFを画像に変換します。
imageMagickを使用するにはGhostScriptも必要です。
"""
import os
import subprocess
import logging
import shutil
from pathlib import Path

# ログの設定
logging.basicConfig(level=logging.INFO,
                    format='%(asctime)s - %(levelname)s - %(message)s')


class PDFConverter:
    def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルに設定します。"""
        try:
            logging.info(f"Starting PDF conversion for: {pdf_path}")

            # PDFごとにユニークなsequenceフォルダを作成
            pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
            output_dir = os.path.join(os.path.dirname(
                pdf_path), f"{pdf_name}_sequence")

            # 既存のsequenceフォルダがあれば削除
            if os.path.exists(output_dir):
                shutil.rmtree(output_dir)
                logging.info(f"Existing sequence folder removed: {output_dir}")

            os.makedirs(output_dir, exist_ok=True)

            images = self.file_converter.convert_pdf_to_images(
                pdf_path, output_dir)

            if images:
                thumbnail_path = os.path.join(
                    os.path.dirname(pdf_path), "thumbnail.png")

                # 既存のサムネイルがあれば削除
                if os.path.exists(thumbnail_path):
                    os.remove(thumbnail_path)
                    logging.info(f"Existing thumbnail removed: {
                                 thumbnail_path}")

                os.rename(images[0], thumbnail_path)
                logging.info(f"PDF thumbnail generated: {thumbnail_path}")

        except Exception as e:
            logging.error(f"Failed to convert PDF: {e}")

    def convert_ppt_to_pdf(self, ppt_path):
        """PPT/PPSXをPDFに変換し、その後動画に変換します。"""
        try:
            ppt_path = Path(ppt_path)
            pdf_path = ppt_path.with_suffix('.pdf')

            # LibreOfficeでPPTをPDFに変換
            cmd_ppt_to_pdf = [
                'soffice', '--headless', '--convert-to', 'pdf', '--outdir',
                str(ppt_path.parent), str(ppt_path)
            ]
            subprocess.check_output(cmd_ppt_to_pdf, stderr=subprocess.STDOUT)
            logging.info(f"PPT converted to PDF: {pdf_path}")

            # PDFを動画に変換
            self.convert_pdf_to_images(pdf_path, ppt_path.parent)
            logging.info(f"PDF converted to images for video creation")

        except subprocess.CalledProcessError as e:
            logging.error(f"Failed to convert PPT to PDF: {e.output.decode()}")
        except Exception as e:
            logging.error(f"Unexpected error during PPT conversion: {e}")
