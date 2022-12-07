#!/usr/bin/env python3
from collections.abc import Mapping
from typing import Any

import fastapi
import pydantic
import starlette.routing
import uvicorn

from noapi import controllers
from noapi import models

# GET /resources/{id}
# GET /resources?{field}=abc&page=1&page_size=10
# POST /resources
# PATCH /resources/{id}
# DELETE /resources/{id}


def get_http_method(method: controllers.Method) -> str:
    return {
        controllers.Method.GET_MANY: "GET",
        controllers.Method.GET_ONE: "GET",
        controllers.Method.POST: "POST",
        controllers.Method.PATCH: "PATCH",
        controllers.Method.DELETE: "DELETE",
    }[method]


def create_endpoint(
    resource_name: str,
    resource: dict[str, Any],
    method: controllers.Method,
    model: models.BaseModel,
) -> fastapi.routing.APIRoute:
    if method == controllers.Method.GET_ONE:
        endpoint_function = controllers.create_get_one_function(
            resource_name,
            resource["model"],
        )
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.GET_MANY:
        endpoint_function = controllers.create_get_many_function(
            resource_name,
            resource["model"],
        )
        path = f"/{resource_name.lower()}"
        response_model = list[type(model)]  # TODO: does this work? lol
        print(response_model)
    elif method == controllers.Method.POST:
        endpoint_function = controllers.create_post_function(
            resource_name,
            resource["model"],
        )
        path = f"/{resource_name.lower()}"
        response_model = model
    elif method == controllers.Method.PATCH:
        endpoint_function = controllers.create_patch_function(
            resource_name,
            resource["model"],
        )
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.DELETE:
        endpoint_function = controllers.create_delete_function(
            resource_name,
            resource["model"],
        )
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    else:
        raise ValueError(f"Unknown method: {method}")

    return fastapi.routing.APIRoute(
        path=path,
        endpoint=endpoint_function,
        methods=[get_http_method(method)],
        summary=f"{method} {resource_name}",
        tags=[resource_name],
        operation_id=f"{method}_{resource_name}",
        response_model=response_model,
    )


def main(resources: Mapping[str, Any]) -> int:
    routes: list[starlette.routing.BaseRoute] = []

    for resource, resource_def in resources.items():
        resource_model = pydantic.create_model(
            resource,
            **resource_def["model"],
            __base__=models.BaseModel,
        )

        for method in resource_def["methods"]:
            if method == controllers.Method.GET_ONE:
                endpoint_function = controllers.create_get_one_function(
                    resource,
                    resource_model,
                )
                path = f"/{resource.lower()}/{{id}}"
                response_model = resource_model
            elif method == controllers.Method.GET_MANY:
                endpoint_function = controllers.create_get_many_function(
                    resource,
                    resource_model,
                )
                path = f"/{resource.lower()}"
                response_model = list[type[resource_model]]
            elif method == controllers.Method.POST:
                endpoint_function = controllers.create_post_function(
                    resource,
                    resource_model,
                )
                path = f"/{resource.lower()}"
                response_model = resource_model
            elif method == controllers.Method.PATCH:
                endpoint_function = controllers.create_patch_function(
                    resource,
                    resource_model,
                )
                path = f"/{resource.lower()}/{{id}}"
                response_model = resource_model
            elif method == controllers.Method.DELETE:
                endpoint_function = controllers.create_delete_function(
                    resource,
                    resource_model,
                )
                path = f"/{resource.lower()}/{{id}}"
                response_model = resource_model
            else:
                raise ValueError(f"Unknown method: {method}")

            routes.append(
                fastapi.routing.APIRoute(
                    path=path,
                    endpoint=endpoint_function,
                    methods=[get_http_method(method)],
                    summary=f"{method} {resource}",
                    tags=[resource],
                    operation_id=f"{method}_{resource}",
                    response_model=response_model,
                )
            )

    api = fastapi.FastAPI(routes=routes)
    uvicorn.run(api)

    return 0
