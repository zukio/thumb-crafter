# Thumb Crafter UDP

Thumb Crafter UDP は、指定したディレクトリ内の動画ファイルを監視し、動画の最初のフレームをサムネイルとして生成するツールです。また、動画ファイルの追加、変更、削除のイベント情報を UDP メッセージとして送信します。

## Features

- 指定したディレクトリ内の動画ファイルを監視し、新しい動画ファイルが追加されたときにサムネイルを生成します。
- 監視対象の動画ファイルの変更（更新）があった場合にもサムネイルを再生成します。
- 動画ファイルが削除された場合には、サムネイルも削除します。
- 動画ファイルの追加、変更、削除のイベント情報を UDP メッセージとして指定した IP アドレスとポートに送信します。

## EX版 追加の機能

- タスクトレイアイコンから設定の変更、アプリケーションの終了が可能です。

- PDFからシーケンス画像生成

  PDFファイルをシーケンス画像に変換し、1ページ目をサムネイルとして設定します。
  PDFごとに個別のシーケンスフォルダを作成し管理します。

- PowerPointファイルの自動ビデオ化

  PowerPointが使用できる環境であれば、PowerPoint（PPTX、PPSX）ファイルをMP4ビデオに変換し、動画からサムネイルを生成します。解像度やフレームレートの指定も可能です。

## Download and Installation

1. リリースページから最新のバージョンの exe ファイルをダウンロードします。

   [リリースページへ移動](https://github.com/zukio/thumb-crafter/releases/tag/udpexe1.0)

2. 監視対象ディレクトリに「thumb_crafter」フォルダを作成し、ダウンロードした exe ファイルを保存します。

3. FFMpeg ツールをインストールします。以下のサイトから適切なバージョンをダウンロードし、インストーラを実行します。

   FFMpeg 公式サイト：[https://ffmpeg.org/](https://ffmpeg.org/)

   注：インストールが完了したら、FFMpeg がシステムのパスに追加されているはずです。本アプリは ffmpeg がシステムパスに追加されているか、またはその実行ファイル（ffmpeg.exe）が直接このスクリプトと同じディレクトリに存在することが前提となっています。

## Usage

### Start App

「thumb_craft_ex」を実行すると、ディレクトリの監視を開始します。
終了するには、タスクトレイアイコンをクリックして、「EXIT」を選択します。

### Options

アプリケーション起動した後、タスクトレイアイコンをクリックして「Settings」を選択することでオプション設定画面を開くことができます。
初期値は、config.json ファイルを編集することで設定可能です。

または、アプリケーションの exe ファイルを右クリックし、[プロパティ]を開いて、起動時引数を書き加えることで設定可能です：

```shell
thumb_crafter_ex.exe --ignore_subfolders --target <監視対象ディレクトリ> --thumbnail_time_seconds 2 --ip <IPアドレス> --port <ポート番号> --send_interval 3
```

- `--ignore_subfolders`: サブディレクトリの監視を除外します。このオプションを指定すると、指定したディレクトリのみが監視されます。
- `--target`: 監視するディレクトリのパス。相対パスまたは絶対パスを指定することができます。
- `--thumbnail_time_seconds`: サムネイルの生成に使用するフレームの秒数。
- `--ip <IPアドレス>`: UDP メッセージを送信するための宛先 IP アドレスを指定します。
- `--port <ポート番号>`: UDP メッセージを送信するための宛先ポート番号を指定します。
- `--send_interval`: UDP の連投を防ぐため後続のイベントを待機する秒数。
- `--slide_duration`: スライドを動画に変換する場合の1ページあたりの表示秒数。

注：デフォルトでは、IP アドレスは`localhost`、ポート番号は`12345`、後続のイベントを待機する秒数 は `1` 秒間です。

注：--target 引数が指定されなかった場合は、Python プロジェクトフォルダが置かれたディレクトリが監視されます。

注：--thumbnail_time_seconds 引数が指定されなかった場合、またはビデオの長さが指定された秒未満の場合は、最初のフレームが使用されます。

## UDP Format

最初の更新から 1 秒間無更新状態が続いた時点で一度だけ UDP が送信されます。
ファイルの追加・削除が連続して発生した場合でも、連続して UDP が送信されることはありません。

``` json
{
  event:[{ type:event-type, path:filepath }],
  files:video_files
}
```

- __event__: 発生したイベントが新しい順に追加され、1 秒間の無更新状態が続いた時点ですべてのイベントの情報を新しい順に配列にまとめて送信します
- __files__: 動画ファイルが追加・削除されるたびにリストが更新されるため、動画リストは常に最新の状態を保持します。

## Logs

thumb-craft-udp.py スクリプトは、ログファイルに実行ログを出力します。ログファイルは`./logs/`ディレクトリ内に日付ごとに作成されます。ログレベルは INFO です。

## For Custom

未リリースの TCP 版を含む開発ソースを使用するには：

1. リポジトリをクローンします。

   ```shell
   git clone https://github.com/zukio/thumb-crafter.git
   ```

2. プロジェクトのディレクトリに移動します。

   ```shell
   cd thumb-crafter-udp
   ```

3. 必要な Python パッケージをインストールします。

   ```shell
   pip install -r requirements.txt
   ```

4. [FFMpeg](https://ffmpeg.org/) 、[ImageMagick](https://imagemagick.org/script/download.php)ツールをインストールします。ffmpeg と ImageMagick はシステムパスに追加されているか、またはその実行ファイルが直接このスクリプトと同じディレクトリに存在することが前提となっています。

   ※ ImageMagick ツールを使用するには [GhostScript](https://ghostscript.com/releases/gsdnld.html) が必要です。

5. main.py スクリプトを使用して、ディレクトリの監視とサムネイル生成を開始します。

   ```shell
   python main.py --protocol udp --ignore_subfolders --target <監視対象ディレクトリ> --thumbnail_time_seconds 2 --ip <IPアドレス> --port <ポート番号> --send_interval 3
   ```

6. ディレクトリ構成

   ```text
   thumb-crafter
   ├── main.py (エントリーポイント)
   ├── modules
   │   ├── filehandler.py (ファイル操作)
   │   ├── fileConvert_img.py
   │   ├── fileConvert_pdf.py
   │   ├── fileConvert_ppt.py
   │   └── fileGenerate_thumbnail.py
   ├── utils
   │   ├── communication
   │   │   ├── ipc_client.py
   │   │   ├── ipc_server.py
   │   │   ├── tcp_client.py
   │   │   └── udp_client.py
   │   ├── logwriter.py
   │   ├── multiple_window.py
   │   └── multiple_pid.py
   └── tray
       ├── config_dialog.py (設定ダイアログ)
       └── tray_icon.py (タスクトレイの実装)
   ```
