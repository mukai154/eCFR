from fastapi import FastAPI  # type: ignore
from fastapi.middleware.cors import CORSMiddleware  # type: ignore
from typing import List  # Import List type for type hinting
from fastapi import Query  # type: ignore
import requests
import xml.etree.ElementTree as ET
from app.utils.logging_config import setup_logging
from app.api.ecfr_api.metrics import router as metrics_router

setup_logging()

app = FastAPI()

# Add CORS middleware to allow requests from any origin
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can replace "*" with specific origin like "http://localhost:5173" for security
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(metrics_router)

@app.get("/")
def root():
    return {"message": "ECFR backend is alive"}