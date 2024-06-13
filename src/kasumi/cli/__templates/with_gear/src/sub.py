import kasumi
from kasumi import Gear
from starlette.requests import Request
from starlette.responses import JSONResponse

router = Gear(prefix="/")