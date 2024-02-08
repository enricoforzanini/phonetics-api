from contextlib import asynccontextmanager
import sys
import aiosqlite
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from typing import List
from pydantic import BaseModel
from app import data_loader

DATABASE = 'data.db'

class TranslateRequest(BaseModel):
    language: str
    words: List[str]

class TranslationItem(BaseModel):
    word: str
    ipa_translation: str
    error: str = None

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

app = FastAPI()

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
            "translate_word": "/translate/{language}/{word}",
            "supported_languages": "/languages",
            "documentation": {
                "Swagger UI": "/docs",
                "ReDoc": "/redoc"
            }
        },
        "example_usage": {
            "translate_word": "/translate/fr/famille",
            "supported_languages": "/languages"
        },
        "contact": "For more information, visit the [GitHub Repo](https://github.com/enricoforzanini/phonetics-api)"
    }

@app.get("/translate/{language}/{word}")
@limiter.limit("5/minute")
async def translate_text(language: str, word: str, request: Request):
    result = await get_supported_languages(request)
    available_languages = result['languages']
    if language not in available_languages:
        raise HTTPException(status_code=404, detail="Language not available")

    ipa_translation = await convert_to_ipa(language, word)
    if ipa_translation is None:
        raise HTTPException(status_code=404, detail="Translation not found")

    return {"language": language, "word": word, "ipa_translation": ipa_translation}

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
