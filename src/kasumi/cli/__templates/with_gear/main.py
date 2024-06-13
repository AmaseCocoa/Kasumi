import kasumi
from kasumi import Kasumi
from starlette.requests import Request
from starlette.responses import JSONResponse

from src.sub import router

app = Kasumi()
app.include_gear(router)

@app.get("/")
async def root(request: Request):
    return JSONResponse({"Hello": "World"})