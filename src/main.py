import asyncio
import logging

from fastapi import FastAPI, HTTPException
from prometheus_fastapi_instrumentator import Instrumentator
import random

from src.logging_config import configure_logging
from pydantic import BaseModel
app = FastAPI()


instrumentator = Instrumentator()
instrumentator.instrument(app).expose(app, endpoint="/metrics")

configure_logging()

logger = logging.getLogger()

class OrderRequest(BaseModel):
    payment_method: str
    amount: float
@app.post("/")
async def root(order: OrderRequest):
    logger.info(f"Order received: amount={order.amount}, method={order.payment_method}")
    if random.random() < 0.3:
        logger.error("Payment gateway error", extra={"order_amount": order.amount})
        raise HTTPException(status_code=500, detail="Payment gateway error")
    await asyncio.sleep(random.uniform(0.1, 0.5))
    logger.info(f"Order processed successfully", extra={"order_amount": order.amount})
    return OrderRequest.model_dump(order)


@app.get("/slow")
async def slow_endpoint():
    await asyncio.sleep(random.uniform(1.0, 3.0))
    return {"message": "Slow response"}
