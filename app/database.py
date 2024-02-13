import aiosqlite
from fastapi import Depends
from loguru import logger
from app.config import DATABASE_URL

async def get_db():
    async with aiosqlite.connect(DATABASE_URL) as db:
        yield db

async def fetch_supported_languages(database=DATABASE_URL) -> list:
    async with aiosqlite.connect(database) as db:
        query = "SELECT DISTINCT language FROM translations"
        async with db.execute(query) as cursor:
            rows = await cursor.fetchall()
            return [language[0] for language in rows]

async def fetch_ipa_translation(language: str, word: str, db=Depends(get_db)) -> str | None:
    query = "SELECT ipa_translation FROM translations WHERE word = ? AND language = ?"
    async with db.execute(query, (word, language)) as cursor:
        translation = await cursor.fetchone()
    if translation:
        return translation[0]
    logger.warning(f"No translation found for {language}/{word}")
    return None
