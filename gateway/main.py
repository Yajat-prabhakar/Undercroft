"""
LLM Inference Gateway
Sits in front of a self-hosted Ollama instance. Handles auth, rate limiting,
request queueing (to protect constrained ARM hardware from overload), and
exposes metrics for Prometheus scraping.
"""
import os
import time
import asyncio
import logging
from contextlib import asynccontextmanager

import httpx
from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.security import APIKeyHeader
from prometheus_client import Counter, Histogram, Gauge, generate_latest, CONTENT_TYPE_LATEST
from starlette.responses import Response
from pydantic import BaseModel

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("gateway")

OLLAMA_URL = os.getenv("OLLAMA_URL", "http://localhost:11434")
API_KEY = os.getenv("GATEWAY_API_KEY", "changeme")  # override via Secret in prod
MAX_CONCURRENT_REQUESTS = int(os.getenv("MAX_CONCURRENT_REQUESTS", "2"))  # ARM box is small, protect it

# --- metrics ---
REQUEST_COUNT = Counter("gateway_requests_total", "Total requests", ["endpoint", "status"])
REQUEST_LATENCY = Histogram("gateway_request_latency_seconds", "Request latency", ["endpoint"])
QUEUE_DEPTH = Gauge("gateway_queue_depth", "Current number of queued/in-flight inference requests")

request_semaphore: asyncio.Semaphore = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    global request_semaphore
    request_semaphore = asyncio.Semaphore(MAX_CONCURRENT_REQUESTS)
    logger.info(f"Gateway starting, max concurrent inference requests={MAX_CONCURRENT_REQUESTS}")
    yield


app = FastAPI(title="LLM Inference Gateway", lifespan=lifespan)

api_key_header = APIKeyHeader(name="X-API-Key")


def verify_api_key(key: str = Depends(api_key_header)):
    if key != API_KEY:
        raise HTTPException(status_code=401, detail="Invalid API key")
    return key


class GenerateRequest(BaseModel):
    model: str = "llama3.2:1b"
    prompt: str
    stream: bool = False


@app.get("/health")
async def health():
    """Used by k8s liveness/readiness probes and the CD rollback check."""
    try:
        async with httpx.AsyncClient(timeout=3.0) as client:
            r = await client.get(f"{OLLAMA_URL}/api/tags")
            r.raise_for_status()
        return {"status": "ok", "ollama": "reachable"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Ollama unreachable: {e}")


@app.get("/metrics")
async def metrics():
    return Response(generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.post("/v1/generate")
async def generate(req: GenerateRequest, _: str = Depends(verify_api_key)):
    endpoint = "/v1/generate"
    start = time.time()
    QUEUE_DEPTH.inc()
    try:
        async with request_semaphore:  # backpressure: only N concurrent hits to Ollama
            async with httpx.AsyncClient(timeout=120.0) as client:
                r = await client.post(
                    f"{OLLAMA_URL}/api/generate",
                    json={"model": req.model, "prompt": req.prompt, "stream": False},
                )
                r.raise_for_status()
                data = r.json()
        REQUEST_COUNT.labels(endpoint=endpoint, status="200").inc()
        return {"response": data.get("response", ""), "model": req.model}
    except httpx.HTTPStatusError as e:
        REQUEST_COUNT.labels(endpoint=endpoint, status=str(e.response.status_code)).inc()
        raise HTTPException(status_code=502, detail=f"Ollama error: {e}")
    except Exception as e:
        REQUEST_COUNT.labels(endpoint=endpoint, status="500").inc()
        raise HTTPException(status_code=500, detail=str(e))
    finally:
        QUEUE_DEPTH.dec()
        REQUEST_LATENCY.labels(endpoint=endpoint).observe(time.time() - start)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    response = await call_next(request)
    return response
