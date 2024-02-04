from fastapi import FastAPI, HTTPException
from app import data_loader

translations = data_loader.load_translations()

app = FastAPI(
    title="Phonetics API",
    summary="Phonetics API to get the IPA translation of words in different languages.",
)

app = FastAPI()

def convert_to_ipa(language, word):
    return translations[language].get(word)

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
        "contact": "For more information, visit the [GitHub Repo](https://github.com/EnricoFo/phonetics-api)"
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
    return {"detail": "Endpoint not found. Please check the URL."}