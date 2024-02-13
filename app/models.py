from typing import List, Optional
from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    language: str = Field(
        ...,
        description='Two-letter ISO 639-1 language code',
        min_length=2,
        max_length=2,
        examples=['fr', 'en']
        )
    words: List[str] = Field(
        ...,
        description='List of words to be translated',
        examples=['hello', 'world']
        )

class TranslationItem(BaseModel):
    word: str = Field(..., description='Word to be translated')
    ipa_translation: Optional[str] = Field(None, description='IPA translation if available')
    error: Optional[str] = Field(None, description='Error message if translation failed')

class TranslateResponse(BaseModel):
    translations: List[TranslationItem] = Field(
        ...,
        description='List of translation items'
    )

class SupportedLanguagesResponse(BaseModel):
    languages: List[str] = Field(
        ...,
        description='List of supported ISO 639-1 language codes'
    )