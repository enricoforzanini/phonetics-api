from fastapi.testclient import TestClient
from app import main

client = TestClient(main.app)

def test_catch_all():
    response = client.get("/test/random/path")
    assert response.status_code == 404
    assert response.json() == {"detail": "Endpoint not found. Please check the URL."}

def test_translate_language_not_found():
    data = {
        "language": "fakelanguage",
        "words": ["hello"]
    }
    response = client.post("/translate", json=data)
    assert response.status_code == 404
    assert response.json() == {"detail": "Language not available"}

def test_valid_translation_one_word():
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

def test_valid_translation_two_words():
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

def test_translation_one_error():
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