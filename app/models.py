from typing import List, Optional
from pydantic import BaseModel, Field

class TranslateRequest(BaseModel):
    language: str = Field(
        ...,
        description='Two-letter ISO 639-1 language code',
        min_length=2,
        max_length=2
        )
    words: List[str] = Field(
        ...,
        description='List of words to be translated'
        )
    
    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "language": "fr",
                    "words": ["bonjour", "monde", "salut", "famille", "le", "les"]
                }
            ]
        }
    }

class TranslationItem(BaseModel):
    word: str = Field(..., description='Word to be translated')
    ipa_translation: Optional[str] = Field(None, description='IPA translation if available')
    error: Optional[str] = Field(None, description='Error message if translation failed')

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "word": "bonjour",
                    "ipa_translation": "bɔ̃.ʒuʁ",
                    "error": None
                }
            ]
        }
    }

class TranslateResponse(BaseModel):
    translations: List[TranslationItem] = Field(
        ...,
        description='List of translation items'
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "translations": [
                        {"word": "bonjour", "ipa_translation": "bɔ̃.ʒuʁ", "error": None},
                        {"word": "monde", "ipa_translation": "mɔ̃d", "error": None},
                        {"word": "salut", "ipa_translation": "sa.ly", "error": None},
                        {"word": "famille", "ipa_translation": "fa.mij", "error": None},
                        {"word": "le", "ipa_translation": "lə", "error": None},
                        {"word": "les", "ipa_translation": "le", "error": None}
                    ]
                }
            ]
        }
    }

class SupportedLanguagesResponse(BaseModel):
    languages: List[str] = Field(
        ...,
        description='List of supported ISO 639-1 language codes'
    )

    model_config = {
        "json_schema_extra": {
            "examples": [
                {
                    "languages": ["fr", "en"]
                }
            ]
        }
    }