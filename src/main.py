import asyncio

from fastapi import FastAPI
from prometheus_fastapi_instrumentator import Instrumentator
import random

app = FastAPI()


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

@app.get("/")
async def root():
    await asyncio.sleep(random.uniform(0.1, 0.5))
    return {"message": "Hello World"}

@app.get("/slow")
async def slow_endpoint():
    await asyncio.sleep(random.uniform(1.0, 3.0))
    return {"message": "Slow response"}