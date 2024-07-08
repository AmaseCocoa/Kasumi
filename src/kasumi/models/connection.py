from pydantic import dataclasses
from pydantic.dataclasses import dataclass

@dataclass
class Client:
    host: str | None = dataclasses.Field(default=None)
    port: int | None = dataclasses.Field(default=None)
    
@dataclass
class Server:
    host: str | None = dataclasses.Field(default=None)
    port: int | None = dataclasses.Field(default=None)