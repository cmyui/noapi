from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import TypedDict
from typing import TypeVar

from noapi._typing import ResourceIdentifier
from noapi.models import BaseModel

R = TypeVar("R")

# TODO: how will we handle different backing services?


class ResourceRepository(TypedDict):
    get_one: Callable[[ResourceIdentifier], Awaitable[dict[str, Any]]]
    get_many: Callable[[int, int], Awaitable[list[dict[str, Any]]]]
    post: Callable[[BaseModel], Awaitable[dict[str, Any]]]
    patch: Callable[[ResourceIdentifier, BaseModel], Awaitable[dict[str, Any]]]
    delete: Callable[[ResourceIdentifier], Awaitable[dict[str, Any]]]


def get_for_resource(resource: str, model: type[BaseModel]) -> ResourceRepository:
    return {
        "get_one": create_get_one_function(resource, model),
        "get_many": create_get_many_function(resource, model),
        "post": create_post_function(resource, model),
        "patch": create_patch_function(resource, model),
        "delete": create_delete_function(resource, model),
    }


def create_get_one_function(
    resource: str, model: type[BaseModel]
) -> Callable[[ResourceIdentifier], Awaitable[dict[str, Any]]]:
    async def get_one(id: ResourceIdentifier) -> dict[str, Any]:
        return {"id": 1, "name": "foo"}

    return get_one


def create_get_many_function(
    resource: str, model: type[BaseModel]
) -> Callable[[int, int], Awaitable[list[dict[str, Any]]]]:
    async def get_many(page: int, page_size: int) -> list[dict[str, Any]]:
        return [{"id": 1, "name": "foo"}, {"id": 2, "name": "bar"}]

    return get_many


def create_post_function(
    resource: str, model: type[BaseModel]
) -> Callable[[BaseModel], Awaitable[dict[str, Any]]]:
    async def post(data: BaseModel) -> dict[str, Any]:
        return {"id": 1, "name": "foo"}

    return post


def create_patch_function(
    resource: str, model: type[BaseModel]
) -> Callable[[ResourceIdentifier, BaseModel], Awaitable[dict[str, Any]]]:
    async def patch(id: ResourceIdentifier, data: BaseModel) -> dict[str, Any]:
        return {"id": 1, "name": "foo"}

    return patch


def create_delete_function(
    resource: str, model: type[BaseModel]
) -> Callable[[ResourceIdentifier], Awaitable[dict[str, Any]]]:
    async def delete(id: ResourceIdentifier) -> dict[str, Any]:
        return {"id": 1, "name": "foo"}

    return delete
