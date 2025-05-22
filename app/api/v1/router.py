from fastapi import APIRouter

# Import individual routers for different functionalities
# For now, these can be placeholders or commented out if not yet implemented
# from .endpoints import sentiment, health, auth, history # Example imports

api_router = APIRouter()

# Include individual routers into the main v1 router
# api_router.include_router(health.router, prefix="/health", tags=["Health"])
# api_router.include_router(sentiment.router, prefix="/sentiment", tags=["Sentiment Analysis"])
# api_router.include_router(auth.router, prefix="/auth", tags=["Authentication"]) # To be implemented later
# api_router.include_router(history.router, prefix="/history", tags=["Analysis History"]) # To be implemented later

# A simple root endpoint for the v1 router for initial testing
@api_router.get("/", tags=["V1 Root"])
async def read_v1_root():
    return {"message": "Welcome to SentimentFlow API v1"}

