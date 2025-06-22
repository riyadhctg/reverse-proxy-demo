from starlette.requests import Request
from starlette.responses import Response, JSONResponse
from src.utils import get_forward_headers, HOP_HEADERS
import random
import asyncio
from src.config import SERVICE_REGISTRY


def health_check(request: Request) -> JSONResponse:
    return JSONResponse({"status": "ok"})


async def proxy(request: Request) -> Response:
    # item_type maps to service names in SERVICE_REGISTRY
    service_name: str = request.path_params.get("item_type")

    if not service_name or service_name not in SERVICE_REGISTRY:
        return JSONResponse(
            {"detail": f"Service '{service_name}' not found"}, status_code=404
        )

    remaining_path: str = request.path_params.get("path", "")
    if remaining_path:
        remaining_path = "/" + remaining_path

    # simple load balancing by randomly selecting a dummy server url
    server_url: str = random.choice(SERVICE_REGISTRY[service_name])
    upstream_url: str = f"{server_url}/{service_name}{remaining_path}"

    headers = get_forward_headers(request)

    try:
        resp = await request.app.state.client.request(
            method=request.method,
            url=upstream_url,
            headers=headers,
            content=await request.body(),
            timeout=5.0,
        )
    except asyncio.TimeoutError:
        return JSONResponse({"message": "Gateway timeout"}, status_code=504)
    except Exception:
        return JSONResponse({"message": "Bad gateway"}, status_code=502)

    response_headers = {
        k: v for k, v in resp.headers.items() if k.lower() not in HOP_HEADERS
    }

    return Response(
        content=resp.content,
        status_code=resp.status_code,
        headers=response_headers,
        media_type=resp.headers.get("content-type"),
    )
