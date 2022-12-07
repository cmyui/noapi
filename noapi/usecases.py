from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypedDict
from typing import TypeVar

from noapi._typing import ResourceIdentifier
from noapi.context import Context
from noapi.errors import ServiceError
from noapi.models import BaseModel
from noapi.repositories import sql  # TODO: user definable

R = TypeVar("R")


# fmt: off
class ResourceUsecases(TypedDict):
    get_one: Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]
    get_many: Callable[[Context, int, int], Awaitable[list[dict[str, Any]] | ServiceError]]
    post: Callable[[Context, BaseModel], Awaitable[dict[str, Any] | ServiceError]]
    patch: Callable[[Context, ResourceIdentifier, BaseModel],Awaitable[dict[str, Any] | ServiceError],]
    delete: Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]
# fmt: on


def get_for_resource(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> ResourceUsecases:
    return {
        "get_one": create_get_one_function(resource_def, model),
        "get_many": create_get_many_function(resource_def, model),
        "post": create_post_function(resource_def, model),
        "patch": create_patch_function(resource_def, model),
        "delete": create_delete_function(resource_def, model),
    }


def create_get_one_function(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]:
    repository = sql.get_for_resource(resource_def, model)

    async def get_one(
        ctx: Context, id: ResourceIdentifier
    ) -> dict[str, Any] | ServiceError:
        data = await repository["get_one"](ctx, id)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return get_one


def create_get_many_function(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> Callable[[Context, int, int], Awaitable[list[dict[str, Any]] | ServiceError]]:
    repository = sql.get_for_resource(resource_def, model)

    async def get_many(
        ctx: Context, page: int, page_size: int
    ) -> list[dict[str, Any]] | ServiceError:
        data = await repository["get_many"](ctx, page, page_size)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return get_many


def create_post_function(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> Callable[[Context, BaseModel], Awaitable[dict[str, Any] | ServiceError]]:
    repository = sql.get_for_resource(resource_def, model)

    async def post(ctx: Context, obj: BaseModel) -> dict[str, Any] | ServiceError:
        data = await repository["post"](ctx, obj)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return post


def create_patch_function(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> Callable[
    [Context, ResourceIdentifier, BaseModel], Awaitable[dict[str, Any] | ServiceError]
]:
    repository = sql.get_for_resource(resource_def, model)

    async def patch(
        ctx: Context, id: ResourceIdentifier, obj: BaseModel
    ) -> dict[str, Any] | ServiceError:
        data = await repository["patch"](ctx, id, obj)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return patch


def create_delete_function(
    resource_def: Mapping[str, Any], model: type[BaseModel]
) -> Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | ServiceError]]:
    repository = sql.get_for_resource(resource_def, model)

    async def delete(
        ctx: Context, id: ResourceIdentifier
    ) -> dict[str, Any] | ServiceError:
        data = await repository["delete"](ctx, id)
        if data is None:
            return ServiceError.RESOURCE_NOT_FOUND

        return data

    return delete
