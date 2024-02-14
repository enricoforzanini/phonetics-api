from fastapi import APIRouter, Request
from ..models import SupportedLanguagesResponse
from ..config import limiter

router = APIRouter()

@router.get("/languages", response_model=SupportedLanguagesResponse)
@limiter.limit("5/minute")
async def get_supported_languages(request: Request):
    return SupportedLanguagesResponse(languages=request.app.state.supported_languages)
