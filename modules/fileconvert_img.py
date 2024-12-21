
""" 
動画ファイルからサムネイルを生成するモジュール
ffmpegを使用して動画ファイルからサムネイルを生成します。
"""
import os
import cv2
import glob
import subprocess


class ImgToVideo:
    def images_to_video(image_dir, output_video, fps=1):
        """画像を動画に変換"""
        images = sorted(glob.glob(os.path.join(image_dir, "*.png")))
        if not images:
            print("No images found in directory")
            return

        frame = cv2.imread(images[0])
        height, width, _ = frame.shape

        fourcc = cv2.VideoWriter_fourcc(*"mp4v")
        video = cv2.VideoWriter(
            output_video, fourcc, fps, (width, height))

        for image in images:
            frame = cv2.imread(image)
            video.write(frame)

        video.release()
        print(f"Video saved: {output_video}")

    def images_to_video_ffmpeg(image_dir, output_video, fps=1):
        """画像を動画に変換（ffmpegを使用）"""
        input_pattern = os.path.join(
            image_dir, "page-%03d.png")  # 例: page-001.png, page-002.png
        cmd = [
            "ffmpeg",
            "-y",  # 既存ファイルを上書き
            "-framerate", str(fps),  # フレームレート
            "-i", input_pattern,  # 入力画像パターン
            "-c:v", "libx264",  # H.264コーデック
            "-pix_fmt", "yuv420p",  # 再生互換性のためのピクセルフォーマット
            output_video
        ]
        try:
            subprocess.run(cmd, check=True)
            print(f"Video created: {output_video}")
        except subprocess.CalledProcessError as e:
            print(f"Error occurred during ffmpeg execution: {e}")
