from pydantic import dataclasses
from pydantic.dataclasses import dataclass

@dataclass
class ASGI:
    version: str
    spec_version: str = dataclasses.Field(default="2.0")