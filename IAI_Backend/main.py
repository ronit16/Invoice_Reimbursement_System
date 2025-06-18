from logger import logger
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1.endpoints import router as api_router

app = FastAPI()
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"],  
    allow_headers=["*"],  
)

logger.info("Starting FastAPI application...")

app.include_router(api_router, prefix="/api/v1")

logger.info("FastAPI application started successfully.")
