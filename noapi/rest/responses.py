from collections.abc import Iterable
from collections.abc import Mapping
from typing import Any
from typing import Generic
from typing import Literal
from typing import TypedDict
from typing import TypeVar

from pydantic.generics import GenericModel

import noapi.json
from noapi.errors import ServiceError

T = TypeVar("T")


class Cookie(TypedDict, total=False):
    key: str
    value: str
    max_age: int | None
    expires: int | None
    path: str
    domain: str | None
    secure: bool
    httponly: bool
    samesite: Literal["lax", "strict", "none"]


def create_response(
    content: Mapping[str, Any],
    status_code: int,
    headers: dict[str, str] | None,
    cookies: Iterable[Cookie] | None = None,
) -> noapi.json.ORJSONResponse:
    response = noapi.json.ORJSONResponse(content, status_code, headers)

    if cookies is None:
        cookies = []

    for cookie in cookies:
        response.set_cookie(**cookie)

    return response


class Success(GenericModel, Generic[T]):
    status: Literal["success"]
    data: T


def format_success(data: Any) -> dict[str, Any]:
    return {"status": "success", "data": data}


def success(
    data: Any,
    status_code: int = 200,
    headers: dict | None = None,
    cookies: Iterable[Cookie] | None = None,
) -> noapi.json.ORJSONResponse:
    content = format_success(data)
    return create_response(content, status_code, headers, cookies)


class Error(GenericModel, Generic[T]):
    status: Literal["error"]
    error: T
    message: str


def format_failure(error: ServiceError, message: str) -> dict[str, Any]:
    return {"status": "error", "error": error, "message": message}


def failure(
    error: ServiceError,
    message: str,
    status_code: int = 400,
    headers: dict | None = None,
    cookies: Iterable[Cookie] | None = None,
) -> noapi.json.ORJSONResponse:
    content = format_failure(error, message)
    return create_response(content, status_code, headers, cookies)
