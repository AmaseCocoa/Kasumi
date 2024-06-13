import kasumi
from kasumi import Kasumi
from starlette.requests import Request
from starlette.responses import JSONResponse

app = Kasumi()

@app.get("/")
async def root(request: Request):
    return JSONResponse({"Hello": "World"})