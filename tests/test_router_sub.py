from kasumi import Gear, Request
from kasumi.responses import JSONResponse

gear = Gear()

@gear.post("/gear")
async def post(request: Request):
    return JSONResponse({"message": "POST Response from gear!"})

@gear.get("/gear")
async def get(request: Request):
    return JSONResponse({"message": "GET Response from gear!"})