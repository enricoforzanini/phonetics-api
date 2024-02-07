from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)

def test_catch_all():
    response = client.get("/test/random/path")
    assert response.status_code == 404
    assert response.json() == {"detail": "Endpoint not found. Please check the URL."}

def test_translate_language_not_found():
    response = client.get("/translate/fakelanguage/hello")
    assert response.status_code == 404
    assert response.json() == {"detail": "Language not available"}

def test_translate_word_not_found():
    response = client.get("/translate/fr/nonexistentword123")
    assert response.status_code == 404
    assert response.json() == {"detail": "Translation not found"}

def test_valid_translation():
    response = client.get("/translate/fr/abdominales")
    assert response.status_code == 200
    assert response.json() == {"language": "fr", "word": "abdominales", "ipa_translation": "ab.dɔ.mi.nal"}


    