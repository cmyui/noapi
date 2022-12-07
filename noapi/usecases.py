from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from typing import Any
from typing import TypedDict
from typing import TypeVar

from noapi import repositories
from noapi._typing import ResourceIdentifier
from noapi.errors import ServiceError
from noapi.models import BaseModel

R = TypeVar("R")


class ResourceUsecases(TypedDict):
    get_one: Callable[[ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]
    get_many: Callable[[int, int], Awaitable[list[dict[str, Any]] | ServiceError]]
    post: Callable[[BaseModel], Awaitable[dict[str, Any] | ServiceError]]
    patch: Callable[
        [ResourceIdentifier, BaseModel], Awaitable[dict[str, Any] | ServiceError]
    ]
    delete: Callable[[ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]


def get_for_resource(resource: str, model: BaseModel) -> ResourceUsecases:
    return {
        "get_one": create_get_one_function(resource, model),
        "get_many": create_get_many_function(resource, model),
        "post": create_post_function(resource, model),
        "patch": create_patch_function(resource, model),
        "delete": create_delete_function(resource, model),
    }


def create_get_one_function(
    resource: str, model: BaseModel
) -> Callable[[ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]:
    repository = repositories.get_for_resource(resource, model)

    async def get_one(id: ResourceIdentifier) -> dict[str, Any] | ServiceError:
        data = await repository["get_one"](id)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return get_one


def create_get_many_function(
    resource: str, model: BaseModel
) -> Callable[[int, int], Awaitable[list[dict[str, Any]] | ServiceError]]:
    repository = repositories.get_for_resource(resource, model)

    async def get_many(
        page: int, page_size: int
    ) -> list[dict[str, Any]] | ServiceError:
        data = await repository["get_many"](page, page_size)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return get_many


def create_post_function(
    resource: str, model: BaseModel
) -> Callable[[BaseModel], Awaitable[dict[str, Any] | ServiceError]]:
    repository = repositories.get_for_resource(resource, model)

    async def post(obj: BaseModel) -> dict[str, Any] | ServiceError:
        data = await repository["post"](obj)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return post


def create_patch_function(
    resource: str, model: BaseModel
) -> Callable[
    [ResourceIdentifier, BaseModel], Awaitable[dict[str, Any] | ServiceError]
]:
    repository = repositories.get_for_resource(resource, model)

    async def patch(
        id: ResourceIdentifier, obj: BaseModel
    ) -> dict[str, Any] | ServiceError:
        data = await repository["patch"](id, obj)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return patch


def create_delete_function(
    resource: str, model: BaseModel
) -> Callable[[ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]:
    repository = repositories.get_for_resource(resource, model)

    async def delete(id: ResourceIdentifier) -> dict[str, Any] | ServiceError:
        data = await repository["delete"](id)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return delete
