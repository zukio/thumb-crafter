""" 
PowerPointのCOMオブジェクトを使用してプレゼンテーションをビデオとしてエクスポートします。
pywin32 ライブラリを使用
"""
import time
import win32com.client
from pathlib import Path


def export_ppt_to_video(folder_path, output_folder, slide_duration=5, resolution=1080, frame_rate=30, event_handler=None):
    """
    PowerPointプレゼンテーションをビデオとしてエクスポートし、生成された動画に対してon_createdを呼び出します。

    Args:
        folder_path (str): PowerPointファイルのあるフォルダパス
        output_path (str): 出力先フォルダパス
        slide_duration (int): 各スライドの表示時間（秒）
        resolution (int): 出力動画の解像度（縦ピクセル）
        frame_rate (int): フレームレート
    """
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

    powerpoint.Quit()
    print("Quitting PowerPoint application.")
