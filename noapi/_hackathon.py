#!/usr/bin/env python3
from typing import Any

import fastapi
import requests
import starlette.routing


def get_api_specification() -> dict[str, Any]:
    response = requests.get("https://chat.cmyui.xyz/openapi.json")
    if response.status_code != 200:
        raise RuntimeError(response.text)

    return response.json()


def main() -> int:
    api_spec = get_api_specification()
    major, minor, micro = api_spec["openapi"].split(".")
    assert major == "3"

    routes: list[starlette.routing.BaseRoute] = []

    # components

    # paths
    for path, path_def in api_spec["paths"].items():
        for method, endpoint in path_def.items():

            async def function(
                request: fastapi.Request,
                *args: Any,
                **kwargs: Any,
            ) -> fastapi.Response:
                ...

            routes.append(
                fastapi.routing.APIRoute(
                    path=path,
                    endpoint=function,
                    methods=[method.upper()],
                    summary=endpoint["summary"],
                    tags=endpoint["tags"],
                    operation_id=endpoint["operationId"],
                )
            )

    api = fastapi.FastAPI(
        routes=routes,
    )
    breakpoint()

    return 0


if __name__ == "__main__":
    exit_code = main()
    raise SystemExit(exit_code)
