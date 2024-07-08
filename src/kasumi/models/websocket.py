from typing import Callable, Iterable, Tuple, Optional, Union

from pydantic import dataclasses
from pydantic.dataclasses import dataclass
from yarl import URL

from .asgi import ASGI
from .connection import Client, Server

"""
@dataclass()
class WebSocket:
    asgi: ASGI
    url: URL
    json: Callable | None
    path: str
    headers: Iterable[Union[bytes, str, Tuple[bytes, bytes]]]
    client: Client
    server: Server
    subprotocols: Iterable[str]
    state: Optional[dict[str]]

    raw_path: bytes | None = dataclasses.Field(
        default=None)
    http_version: str = dataclasses.Field(
        default="2.0")
    text: str | bytes | None = dataclasses.Field(
        default=None)
    query_string: bytes = dataclasses.Field(
        default=b'')
    root_path: str = dataclasses.Field(
        default='')
"""

@dataclass
class WSMessage:
    text: str | bytes | None = dataclasses.Field(
        default=None)
    json: dict | None = dataclasses.Field(
        default=None)
