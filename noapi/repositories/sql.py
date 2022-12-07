from __future__ import annotations

from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any
from typing import TypedDict
from typing import TypeVar

from noapi._typing import ResourceIdentifier
from noapi.context import Context
from noapi.models import BaseModel

R = TypeVar("R")

# TODO: how will we handle different backing services?


class ResourceRepository(TypedDict):
    get_one: Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | None]]
    get_many: Callable[[Context, int, int], Awaitable[list[dict[str, Any]]]]
    post: Callable[[Context, BaseModel], Awaitable[dict[str, Any]]]
    patch: Callable[[Context, ResourceIdentifier, BaseModel], Awaitable[dict[str, Any]]]
    delete: Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any]]]


def get_for_resource(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> ResourceRepository:
    return {
        "get_one": create_get_one_function(resource_def, model_cls),
        "get_many": create_get_many_function(resource_def, model_cls),
        "post": create_post_function(resource_def, model_cls),
        "patch": create_patch_function(resource_def, model_cls),
        "delete": create_delete_function(resource_def, model_cls),
    }


def _get_resource_read_params(model_cls: type[BaseModel]) -> list[str]:
    # TODO: make a way to have a model field private?
    return list(model_cls.__fields__.keys())


def _get_resource_write_params(model_cls: type[BaseModel]) -> list[str]:
    return list(model_cls.__fields__.keys())


def create_get_one_function(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any] | None]]:
    read_params = _get_resource_read_params(model_cls)

    query = f"""\
        SELECT {", ".join(read_params)}
          FROM {resource_def["table_name"]}
         WHERE id = :id
    """

    async def get_one(
        ctx: Context,
        id: ResourceIdentifier,
    ) -> dict[str, Any] | None:
        params = {
            "id": id,
        }
        rec = await ctx.database_client.fetch_one(query, params)
        return dict(rec._mapping) if rec is not None else None

    return get_one


def create_get_many_function(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> Callable[[Context, int, int], Awaitable[list[dict[str, Any]]]]:
    read_params = _get_resource_read_params(model_cls)

    query = f"""\
        SELECT {", ".join(read_params)}
          FROM {resource_def["table_name"]}
         LIMIT :limit
        OFFSET :offset
    """

    async def get_many(
        ctx: Context,
        page: int,
        page_size: int,
    ) -> list[dict[str, Any]]:
        params = {
            "limit": page_size,
            "offset": (page - 1) * page_size,
        }
        recs = await ctx.database_client.fetch_all(query, params)
        return [dict(rec._mapping) for rec in recs]

    return get_many


def create_post_function(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> Callable[[Context, BaseModel], Awaitable[dict[str, Any]]]:
    write_params = _get_resource_write_params(model_cls)
    read_params = _get_resource_read_params(model_cls)

    query = f"""\
        INSERT INTO {resource_def["name"]} ({", ".join(write_params)})
             VALUES ({", ".join(f":{k}" for k in model_cls.__fields__)})
    """

    read_query = f"""\
        SELECT {", ".join(read_params)}
          FROM {resource_def["table_name"]}
         WHERE id = :id
    """

    async def post(
        ctx: Context,
        data: BaseModel,
    ) -> dict[str, Any]:
        params = data.dict()
        id = await ctx.database_client.execute(query, params)
        assert id is not None

        params = {
            "id": id,
        }
        rec = await ctx.database_client.fetch_one(read_query, params)
        assert rec is not None
        return dict(rec._mapping)

    return post


def create_patch_function(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> Callable[[Context, ResourceIdentifier, BaseModel], Awaitable[dict[str, Any]]]:
    write_params = _get_resource_write_params(model_cls)
    read_params = _get_resource_read_params(model_cls)

    query = f"""\
        UPDATE {resource_def["table_name"]}
           SET {", ".join(f"{k} = :{k}" for k in write_params)}
         WHERE id = :id
    """

    read_query = f"""\
        SELECT {", ".join(read_params)}
          FROM {resource_def["table_name"]}
         WHERE id = :id
    """

    async def patch(
        ctx: Context,
        id: ResourceIdentifier,
        data: BaseModel,
    ) -> dict[str, Any]:
        params = data.dict()
        params["id"] = id
        await ctx.database_client.execute(query, params)

        params = {
            "id": id,
        }
        rec = await ctx.database_client.fetch_one(read_query, params)
        assert rec is not None
        return dict(rec._mapping)

    return patch


def create_delete_function(
    resource_def: Mapping[str, Any], model_cls: type[BaseModel]
) -> Callable[[Context, ResourceIdentifier], Awaitable[dict[str, Any]]]:
    read_params = _get_resource_read_params(model_cls)

    query = f"""\
        DELETE FROM {resource_def["table_name"]}
              WHERE id = :id
    """

    read_query = f"""\
        SELECT {", ".join(read_params)}
          FROM {resource_def["table_name"]}
         WHERE id = :id
    """

    async def delete(
        ctx: Context,
        id: ResourceIdentifier,
    ) -> dict[str, Any]:
        params = {
            "id": id,
        }
        rec = await ctx.database_client.fetch_one(read_query, params)
        assert rec is not None
        data = dict(rec._mapping)

        await ctx.database_client.execute(query, params)
        return data

    return delete
