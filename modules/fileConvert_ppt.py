""" 
PowerPointのCOMオブジェクトを使用してプレゼンテーションをビデオとしてエクスポートします。
pywin32 ライブラリを使用
"""
import time
import win32com.client
from pathlib import Path
import os
import shutil
from pathlib import Path
import win32com.client


class PowerPointConverter:
    def convert_ppt_to_images(self, ppt_path):
        """PPTX/PPSXをシーケンス画像に変換し、1ページ目をサムネイルとして生成します。"""
        try:
            ppt_path = Path(ppt_path)
            output_dir = ppt_path.parent / f"{ppt_path.stem}_sequence"
            output_dir.mkdir(parents=True, exist_ok=True)

            # PowerPointアプリケーションの起動
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            powerpoint.Visible = True

            # プレゼンテーションを開く
            presentation = powerpoint.Presentations.Open(
                str(ppt_path), WithWindow=False)

            for index, slide in enumerate(presentation.Slides, start=1):
                output_image = output_dir / f"page-{index:03d}.png"
                slide.Export(str(output_image), "PNG")
                print(f"Saved slide {index} as {output_image}")

            # 最初のスライドをサムネイルとしてコピー
            first_page = output_dir / "page-001.png"
            thumbnail_path = ppt_path.parent / f"{ppt_path.stem}_thumbnail.png"
            if first_page.exists():
                shutil.copy(first_page, thumbnail_path)
                print(f"Thumbnail saved: {thumbnail_path}")

            # プレゼンテーションを閉じる
            presentation.Close()
            powerpoint.Quit()

            return output_dir
        except Exception as e:
            print(f"Error converting PowerPoint to images: {e}")
            raise

    def export_ppt_to_video(self, folder_path, output_folder, slide_duration=5, resolution=1080, frame_rate=30, event_handler=None):
        powerpoint = None
        try:
            powerpoint = win32com.client.Dispatch("PowerPoint.Application")
            powerpoint.Visible = True

            output_folder = Path(output_folder)
            output_folder.mkdir(parents=True, exist_ok=True)

            files = [f for f in Path(folder_path).iterdir()
                     if f.suffix.lower() in ['.pptx', '.ppsx']]

            if not files:
                print(f"No PowerPoint files found in {folder_path}")
                return

            for file in files:
                presentation = None
                try:
                    print(f"Processing {file}...")

                    # プレゼンテーションを開く
                    presentation = powerpoint.Presentations.Open(
                        str(file), True, False, False)

                    # スライドごとの表示時間を設定
                    for slide in presentation.Slides:
                        if not slide.SlideShowTransition.AdvanceOnTime:
                            slide.SlideShowTransition.AdvanceTime = slide_duration
                        slide.SlideShowTransition.AdvanceOnTime = True  # 時間経過で自動進行

                    # 出力先のMP4ファイルパス
                    output_path = output_folder / f"{file.stem}.mp4"
                    print(f"Exporting to {output_path}...")

                    # ビデオとしてエクスポート
                    presentation.CreateVideo(
                        FileName=str(output_path),
                        UseTimingsAndNarrations=True,  # スライド時間設定を使用
                        DefaultSlideDuration=slide_duration  # タイミングがないスライドのデフォルト時間
                    )
                    print("CreateVideo called.")

                    # エクスポートが完了するまで待機（最大600秒）
                    timeout = 600
                    elapsed = 0
                    EXPORT_COMPLETE_STATUS = 3
                    CHECK_INTERVAL = 5  # seconds

                    while presentation.CreateVideoStatus != EXPORT_COMPLETE_STATUS and elapsed < timeout:
                        time.sleep(CHECK_INTERVAL)
                        elapsed += CHECK_INTERVAL
                        print(f"Waiting... Elapsed time: {elapsed} seconds. CreateVideoStatus: {
                              presentation.CreateVideoStatus}")

                except Exception as e:
                    print(f"Error processing {file}: {e}")

                finally:
                    if presentation:
                        presentation.Close()
                    print("Finished processing.")

        except Exception as e:
            print(f"Error with PowerPoint Application: {e}")

        finally:
            if powerpoint:
                powerpoint.Quit()
            print("Quitting PowerPoint application.")
