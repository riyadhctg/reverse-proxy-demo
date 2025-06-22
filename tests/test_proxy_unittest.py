import unittest
from unittest.mock import MagicMock
from starlette.requests import Request
from starlette.responses import JSONResponse
from src.proxy import health_check, proxy, get_forward_headers


class ProxyTests(unittest.TestCase):
    def test_health_check(self):
        mock_request = MagicMock()
        response = health_check(mock_request)
        self.assertIsInstance(response, JSONResponse)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.body, b'{"status":"ok"}')

    def test_get_forward_headers_minimal(self):
        mock_request = MagicMock()
        mock_request.headers = {
            "Content-Type": "application/json",
            "custom-header": "hello",
        }
        mock_request.client = MagicMock()
        mock_request.client.host = "1.1.1.1"

        result = get_forward_headers(mock_request)

        self.assertIn("X-Request-ID", result)
        self.assertIn("X-Forwarded-For", result)
        self.assertIn("Content-Type", result)
        self.assertIn("custom-header", result)

    def test_get_forward_headers_defaults(self):
        mock_request = MagicMock()
        mock_request.headers = {}
        mock_request.client = MagicMock()
        mock_request.client.host = "2.2.2.2"

        result = get_forward_headers(mock_request)

        self.assertIn("X-Request-ID", result)
        self.assertEqual(result["X-Forwarded-For"], "2.2.2.2")
        self.assertEqual(result["Content-Type"], "application/json")


class ProxyAsyncTests(unittest.IsolatedAsyncioTestCase):
    async def test_proxy_invalid_service(self):
        scope = {
            "type": "http",
            "method": "GET",
            "path": "/items/invalid/path",
            "headers": [],
            "query_string": b"",
            "client": ("127.0.0.1", 12345),
            "path_params": {"item_type": "invalid", "path": "path"},
        }

        mock_request = Request(scope)
        response = await proxy(mock_request)

        self.assertEqual(response.status_code, 404)
        self.assertEqual(response.body, b'{"detail":"Service \'invalid\' not found"}')
