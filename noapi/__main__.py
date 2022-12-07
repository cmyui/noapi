#!/usr/bin/env python3
from collections.abc import Mapping
from typing import Any

import pydantic
import starlette.routing
import uvicorn
from fastapi import FastAPI
from fastapi.routing import APIRoute

from noapi import controllers
from noapi import models


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
    method: controllers.Method,
    model: type[models.BaseModel],
) -> APIRoute:
    if method == controllers.Method.GET_ONE:
        endpoint_function = controllers.create_get_one_function(resource_name, model)
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.GET_MANY:
        endpoint_function = controllers.create_get_many_function(resource_name, model)
        path = f"/{resource_name.lower()}"
        response_model = list[type[model]]  # TODO: does this work? lol
        print(response_model)
    elif method == controllers.Method.POST:
        endpoint_function = controllers.create_post_function(resource_name, model)
        path = f"/{resource_name.lower()}"
        response_model = model
    elif method == controllers.Method.PATCH:
        endpoint_function = controllers.create_patch_function(resource_name, model)
        path = f"/{resource_name.lower()}/{{id}}"
        response_model = model
    elif method == controllers.Method.DELETE:
        endpoint_function = controllers.create_delete_function(resource_name, model)
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


def main(resources: Mapping[str, Any]) -> int:
    routes: list[starlette.routing.BaseRoute] = []

    for resource_name, resource in resources.items():
        # TODO: this creates the models in the pydantic.main namespace which
        #       *might* be a problem
        resource_model = pydantic.create_model(
            resource_name,
            **resource["model"],
            __base__=models.BaseModel,
        )

        for method in resource["methods"]:
            routes.append(
                create_endpoint(
                    resource_name,
                    method,
                    resource_model,
                )
            )

    api = FastAPI(routes=routes)
    uvicorn.run(api)

    return 0
