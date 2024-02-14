from fastapi import APIRouter, Depends, HTTPException, Request
from ..models import TranslateRequest, TranslationItem, TranslateResponse
from ..database import get_db, fetch_ipa_translation
from ..config import limiter

router = APIRouter()

@router.post("/translate", response_model=TranslateResponse)
@limiter.limit("5/minute")
async def translate_text(request: Request, translate_request: TranslateRequest, db=Depends(get_db)):
    max_words = 200
    if len(translate_request.words) > max_words:
        raise HTTPException(status_code=400, detail=f"Request exceeds maximum allowed number of words ({max_words}).")
    if translate_request.language not in request.app.state.supported_languages:
        raise HTTPException(status_code=404, detail="Language not available")

    translations = []
    for word in translate_request.words:
        translation = await fetch_ipa_translation(translate_request.language, word.lower(), db)
        if translation:
            translations.append(TranslationItem(word=word, ipa_translation=translation))
        else:
            translations.append(TranslationItem(word=word, ipa_translation=None, error="Translation not found"))

    return TranslateResponse(translations=translations)

@router.get("/translate/{language}/{word}", response_model=TranslationItem)
@limiter.limit("15/minute")
async def translate_word(request: Request, language: str, word: str, db=Depends(get_db)):
    if language not in request.app.state.supported_languages:
        raise HTTPException(status_code=404, detail="Language not available")
    translation = await fetch_ipa_translation(language, word.lower(), db)
    if translation:
        return TranslationItem(word=word, ipa_translation=translation)
    return TranslationItem(word=word, ipa_translation=None, error="Translation not found")
