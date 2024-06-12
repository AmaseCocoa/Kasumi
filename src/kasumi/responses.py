import typing

from starlette.background import BackgroundTask
from starlette.responses import FileResponse as FileResponse
from starlette.responses import HTMLResponse as HTMLResponse
from starlette.responses import PlainTextResponse as PlainTextResponse
from starlette.responses import RedirectResponse as RedirectResponse
from starlette.responses import Response
from starlette.responses import StreamingResponse as StreamingResponse

try:
    import orjson
    orjson_available = True
except ModuleNotFoundError:
    import json
    orjson_available = False

class JSONResponse(Response):
    media_type = "application/json"

    def __init__(
        self,
        content: typing.Any,
        status_code: int = 200,
        headers: typing.Mapping[str, str] | None = None,
        media_type: str | None = None,
        background: BackgroundTask | None = None,
        use_orjson: bool = True
    ) -> None:
        super().__init__(content, status_code, headers, media_type, background)
        self.use_orjson = use_orjson

    def render(self, content: typing.Any) -> bytes:
        if self.use_orjson:
            if orjson_available:
                dp = orjson.dumps(
                    content, 
                    option=orjson.OPT_NON_STR_KEYS | orjson.OPT_SERIALIZE_NUMPY
                )
            else:
                dp = json.dumps(
                    content,
                    ensure_ascii=False,
                    allow_nan=False,
                    indent=None,
                    separators=(",", ":"),
                ).encode("utf-8")
        else:
            dp = json.dumps(
                content,
                ensure_ascii=False,
                allow_nan=False,
                indent=None,
                separators=(",", ":"),
            ).encode("utf-8")
        return dp