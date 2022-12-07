from typing import Any
from typing import Literal
from typing import TypedDict

ResourceIdentifier = Any


class Service(TypedDict):
    name: str
    type: str
    driver: str
    user: str
    password: str
    host: str
    port: int
    database: str


class Resource(TypedDict):
    name: str
    table_name: str
    methods: list[Literal["get_many", "get_one", "post", "patch", "delete"]]
    model: dict[str, tuple[type[Any], Any]]
    backing_service: str


class Specification(TypedDict):
    services: list[Service]
    resources: list[Resource]
