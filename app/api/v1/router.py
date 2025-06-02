from fastapi import APIRouter

# Import individual routers for different functionalities
from .sentiment import router as sentiment_router
from .history import router as history_router

api_router = APIRouter()

# Include individual routers into the main v1 router
# Note: sentiment and history routers already have their own prefixes defined
api_router.include_router(sentiment_router)
api_router.include_router(history_router)

# A simple root endpoint for the v1 router for initial testing
@api_router.get("/", tags=["V1 Root"])
async def read_v1_root():
    return {"message": "Welcome to SentimentFlow API v1"}

