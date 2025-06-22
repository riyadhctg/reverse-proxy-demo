from starlette.applications import Starlette
from starlette.routing import Route
from starlette.middleware import Middleware
from src.proxy import proxy, health_check
from src.middlewares.auth import AuthMiddleware
import httpx

routes = [
    Route(
        "/items/{item_type}", proxy, methods=["GET", "POST", "PUT", "DELETE", "PATCH"]
    ),
    Route("/health", health_check, methods=["GET"]),
]

middleware = [Middleware(AuthMiddleware)]


async def startup() -> None:
    app.state.client = httpx.AsyncClient(limits=httpx.Limits(max_connections=100))


async def shutdown() -> None:
    await app.state.client.aclose()


app = Starlette(
    routes=routes, middleware=middleware, on_startup=[startup], on_shutdown=[shutdown]
)
