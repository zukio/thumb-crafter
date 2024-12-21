""" 
PDFをシーケンス画像に変換します。
pip（PyMuPDF）を使用する版と、外部ツール（ImageMagick）を使用する版があります。
外部ツール（ImageMagick）を使用する方法は高速かつ効率的ですがインストールが複雑です。
"""
import os
import asyncio
import shutil
from pathlib import Path
import fitz  # PyMuPDF
from modules.fileconvert_img import ImgToVideo


class PDFConverter:
    async def convert_pdf_to_images(self, pdf_path):
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルとして生成します。"""
        # 出力ディレクトリの設定
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        sequence_dir = Path(pdf_path).parent / f"{pdf_name}_sequence"
        os.makedirs(sequence_dir, exist_ok=True)

        # PyMuPDFを使ってPDFを画像に変換
        doc = fitz.open(pdf_path)
        for page_number in range(len(doc)):
            page = doc[page_number]
            pix = page.get_pixmap(dpi=150)  # 解像度を設定（150 DPI）
            output_image = sequence_dir / f"page-{page_number:03d}.png"
            pix.save(output_image)
            print(f"Saved {output_image}")

        # 1ページ目をサムネイルとしてコピー
        first_page = sequence_dir / "page-000.png"
        thumbnail_path = Path(pdf_path).parent / f"{pdf_name}_thumbnail.png"
        if first_page.exists():
            shutil.copy(first_page, thumbnail_path)
            print(f"Thumbnail saved: {thumbnail_path}")

    async def convert_pdf_to_imagemagick(self, pdf_path):
        # ImageMagickのインストールが必要です。
        """PDFをシーケンス画像に変換し、1ページ目をサムネイルとして生成します。"""
        # 出力ディレクトリの設定
        pdf_name = os.path.splitext(os.path.basename(pdf_path))[0]
        sequence_dir = Path(pdf_path).parent / f"{pdf_name}_sequence"
        os.makedirs(sequence_dir, exist_ok=True)

        # 出力画像のパスフォーマット
        output_image = sequence_dir / "page-%03d.png"

        # ImageMagickのコマンド
        cmd = ["magick", "convert", "-density",
               "150", pdf_path, str(output_image)]
        await self.run_subprocess(cmd, f"PDF converted to images: {sequence_dir}")

        # 1ページ目をサムネイルにコピー
        first_page = sequence_dir / "page-000.png"
        thumbnail_path = Path(pdf_path).parent / \
            f"{pdf_name}_thumbnail.png"
        if first_page.exists():
            shutil.copy(first_page, thumbnail_path)

    async def convert_ppt_to_pdf(self, ppt_path):
        # LibreOfficeのインストールが必要です。
        """PPT/PPSXをPDFに変換し、その後PDFを画像に変換します。"""
        ppt_path = Path(ppt_path)
        pdf_path = ppt_path.with_suffix('.pdf')

        # LibreOfficeでPPTをPDFに非同期で変換
        cmd_ppt_to_pdf = [
            'soffice', '--headless', '--convert-to', 'pdf', '--outdir',
            str(ppt_path.parent), str(ppt_path)
        ]
        await self.run_subprocess(cmd_ppt_to_pdf, f"PPT converted to PDF: {pdf_path}")
        return pdf_path

    async def run_subprocess(self, cmd, success_message):
        """非同期でsubprocessを実行します。"""
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Error during subprocess: {
                               stderr.decode().strip()}")

    def pdf_to_video(self, pdf_path, output_video, temp_dir="temp_images", fps=1):
        """PDFを動画に変換"""
        try:
            print("Converting PDF to images...")
            image_dir = self.convert_pdf_to_images(pdf_path, temp_dir)

            print("Creating video from images...")
            ImgToVideo.images_to_video_ffmpeg(image_dir, output_video, fps)

            print("PDF to video conversion completed.")
        finally:
            # 一時ディレクトリを削除する場合はここで対応
            pass
