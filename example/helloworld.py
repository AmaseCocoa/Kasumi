from kasumi import Kasumi
from starlette.requests import Request
from starlette.responses import JSONResponse

app = Kasumi()

@app.post("/")
async def root(request: Request):
    return JSONResponse({"Hello": "World"})