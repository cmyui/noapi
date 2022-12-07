import enum
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any

import fastapi
from fastapi import Depends

import noapi.logger as logger
import noapi.rest.responses as responses
from noapi import models
from noapi import usecases as _usecases
from noapi._typing import ResourceIdentifier
from noapi.errors import ServiceError
from noapi.rest.context import RestContext


class Method(str, enum.Enum):
    GET_MANY = "get_many"  # /resource
    GET_ONE = "get_one"  # /resource/{id}
    POST = "post"
    PATCH = "patch"
    DELETE = "delete"


def determine_http_code(error: ServiceError) -> int:
    match error:
        # 4xx
        case ServiceError.RESOURCE_NOT_FOUND:
            return fastapi.status.HTTP_404_NOT_FOUND
        # 5xx
        case ServiceError.RESOURCE_FETCH_FAILED:
            return fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        case ServiceError.RESOURCE_CREATION_FAILED:
            return fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        case ServiceError.RESOURCE_UPDATE_FAILED:
            return fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        case ServiceError.RESOURCE_DELETION_FAILED:
            return fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR
        case _:
            return fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR


def create_get_many_function(
    resource_def: Mapping[str, Any],
    model: type[models.BaseModel],
) -> Callable[[fastapi.Request], Awaitable[fastapi.Response]]:
    usecases = _usecases.get_for_resource(resource_def, model)

    async def function(
        request: fastapi.Request,
        page: int = 1,
        page_size: int = 10,
        ctx: RestContext = Depends(),
    ) -> fastapi.Response:
        usecase = usecases.get("get_many")
        if usecase is None:
            logger.error(
                f"No usecase available to process the incoming request",
                resource_name=resource_def["name"],
                method=Method.GET_MANY,
            )
            return responses.failure(
                error=ServiceError.RESOURCE_FETCH_FAILED,
                message="Failed to fetch resource(s)",
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        data = await usecase(ctx, page, page_size)
        if isinstance(data, ServiceError):
            return responses.failure(
                error=data,
                message="Failed to fetch resource(s)",
                status_code=determine_http_code(data),
            )

        resp = [model.from_mapping(rec) for rec in data]

        return responses.success(
            data=resp,
            status_code=fastapi.status.HTTP_200_OK,
        )

    return function


def create_get_one_function(
    resource_def: Mapping[str, Any],
    model: type[models.BaseModel],
) -> Callable[[fastapi.Request], Awaitable[fastapi.Response]]:
    usecases = _usecases.get_for_resource(resource_def, model)

    async def function(
        id: ResourceIdentifier,
        ctx: RestContext = Depends(),
    ) -> fastapi.Response:
        usecase = usecases.get("get_one")
        if usecase is None:
            logger.error(
                f"No usecase available to process the incoming request",
                resource_name=resource_def["name"],
                method=Method.GET_ONE,
            )
            return responses.failure(
                error=ServiceError.RESOURCE_FETCH_FAILED,
                message="Failed to fetch resource",
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        data = await usecase(ctx, id)
        if isinstance(data, ServiceError):
            return responses.failure(
                error=data,
                message="Failed to fetch resource",
                status_code=determine_http_code(data),
            )

        resp = model.from_mapping(data)

        return responses.success(
            data=resp,
            status_code=fastapi.status.HTTP_200_OK,
        )

    return function


def create_post_function(
    resource_def: Mapping[str, Any],
    model: type[models.BaseModel],
) -> Callable[[models.BaseModel], Awaitable[fastapi.Response]]:
    usecases = _usecases.get_for_resource(resource_def, model)

    async def function(
        obj: models.BaseModel,
        ctx: RestContext = Depends(),
    ) -> fastapi.Response:
        usecase = usecases.get("post")
        if usecase is None:
            logger.error(
                f"No usecase available to process the incoming request",
                resource_name=resource_def["name"],
                method=Method.POST,
            )
            return responses.failure(
                error=ServiceError.RESOURCE_CREATION_FAILED,
                message="Failed to create resource",
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        data = await usecase(ctx, obj)
        if isinstance(data, ServiceError):
            return responses.failure(
                error=data,
                message="Failed to create resource",
                status_code=determine_http_code(data),
            )

        resp = model.from_mapping(data)

        return responses.success(
            data=resp,
            status_code=fastapi.status.HTTP_200_OK,
        )

    return function


def create_patch_function(
    resource_def: Mapping[str, Any],
    model: type[models.BaseModel],
) -> Callable[[ResourceIdentifier, models.BaseModel], Awaitable[fastapi.Response]]:
    usecases = _usecases.get_for_resource(resource_def, model)

    # TODO: need to type `obj` here dynamically. this might need a refactor?
    # TODO: can i type id here? (do i need to?)
    async def function(
        id: ResourceIdentifier,
        obj: Any,
        ctx: RestContext = Depends(),
    ) -> fastapi.Response:
        usecase = usecases.get("patch")
        if usecase is None:
            logger.error(
                f"No usecase available to process the incoming request",
                resource_name=resource_def["name"],
                method=Method.POST,
            )
            return responses.failure(
                error=ServiceError.RESOURCE_UPDATE_FAILED,
                message="Failed to update resource",
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        data = await usecase(ctx, id, obj)
        if isinstance(data, ServiceError):
            return responses.failure(
                error=data,
                message="Failed to update resource",
                status_code=determine_http_code(data),
            )

        resp = model.from_mapping(data)

        return responses.success(
            data=resp,
            status_code=fastapi.status.HTTP_200_OK,
        )

    return function


def create_delete_function(
    resource_def: Mapping[str, Any],
    model: type[models.BaseModel],
) -> Callable[[fastapi.Request], Awaitable[fastapi.Response]]:
    usecases = _usecases.get_for_resource(resource_def, model)

    # TODO: can i type id here? (do i need to?)
    async def function(
        id: ResourceIdentifier,
        ctx: RestContext = Depends(),
    ) -> fastapi.Response:
        usecase = usecases.get("delete")
        if usecase is None:
            logger.error(
                f"No usecase available to process the incoming request",
                resource_name=resource_def["name"],
                method=Method.POST,
            )
            return responses.failure(
                error=ServiceError.RESOURCE_DELETION_FAILED,
                message="Failed to delete resource",
                status_code=fastapi.status.HTTP_500_INTERNAL_SERVER_ERROR,
            )

        data = await usecase(ctx, id)
        if isinstance(data, ServiceError):
            return responses.failure(
                error=data,
                message="Failed to delete resource",
                status_code=determine_http_code(data),
            )

        resp = model.from_mapping(data)

        return responses.success(
            data=resp,
            status_code=fastapi.status.HTTP_200_OK,
        )

    return function
