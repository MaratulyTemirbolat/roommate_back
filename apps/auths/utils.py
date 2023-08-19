# Python
from typing import (
    Dict,
    Any,
    Tuple,
)


def get_valid_request_data(
    request_data: Dict[str, Any],
    single_keys: Tuple[str],
) -> Dict[str, Any]:
    """Get valid request data."""
    resulted_data: Dict[str, Any] = {}
    key: str
    for key in request_data:
        if key in single_keys:
            resulted_data.setdefault(
                key,
                request_data[key]
            )
    return resulted_data
