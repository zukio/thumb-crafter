""" 
動画ファイルからサムネイルを生成するモジュール
ffmpegまたはOpenCVを使用して動画ファイルからサムネイルを生成します。
"""
import os
import asyncio
import cv2


class VideoThumbnailGenerator:
    async def create_thumbnail(self, file_path, user_second):
        """ffmpegを使用し、指定された動画ファイルからサムネイルを非同期で生成します。"""
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
        """ffmpegを使用し、指定された動画ファイルの長さを非同期で取得します。"""
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

    def video_to_thumbnail(video_path, output_image, time_in_seconds=0):
        """
        動画から指定した時間のフレームをサムネイルとして保存（OpenCV版）
        :param video_path: 動画ファイルのパス
        :param output_image: 出力されるサムネイル画像のパス
        :param time_in_seconds: サムネイルを抽出する時間（秒単位）
        """
        # 動画を読み込む
        cap = cv2.VideoCapture(video_path)

        if not cap.isOpened():
            print(f"Error: Cannot open video {video_path}")
            return

        # フレームレートを取得
        fps = cap.get(cv2.CAP_PROP_FPS)
        print(f"FPS: {fps}")

        # 指定された秒数に対応するフレーム番号を計算
        frame_number = int(fps * time_in_seconds)
        cap.set(cv2.CAP_PROP_POS_FRAMES, frame_number)

        # フレームを読み取る
        ret, frame = cap.read()
        if ret:
            # フレームを画像として保存
            cv2.imwrite(output_image, frame)
            print(f"Thumbnail saved at: {output_image}")
        else:
            print("Error: Cannot read the frame")

        # リソースを解放
        cap.release()
