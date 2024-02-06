from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from loguru import logger
from app import data_loader
import sys

logger.remove()
logger.level("INFO")
logger.add(sys.stdout, format="{time} {level} {message}")

translations = data_loader.load_translations()

app = FastAPI(
    title="Phonetics API",
    summary="Phonetics API to get the IPA translation of words in different languages.",
)

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


def convert_to_ipa(language, word):
    translation = translations[language].get(word)
    if translation:
        logger.info(f"Translation found for {language}/{word}: {translation}")
    else:
        logger.warning(f"No translation found for {language}/{word}")
    return translation

@app.get("/")
def read_root():
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
def translate_text(language: str, word: str):

    if language not in translations.keys():
        raise HTTPException(status_code=404, detail="Language not available")

    ipa_translation = convert_to_ipa(language, word)
    if ipa_translation is None:
        raise HTTPException(status_code=404, detail="Translation not found")

    return {"language": language, "word": word, "ipa_translation": ipa_translation}

@app.get("/languages")
def get_supported_languages():
    return {"languages": list(translations.keys())}

@app.get("/{path:path}")
def catch_all(path: str):
    raise HTTPException(status_code=404, detail="Endpoint not found. Please check the URL.")
