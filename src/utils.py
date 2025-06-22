from starlette.requests import Request
import uuid

from src.config import (
    HEADER_AUTHORIZATION,
    HEADER_X_REQUEST_ID,
    HEADER_X_FORWARDED_FOR,
    HEADER_CONTENT_TYPE,
    DEFAULT_CONTENT_TYPE,
)

# hop-by-hop headers to exclude
# https://developer.mozilla.org/en-US/docs/Web/HTTP/Reference/Headers/Connection
HOP_HEADERS = {
    "connection",
    "keep-alive",
    "proxy-authenticate",
    "proxy-authorization",
    "te",
    "trailer",
    "transfer-encoding",
    "upgrade",
}


def get_forward_headers(request: Request) -> dict:
    headers_to_forward = {}

    auth_header = request.headers.get(HEADER_AUTHORIZATION)
    if auth_header:
        headers_to_forward[HEADER_AUTHORIZATION] = auth_header

    # setting request id for tracing
    request_id = request.headers.get(HEADER_X_REQUEST_ID, str(uuid.uuid4()))
    headers_to_forward[HEADER_X_REQUEST_ID] = request_id

    # setting original client ip in the X-Forwarded-For header for backend service's use
    x_forwarded_for = request.headers.get(HEADER_X_FORWARDED_FOR, request.client.host)
    headers_to_forward[HEADER_X_FORWARDED_FOR] = x_forwarded_for

    headers_to_forward[HEADER_CONTENT_TYPE] = request.headers.get(
        HEADER_CONTENT_TYPE, DEFAULT_CONTENT_TYPE
    )

    # add all other headers except hop-by-hop and already included ones
    for key, value in request.headers.items():
        key_lower = key.lower()
        if (
            key_lower not in HOP_HEADERS
            and key not in headers_to_forward
            and key_lower not in {h.lower() for h in headers_to_forward}
        ):
            headers_to_forward[key] = value

    return headers_to_forward
