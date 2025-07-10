from fastapi import FastAPI
from app.api.routes import router
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(title="Mini-Nudge Agent")

# Include API routes
app.include_router(router)