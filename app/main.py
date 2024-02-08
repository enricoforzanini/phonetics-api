from contextlib import asynccontextmanager
import sys
import aiosqlite
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import List, Optional
from pydantic import BaseModel
from app import data_loader

DATABASE = 'data.db'

allowed_origins = [
    "http://localhost:3000",
    "https://enricoforzanini.github.io/",
]

class TranslateRequest(BaseModel):
    language: str
    words: List[str]

class TranslationItem(BaseModel):
    word: str
    ipa_translation: Optional[str] = None
    error: Optional[str] = None

class TranslateResponse(BaseModel):
    translations: List[TranslationItem]

logger.remove()
logger.level("INFO")
logger.add(sys.stdout, format="{time} {level} {message}")

data_loader.download_data()

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Phonetics API",
    summary="Phonetics API to get the IPA translation of words in different languages.",
)
app.state.limiter = limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

main_app_lifespan = app.router.lifespan_context # from https://stackoverflow.com/a/77364729

@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info("Application startup")
    async with main_app_lifespan(app) as state:
        yield state
    logger.info("Application shutdown")

app.router.lifespan_context = lifespan

@app.middleware("http")
async def log_requests(request: Request, call_next):
    response = await call_next(request)
    logger.info(f"Request: {request.method} {request.url} {response.status_code}")
    return response

@app.exception_handler(HTTPException)
async def log_http_exceptions(request: Request, exception: HTTPException):
    logger.error(f"HTTP error: {exception.detail}")
    return JSONResponse(status_code=exception.status_code, content={"detail": exception.detail})

async def convert_to_ipa(language, word):
    async with aiosqlite.connect(DATABASE) as db:
        c = await db.execute("SELECT ipa_translation FROM translations WHERE word = ? AND language = ?", (word, language))
        translation = await c.fetchone()
        await c.close()
    if translation:
        return translation[0]
    else:
        logger.warning(f"No translation found for {language}/{word}")
        return None

@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    return {
        "message": "Welcome to the Phonetics API",
        "endpoints": {
            "translate": {
                "method": "POST",
                "description": "Translates words to IPA. Accepts JSON with language and a list of words.",
                "example_request": {
                    "language": "fr",
                    "words": ["salut", "monde"]
                }
            },
        
            "supported_languages": {
                    "method": "GET",
                    "path": "/languages",
                    "description": "Lists all supported languages for translation."
                }
            },
            "documentation": {
                "Swagger UI": "/docs",
                "ReDoc": "/redoc"
            },
            "contact": "For more information, visit the [GitHub Repo](https://github.com/enricoforzanini/phonetics-api)"
    }

@app.post("/translate", response_model=TranslateResponse)
async def translate_text(request: Request, translate_request: TranslateRequest):
    max_words = 200
    if len(translate_request.words) > max_words:
        raise HTTPException(status_code=400, detail=f"Request exceeds maximum allowed number of words ({max_words}).")

    result = await get_supported_languages(request)
    available_languages = result['languages']
    if translate_request.language not in available_languages:
        raise HTTPException(status_code=404, detail="Language not available")
    
    translations = []
    for word in translate_request.words:
        translation = await convert_to_ipa(translate_request.language, word.lower())
        if translation:
            translations.append(TranslationItem(word=word, ipa_translation=translation))
        else:
            translations.append(TranslationItem(word=word, ipa_translation=None, error="Translation not found"))
    
    return TranslateResponse(translations=translations)

@app.get("/languages")
@limiter.limit("5/minute")
async def get_supported_languages(request: Request):
    async with aiosqlite.connect(DATABASE) as db:
        c = await db.execute("SELECT DISTINCT language FROM translations")
        rows = await c.fetchall()
        languages = [language[0] for language in rows]
        await c.close()
    return {"languages": languages}

@app.get("/{path:path}")
@limiter.limit("10/minute")
def catch_all(path: str, request: Request):
    raise HTTPException(status_code=404, detail="Endpoint not found. Please check the URL.")
