from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import io
import json
from app.core.processor import process_deals

router = APIRouter()

@router.get("/")
async def get_root():
    """Return a simple message."""
    return {"message": "Welcome to the Mini Nudge Agent API!"}

@router.get("/nudges")
async def get_nudges():
    """Stream nudge results as JSON."""
    nudges = process_deals()
    output = io.StringIO()
    json.dump([nudge.dict() for nudge in nudges], output, indent=2)
    output.seek(0)
    return StreamingResponse(output, media_type="application/json")