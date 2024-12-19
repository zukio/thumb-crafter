import asyncio
import os
import shutil
from pathlib import Path


class PDFConverter:
    async def convert_pdf_to_images(self, pdf_path):
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
        """PPT/PPSXをPDFに変換し、その後PDFを画像に変換します。"""
        ppt_path = Path(ppt_path)
        pdf_path = ppt_path.with_suffix('.pdf')

        # LibreOfficeでPPTをPDFに非同期で変換
        cmd_ppt_to_pdf = [
            'soffice', '--headless', '--convert-to', 'pdf', '--outdir',
            str(ppt_path.parent), str(ppt_path)
        ]
        await self.run_subprocess(cmd_ppt_to_pdf, f"PPT converted to PDF: {pdf_path}")

        # PDFを画像に変換
        await self.convert_pdf_to_images(pdf_path)

    async def run_subprocess(self, cmd, success_message):
        """非同期でsubprocessを実行します。"""
        process = await asyncio.create_subprocess_exec(
            *cmd, stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode != 0:
            raise RuntimeError(f"Error during subprocess: {
                               stderr.decode().strip()}")
