""" 
動画ファイルからサムネイルを生成するモジュール
ffmpegを使用して動画ファイルからサムネイルを生成します。
"""
import os
import asyncio


class VideoThumbnailGenerator:
    async def create_thumbnail(self, file_path, user_second):
        """指定された動画ファイルからサムネイルを非同期で生成します。"""
        thumbnail_path = f"{os.path.splitext(file_path)[0]}_thumbnail.png"
        duration = await self.get_video_duration(file_path)

        if user_second == 0 or duration <= user_second:
            # 動画の長さが指定秒以下の場合、最初のフレームをサムネイルとして生成
            cmd = f'ffmpeg -y -i "{file_path}" -vframes 1 "{thumbnail_path}"'
        else:
            # 分と秒に分割して時間指定
            minutes, seconds = divmod(user_second, 60)
            cmd = f'ffmpeg -y -i "{file_path}" -ss {int(minutes):02d}:{int(
                seconds):02d} -t 00:00:01 -vframes 1 "{thumbnail_path}"'

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return thumbnail_path
        else:
            raise Exception(f"Thumbnail generation failed: {
                            stderr.decode().strip()}")

    async def get_video_duration(self, file_path):
        """指定された動画ファイルの長さを非同期で取得します。"""
        cmd = f'ffprobe -v error -show_entries format=duration -of default=noprint_wrappers=1:nokey=1 "{
            file_path}"'

        process = await asyncio.create_subprocess_shell(
            cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        if process.returncode == 0:
            return float(stdout.decode().strip())
        else:
            raise Exception(f"Failed to get video duration: {
                            stderr.decode().strip()}")
