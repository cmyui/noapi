from collections.abc import Mapping
from typing import Any
from typing import TypeVar

import pydantic

T = TypeVar("T", bound=type["BaseModel"])


class BaseModel(pydantic.BaseModel):
    class Config:
        anystr_strip_whitespace = True

    @classmethod
    def from_mapping(cls: T, mapping: Mapping[str, Any]) -> T:
        return cls(**{k: mapping[k] for k in cls.__fields__})
