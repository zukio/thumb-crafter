import asyncio
import signal

key = "ExistingInstance"


async def handle_client(reader, writer):
    writer.write(key.encode())
    await writer.drain()
    writer.close()


async def start_server(port, _key):
    global key
    key = _key
    server = await asyncio.start_server(
        handle_client, 'localhost', port)

    addr = server.sockets[0].getsockname()
    # print(f'Serving on {addr}')

    try:
        async with server:
            await server.serve_forever()
    except asyncio.CancelledError:
        print("Server task cancelled.")
    finally:
        # サーバーを明示的に閉じる
        server.close()
        try:
            await server.wait_closed()
        except AttributeError:
            # サーバーがすでにNoneの場合、エラーを無視
            pass

# async def async_handle_client(reader, writer):
#    data = await reader.read(100)
#    message = data.decode()
#    addr = writer.get_extra_info('peername')
#    print(f"Received {message!r} from {addr!r}")
#
#    # クライアントからの接続に対する処理
#    response = key  # 既に起動している場合は適切なレスポンスを返す
#
#    writer.write(response.encode())
#    await writer.drain()
#
#    writer.close()


# asyncio.run(start_server( ))
