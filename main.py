import os
import sys
import signal
import argparse
import asyncio
from aioconsole import ainput
from watchdog.observers import Observer
from modules.communication.udp_client import DelayedUDPSender as DelayedUDPSenderUDP, hello_server as hello_server_udp
from modules.communication.tcp_client import DelayedTCPSender as DelayedTCPSenderTCP, hello_server as hello_server_tcp
from modules.filehandler import FileHandler
from modules.communication.ipc_client import check_existing_instance
from modules.communication.ipc_server import start_server

# プロセスサーバのタスクハンドルを保持する変数
server_task = None


async def main(args):
    global server_task

    # プロセスサーバのタスクを開始する
    server_task = asyncio.create_task(start_server(12321, "some_key"))

    # ファイルのリストを取得する
    event_handler.list_files(path)

    try:
        # 以下に後続の処理を記述する
        while True:
            command = await ainput("Enter a command exit: ")
            if command.lower() == "exit":
                exit_handler("[Exit] Command Exit")
                break
            await asyncio.sleep(1)

        # プロセスサーバのタスクが完了するまで待機する
        await server_task

    except asyncio.CancelledError:
        # プロセスサーバのタスクがキャンセルされた場合の処理
        pass
    finally:
        # プロセスサーバのクリーンアップ処理（必要な場合は実装）
        if server_task:
            server_task.cancel()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description='Monitor a directory and create thumbnails for video files.')
    parser.add_argument('--exclude_subdirectories', default=False, action='store_true',
                        help='Exclude subdirectories in monitoring and thumbnail creation.')
    parser.add_argument('--target', default='', type=str,
                        help='Directory path to monitor')
    parser.add_argument('--seconds', default=1, type=int,
                        help='Specify the seconds of the frame to be used for thumbnail generation')
    parser.add_argument('--ip', default='localhost', type=str,
                        help='IP address to send the messages')
    parser.add_argument('--port', default=12345, type=int,
                        help='Port number to send the messages')
    parser.add_argument('--delay', default=1, type=int,
                        help='Delay in seconds for sending messages')
    parser.add_argument('--protocol', choices=['none', 'udp', 'tcp'], default='none',
                        help='Communication protocol to use (none, udp, tcp)')
    args = parser.parse_args()

    path = os.path.abspath(args.target) if args.target else os.path.abspath(
        os.path.join(os.getcwd(), os.pardir))

    if check_existing_instance(12321, path):
        print("既に起動しています。")
        sys.exit(0)

    if args.protocol == 'udp':
        sender = DelayedUDPSenderUDP(args.delay)
        hello_server = hello_server_udp
    elif args.protocol == 'tcp':
        sender = DelayedTCPSenderTCP(args.delay)
        hello_server = hello_server_tcp
    else:
        sender = None
        def hello_server(x): return None

    event_handler = FileHandler(
        args.exclude_subdirectories, sender, args.ip, args.port, args.seconds)

    if sender:
        response = hello_server(path)
        if response is not None:
            print(f"Hello {args.protocol.upper()}: " + response)
            if response == "overlapping":
                sys.exit("[Exit] Overlapping")

    observer = Observer()
    observer.schedule(event_handler, path,
                      recursive=not args.exclude_subdirectories)
    observer.start()

    def exit_handler(reason):
        if sender:
            sender.send_message(args.ip, args.port, reason)
        result = event_handler.destroy(reason)
        if server_task:
            server_task.cancel()
        sys.exit(result)

    def exit_wrapper(reason):
        return lambda sig, frame: exit_handler(reason)
    signal.signal(signal.SIGINT, exit_wrapper("[Exit] Signal Interrupt"))

    try:
        asyncio.run(main(args))
    except KeyboardInterrupt:
        observer.stop()
        exit_handler("[Exit] Keyboard Interrupt")
    observer.join()
