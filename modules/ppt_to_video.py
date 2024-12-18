""" 
PowerPointのCOMオブジェクトを使用してプレゼンテーションをビデオとしてエクスポートします。
pywin32 ライブラリを使用
"""
import time
import win32com.client
from pathlib import Path


def export_ppt_to_video(folder_path, output_folder, resolution=1080, frame_rate=30):
    """PowerPointプレゼンテーションをビデオとしてエクスポートします。"""
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
        try:
            print(f"Processing {file}...")

            presentation = powerpoint.Presentations.Open(
                str(file), True, False, False)
            output_path = output_folder / f"{file.stem}.mp4"
            print(f"Exporting to {output_path}...")

            presentation.CreateVideo(str(output_path), resolution, frame_rate)
            print("CreateVideo called.")

            # エクスポートが完了するまで待機（最大600秒）
            timeout = 600
            elapsed = 0

            while presentation.CreateVideoStatus != 3 and elapsed < timeout:
                time.sleep(5)
                elapsed += 5
                print(f"Waiting... Elapsed time: {elapsed} seconds. CreateVideoStatus: {
                      presentation.CreateVideoStatus}")

            if presentation.CreateVideoStatus == 3:
                print(f"Exported to {output_path}")
            else:
                print(f"Warning: Export may not have completed for {
                      file.name}")

            presentation.Close()
        except Exception as e:
            print(f"Error processing {file}: {e}")
        finally:
            # 確実にPowerPointを終了する
            if 'presentation' in locals() and not presentation.Saved:
                presentation.Close()

    print("Quitting PowerPoint application.")
    powerpoint.Quit()
