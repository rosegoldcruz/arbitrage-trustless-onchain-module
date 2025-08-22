from fastapi import FastAPI
from api.metrics import router as metrics
app = FastAPI()
app.include_router(metrics)
