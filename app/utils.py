from typing import Any, Callable, Optional
from uuid import UUID

from orjson import OPT_NON_STR_KEYS, dumps as orjson_dumps, loads as orjson_loads


def _default(value: Any) -> Any:
    if isinstance(value, UUID):
        return str(value)
    raise TypeError(f"Can't dump {value}")


def json_loads(value: Any) -> Any:
    return orjson_loads(value)


def json_dumps(
    value: Any, decode: bool = True, default: Optional[Callable[..., Any]] = None
) -> Any:
    if default is None:
        default = _default
    if not decode:
        return orjson_dumps(value, default=default, option=OPT_NON_STR_KEYS)
    return orjson_dumps(value, default=default, option=OPT_NON_STR_KEYS).decode()
