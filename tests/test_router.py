from multiprocessing import Process
import socket
import random

import pytest
import uvicorn
from httpx import AsyncClient, ASGITransport
from kasumi import Kasumi, Request
from kasumi.responses import JSONResponse

from tests.test_router_sub import gear

app = Kasumi()
app.include_gear(gear)

def is_port_in_use(port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('localhost', port)) == 0

def get_random_port() -> int:
    while True:
        port = random.randint(1024, 65535)
        if not is_port_in_use(port):
            return port

port = get_random_port()

@app.err(404)
async def not_found(request: Request):
    return JSONResponse({"message": "404 Not Found"}, status_code=404)

@app.get("/")
async def get(request: Request):
    return JSONResponse({"message": "This is GET Request"})

@app.post("/")
async def post(request: Request):
    return JSONResponse({"message": "This is POST Request"})

@pytest.fixture(scope="module")
def uvicorn_server():
    config = uvicorn.Config(app, host="127.0.0.1", port=port, log_level="info")
    server = uvicorn.Server(config)
    process = Process(target=server.run)
    process.start()
    socket_getaddrinfo = socket.getaddrinfo

    def getaddrinfo(host, *args, **kwargs):
        if host.endswith(".localhost"):
            return socket_getaddrinfo("127.0.0.1", *args, **kwargs)
        return socket_getaddrinfo(host, *args, **kwargs)

    socket.getaddrinfo = getaddrinfo
    yield
    process.terminate()
    process.join()

@pytest.mark.asyncio
async def test_get():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://127.0.0.1:{str(port)}") as ac:
        response = await ac.get("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is GET Request"}

@pytest.mark.asyncio
async def test_post():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://127.0.0.1:{str(port)}") as ac:
        response = await ac.post("/")
    assert response.status_code == 200
    assert response.json() == {"message": "This is POST Request"}

@pytest.mark.asyncio
async def test_get_gear():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://127.0.0.1:{str(port)}") as ac:
        response = await ac.get("/gear")
    assert response.status_code == 200
    assert response.json() == {"message": "GET Response from gear!"}

@pytest.mark.asyncio
async def test_post_gear():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://127.0.0.1:{str(port)}") as ac:
        response = await ac.post("/gear")
    assert response.status_code == 200
    assert response.json() == {"message": "POST Response from gear!"}

@pytest.mark.asyncio
async def test_404():
    async with AsyncClient(transport=ASGITransport(app=app), base_url=f"http://127.0.0.1:{str(port)}") as ac:
        response = await ac.get("/nonexistent")
    assert response.status_code == 404
    assert response.json() == {"message": "404 Not Found"}
