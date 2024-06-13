from importlib.metadata import version

from starlette.requests import Request

from . import responses
from .applications import Kasumi
from .gear import Gear

__version__ = version("kasumi")
