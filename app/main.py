from fastapi import FastAPI, HTTPException
from app import data_loader

translations = data_loader.load_translations()

app = FastAPI()

def convert_to_ipa(language, word):
    return translations[language].get(word)

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