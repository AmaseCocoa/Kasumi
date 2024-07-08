from multiprocessing import Process
import socket
import random
import time

import pytest
import uvicorn
from kasumi import Kasumi, WebSocket
from kasumi.exceptions import ConnectionClosed
from websockets.client import connect
from websockets.exceptions import ConnectionClosedError

app = Kasumi()

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_random_port() -> int:
    while True:
        port = random.randint(1024, 65535)
        if not is_port_in_use(port):
            return port

port = get_random_port()

@app.ws("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            data = await websocket.recv()
            if data:
                await websocket.send_str(f"Message text was: {data.text}")
    except ConnectionClosed:
        pass

@pytest.fixture(scope="module")
def uvicorn_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)
    process = Process(target=server.run)
    process.start()
    time.sleep(1)
    yield
    process.terminate()
    process.join()

@pytest.mark.asyncio
async def test_websocket(uvicorn_server):
    try:
        async with connect(f"ws://127.0.0.1:{port}/ws") as websocket:
            await websocket.send("Hello, WebSocket!")
            response = await websocket.recv()
            assert response == "Message text was: Hello, WebSocket!"
    except ConnectionClosedError:
        pass