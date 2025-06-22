# Simple Reverse Proxy

## How it works
A simple reverse proxy server connects to a dummy backend service that mimics multiple servers using different endpoints. When a user invokes the proxy server, it will do some minimal work such as dummy auth checks, header management (e.g., addition of request-id, x-forwarded-for), and then it will forward the request to the destination server based on the request path and send the response back to the user upon receipt.

## How to Use

This project uses **Python >= 3.10** along with the **[uv](https://docs.astral.sh/uv/)** package manager.

### Steps to Run the Server

1. Install `uv` by following this guide: https://docs.astral.sh/uv/getting-started/installation/
2. In the root of the repo, run:  
```bash
uv sync
```

This will create a virtual environment .venv and install all dependencies.
3. Start the proxy server:
```bash
uv run uvicorn src.main:app --reload --host 0.0.0.0 --port 8080
```
The server will be available at http://localhost:8080
4. In another terminal, run the following inline Python script (GPT generated) to start a mock backend server. This simulates multiple servers via endpoint suffixes and runs on http://localhost:8000:

```bash
python -c "exec(\"\"\"from http.server import BaseHTTPRequestHandler, HTTPServer
import json,re

D = {}
class H(BaseHTTPRequestHandler):
    def do_GET(self):
        m = re.match(r'^/(server[A-Z])/(books|health)$', self.path)
        if not m:
            self.send_error(404)
            return
        srv, ep = m.groups()
        self.send_response(200)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'status': 'ok'} if ep == 'health' else D.get(srv, [])).encode())

    def do_POST(self):
        m = re.match(r'^/(server[A-Z])/books$', self.path)
        if not m:
            self.send_error(404)
            return
        srv = m.group(1)
        d = json.loads(self.rfile.read(int(self.headers['Content-Length'])))
        if 'name' in d and 'author' in d:
            D.setdefault(srv, []).append(d)
            self.send_response(201)
        else:
            self.send_response(400)
        self.send_header('Content-Type', 'application/json')
        self.end_headers()
        self.wfile.write(json.dumps({'book': d} if 'name' in d and 'author' in d else {'error': 'bad request'}).encode())

print('Server running on http://localhost:8000')
HTTPServer(('', 8000), H).serve_forever()
\"\"\")"

```


### Test the Server

✅ 1. Health Check
```bash
curl http://localhost:8080/health
```
```
{"status": "ok"}
```

🚫 2. Missing Auth Header
```bash
curl http://localhost:8080/items/books
```
```
{"message": "Not authenticated"}
```

📚 3. Get Books (with auth)
```bash
curl http://localhost:8080/items/books \
  -H "Authorization: Bearer secret-token"
```
```
[{"name": "The Hobbit", "author": "J.R.R. Tolkien"}]
```

➕ 4. Add Book (with auth)
```bash
curl -X POST http://localhost:8080/items/books \
  -H "Authorization: Bearer secret-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "The Hobbit", "author": "J.R.R. Tolkien"}'
```
```
{"book": {"name": "The Hobbit", "author": "J.R.R. Tolkien"}}
```


❌ 5. Add Invalid Book (missing author)
```bash
curl -X POST http://localhost:8080/items/books \
  -H "Authorization: Bearer secret-token" \
  -H "Content-Type: application/json" \
  -d '{"name": "Missing Author"}'
```
```
{"error": "bad request"}
```

❓ 6. Unknown Service
```bash
curl http://localhost:8080/items/unknown \
  -H "Authorization: Bearer secret-token"
```
```
{"message": "Service 'unknown' not found"}

```


## Design Decisions
To demonstrate a basic HTTP reverse proxy server, a load balancer use case was chosen.

The scope was intentionally kept minimal to avoid over-engineering for a take-home assessment. For example:
* Load balancing uses simple random selection of servers.
* Target servers are simulated via one server using multiple endpoints (serverA, serverB, serverC), generated using GPT in inline python -c format for reviewer convenience.
* Logging and tracing are excluded to maintain simplicity.
* Only a minimal, functional reverse proxy is demonstrated—without additional features like rate limiting or retries.

There are three main external dependencies:
* starlette: popular and minimal ASGI toolkit to build async services
* httpx: popular http client with async support
* uvicorn: popular ASGI server


## How Would You Scale This?
* Horizontal Scaling: Run multiple instances behind a production-grade load balancer (e.g., AWS ELB).
* Concurrency: Use multiple Uvicorn workers for better concurrency e.g., ```uvicorn --workers 4 ...```
* Deployment: Package as a container image and deploy via cloud platforms like AWS ECS or EKS.
•* Load Balancing: Replace random selection with a more robust strategy like round-robin.
* Health Checks: Incorporate health/unhealth checks of target servers.
* Service Discovery: Replace hardcoded SERVICE_REGISTRY with dynamic service discovery (e.g., Consul).
* Observability: Integrate logging and monitoring (Grafana, OpenTelemetry, ELK).
* Production Readiness: Add features like retries, rate limiting, and circuit breakers.


## How Would You Make It More Secure?
* Implement proper token-based authentication (e.g., JWT, OAuth).
* Enforce HTTPS.
* Validate headers appropriately.
* Use rate limiting to prevent DDoS or abuse.


## Resources Used
* Articles for high level refresher, including: https://www.cloudflare.com/learning/cdn/glossary/reverse-proxy/
* GitHub Copilot for code completion.
* ChatGPT and Claude for some code snippets, test-cases generation, debugging help, and suggestions (e.g., handling hop-by-hop headers).
* GPT was also used to generate parts of this README (e.g., curl command sections).
