SUPPORTED_ITEM_TYPES = {"books", "movies"}

HEADER_AUTHORIZATION = "Authorization"
HEADER_X_REQUEST_ID = "X-Request-ID"
HEADER_X_FORWARDED_FOR = "X-Forwarded-For"
HEADER_CONTENT_TYPE = "Content-Type"
DEFAULT_CONTENT_TYPE = "application/json"

# service registry mapping item types to service URLs
# several urls to mimic many instances of the same service to demonstrate load balancing
SERVICE_REGISTRY = {
    "books": [
        "http://localhost:8000/serverA",
        "http://localhost:8000/serverB",
        "http://localhost:8000/serverC",
    ],
    # movies point to unimplemented service. This is just only for placeholder purposes
    "movies": [
        "http://localhost:8001/serverA",
        "http://localhost:8001/serverB",
        "http://localhost:8001/serverC",
    ],
}
