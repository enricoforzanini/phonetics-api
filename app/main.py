from contextlib import asynccontextmanager
import sys
from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from loguru import logger
from slowapi.errors import RateLimitExceeded
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from app.database import fetch_supported_languages
from app import data_loader
from app.routers import translation, languages

allowed_origins = [
    "http://localhost:3000",
    "http://localhost:8080",
    "http://localhost"
]

logger.remove()
logger.level("INFO")
logger.add(sys.stdout, format="{time} {level} {message}")

limiter = Limiter(key_func=get_remote_address)
app = FastAPI(
    title="Phonetics API",
    summary="Phonetics API to get the IPA translation of words in different languages.",
)
app.include_router(translation.router)
app.include_router(languages.router)
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
    data_loader.download_data()
    logger.info("Data Downloaded")
    app.state.supported_languages = await fetch_supported_languages()
    logger.info("Available languages")
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

@app.get("/")
@limiter.limit("10/minute")
def read_root(request: Request):
    base_url = str(request.base_url)[:-1]
    return JSONResponse(content = {
        "message": "Welcome to the Phonetics API",
        "endpoints": [
            {
                "name": "Translate multiple words",
                "path": f"{base_url}/translate",
                "method": "POST",
                "description": "Translates words to IPA. Accepts JSON with language and a list of words.",
                "example_request": {
                    "language": "fr",
                    "words": ["salut", "monde"]
                }
            },
            {
                "name": "Translate a single word",
                "path": base_url + "/translate/{language}/{word}",
                "method": "GET",
                "description": "Translates a single word IPA. Requires language and word as path parameters."
            },
            {
                "name": "Supported Languages",
                "path": f"{base_url}/languages",
                "method": "GET",
                "description": "Lists all supported languages for translation."
            }
        ],
        "documentation": [
            {
                "name": "Swagger UI",
                "url": f"{base_url}/docs"
            },
            {
                "name": "ReDoc",
                "url": f"{base_url}/redoc"
            }
        ],
        "contact": {
            "message": "For more information, visit the GitHub Repo",
            "url": "https://github.com/enricoforzanini/phonetics-api"
        }
    })

@app.get("/{path:path}")
@limiter.limit("10/minute")
def catch_all(path: str, request: Request):
    raise HTTPException(status_code=404, detail="Endpoint not found. Please check the URL.")
