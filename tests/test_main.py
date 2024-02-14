from fastapi.testclient import TestClient
import pytest
from app import main

@pytest.fixture
def client():
    with TestClient(main.app) as c:
        yield c

def test_catch_all(client):
    response = client.get("/test/random/path")
    assert response.status_code == 404
    assert response.json() == {"detail": "Endpoint not found. Please check the URL."}

def test_translate_language_not_found(client):
    data = {
        "language": "zz",
        "words": ["hello"]
    }
    response = client.post("/translate", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Language not available"}

def test_valid_translation_one_word(client):
    data = {
        "language": "fr",
        "words": ["abdominales"]
    }
    response = client.post("/translate", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "translations": [
            {"word": "abdominales", "ipa_translation": "ab.dɔ.mi.nal", "error": None}
        ]
    }

def test_valid_translation_two_words(client):
    data = {
        "language": "fr",
        "words": ["abdominales", "musculaires"]
    }
    response = client.post("/translate", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "translations": [
            {"word": "abdominales", "ipa_translation": "ab.dɔ.mi.nal", "error": None},
            {"word": "musculaires", "ipa_translation": "mys.ky.lɛʁ", "error": None}
        ]
    }

def test_translation_one_error(client):
    data = {
        "language": "fr",
        "words": ["abdominales", "nonexistentword"]
    }
    response = client.post("/translate", json=data)
    assert response.status_code == 200
    assert response.json() == {
        "translations": [
            {"word": "abdominales", "ipa_translation": "ab.dɔ.mi.nal", "error": None},
            {"word": "nonexistentword", "ipa_translation": None, "error": "Translation not found"}
        ]
    }

def test_get_translate_language_not_found(client):
    response = client.get("/translate/zz/hello")
    assert response.status_code == 404
    assert response.json() == {"detail": "Language not available"}

def test_get_translate_word_not_found(client):
    response = client.get("/translate/fr/nonexistentword123")
    assert response.status_code == 200
    assert response.json() == {"word": "nonexistentword123", "ipa_translation": None, "error": "Translation not found"}

def test_get_valid_translation(client):
    response = client.get("/translate/fr/abdominales")
    assert response.status_code == 200
    assert response.json() == {"word": "abdominales", "ipa_translation": "ab.dɔ.mi.nal", "error": None}

def test_supported_languages(client):
    response = client.get("/languages")
    assert response.status_code == 200
    assert 'fr' in response.json()['languages']