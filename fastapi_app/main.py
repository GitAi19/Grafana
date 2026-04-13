import time
import asyncio
import logging
import prometheus_client
from prometheus_client import Counter, Histogram
from fastapi import FastAPI, Request, Response
from opentelemetry import trace
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from opentelemetry.instrumentation.logging import LoggingInstrumentor
from opentelemetry.sdk.resources import Resource, SERVICE_NAME
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.otlp.proto.grpc.trace_exporter import OTLPSpanExporter

# ---------- Logging ----------
LoggingInstrumentor().instrument(set_logging_format=True)
logger = logging.getLogger("fastapi_app")
logger.setLevel(logging.INFO)



# ---------- Tracing (Tempo via OTLP gRPC) ----------
resource = Resource.create({SERVICE_NAME: "fastapi-service"})
provider = TracerProvider(resource=resource)
provider.add_span_processor(
    BatchSpanProcessor(OTLPSpanExporter(endpoint="http://tempo:4317"))
)
trace.set_tracer_provider(provider)



# ---------- Prometheus custom metrics ----------
REQUEST_COUNT = Counter(
    "fastapi_requests_total",
    "Total number of requests",
    ["method", "path", "status"],
)

REQUEST_LATENCY = Histogram(
    "request_duration_seconds",
    "Request duration histogram in seconds",
    ["method", "path"],
)

# ---------- App ----------
app = FastAPI()
FastAPIInstrumentor.instrument_app(app, tracer_provider=trace.get_tracer_provider())

# Metrics middleware
@app.middleware("http")
async def metrics_middleware(request: Request, call_next):
    start = time.time()
    response = await call_next(request)
    duration = time.time() - start

    path = request.url.path
    method = request.method
    status = str(response.status_code)

    REQUEST_COUNT.labels(method, path, status).inc()
    REQUEST_LATENCY.labels(method, path).observe(duration)
    return response

@app.get("/items/{item_id}")
async def read_item(item_id: int, request: Request):
    tracer = trace.get_tracer(__name__)
    with tracer.start_as_current_span("read_item") as span:
        logger.info("Received request for item_id: %s", item_id)
        span.set_attribute("http.route", "/items/{item_id}")
        span.set_attribute("item.id", item_id)

        # a fake DB call
        with tracer.start_as_current_span("simulated_db_call"):
            await asyncio.sleep(0.1)

        # some extra work
        with tracer.start_as_current_span("additional_work") as s:
            await asyncio.sleep(0.05)
            s.set_attribute("work.status", "completed")

        logger.info("Successfully processed request for item_id: %s", item_id)

    return {"item_id": item_id, "message": "Item processed successfully"}

@app.get("/health")
def health():
    return {"status": "ok"}

# Expose Prometheus metrics on /metrics
@app.get("/metrics")
def metrics():
    return Response(
        content=prometheus_client.generate_latest(),
        media_type="text/plain",
    )
