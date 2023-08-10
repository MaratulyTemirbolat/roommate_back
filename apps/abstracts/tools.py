from typing import (
    Optional,
    Tuple,
    Dict,
    Any,
)


def conver_to_int_or_none(number: str = "") -> Optional[int]:
    """Get converted string to number. If problem then None."""
    try:
        return int(number)
    except ValueError:
        return None


def get_filled_params_dict(
    req_params: Tuple[str],
    **query_params: Dict[str, Any]
) -> Dict[str, Any]:
    """Get filled dictioanary with the provided params."""
    res_dict: Dict[str, Any] = {}

    key: str
    for key in query_params:
        if key in req_params:
            res_dict.setdefault(key, query_params[key][0])
    return res_dict
