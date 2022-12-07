#!/usr/bin/env python3
from collections.abc import Awaitable
from collections.abc import Callable
from collections.abc import Mapping
from typing import Any

import databases
import pydantic
import starlette.routing
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from noapi import controllers
from noapi import models
from noapi._typing import Specification
from noapi.services.sql import dsn


def get_http_method(method: controllers.Method) -> str:
    return {
        controllers.Method.GET_MANY: "GET",
        controllers.Method.GET_ONE: "GET",
        controllers.Method.POST: "POST",
        controllers.Method.PATCH: "PATCH",
        controllers.Method.DELETE: "DELETE",
    }[method]


def create_endpoint(
    resource_def: Mapping[str, Any],
    method: controllers.Method,
    model: type[models.BaseModel],
) -> APIRoute:
    # TODO: maybe there should be another layer of abstraction here?
    # this looks like shit

    resource_name = resource_def["name"]

    if method == controllers.Method.GET_ONE:
        endpoint_function = controllers.create_get_one_function(resource_def, model)
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.GET_MANY:
        endpoint_function = controllers.create_get_many_function(resource_def, model)
        path = f"/{resource_name.lower()}"
        response_model = list[type[model]]
        print(response_model)
    elif method == controllers.Method.POST:
        endpoint_function = controllers.create_post_function(resource_def, model)
        path = f"/{resource_name.lower()}"
        response_model = model
    elif method == controllers.Method.PATCH:
        endpoint_function = controllers.create_patch_function(resource_def, model)
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.DELETE:
        endpoint_function = controllers.create_delete_function(resource_def, model)
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    else:
        raise ValueError(f"Unknown method: {method}")

    return APIRoute(
        path=path,
        endpoint=endpoint_function,
        methods=[get_http_method(method)],
        summary=f"{method} {resource_name}",
        tags=[resource_name],
        operation_id=f"{method}_{resource_name}",
        response_model=response_model,
    )


def create_startup_event(
    api: FastAPI,
    service_definition: Mapping[str, Any],
) -> Callable[[], Awaitable[None]]:
    async def on_startup() -> None:
        match service_definition["type"]:
            case "sql":
                service = databases.Database(
                    dsn(
                        driver=service_definition["driver"],
                        user=service_definition["user"],
                        password=service_definition["password"],
                        host=service_definition["host"],
                        port=service_definition["port"],
                        database=service_definition["database"],
                    )
                )
                await service.connect()
                api.state.database_client = service
            case _:
                raise ValueError(f"Unknown service type: {service_definition['type']}")

    return on_startup


def create_shutdown_event(
    api: FastAPI,
    service_definition: Mapping[str, Any],
) -> Callable[[], Awaitable[None]]:
    async def on_shutdown() -> None:
        match service_definition["type"]:
            case "sql":
                await api.state.database_client.disconnect()
                del api.state.database_client
            case _:
                raise ValueError(f"Unknown service type: {service_definition['type']}")

    return on_shutdown


# TODO: more accurate model for specification
def main(specification: Specification) -> int:
    routes: list[starlette.routing.BaseRoute] = []

    for resource_def in specification["resources"]:
        # TODO: this creates the models in the pydantic.main namespace which
        #       *might* be a problem
        resource_model = pydantic.create_model(
            resource_def["name"],
            **resource_def["model"],
            __base__=models.BaseModel,
        )

        for method in map(controllers.Method, resource_def["methods"]):
            routes.append(create_endpoint(resource_def, method, resource_model))

    api = FastAPI(routes=routes)

    # set up service initialization & teardown
    for service_def in specification["services"]:
        api.on_event("startup")(create_startup_event(api, service_def))
        api.on_event("shutdown")(create_shutdown_event(api, service_def))

    uvicorn.run(api)

    return 0
