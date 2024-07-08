from importlib.metadata import version
from importlib.metadata import PackageNotFoundError

from starlette.requests import Request

from . import responses
from .applications import Kasumi
from .gear import Gear
from .websocket import WebSocket

try:
    __version__ = version("kasumi")
except PackageNotFoundError:
    __version__ = "0.0.0"