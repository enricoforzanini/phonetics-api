# phonetics-api

**Note: this project is no longer deployed, the previous version at https://13.49.60.103.nip.io/homepage is no longer active.

The Phonetics API is a personal project designed to provide International Phonetic Alphabet (IPA) translations for words in multiple languages. The data used has been scraped from [wiktionary](https://www.wiktionary.org/) XML data dumps. Check the docs: [Swagger UI](https://13.49.60.103.nip.io/docs) or [ReDoc](https://13.49.60.103.nip.io/redoc). Test the API with a simple frontend at https://13.49.60.103.nip.io/homepage (for French only).

## Overview

* Technologies Used: Python, FastAPI, Pydantic, SQLite, Docker, AWS (ECR, S3, EC2).
* Features:
    * IPA translations for supported languages for single or multiple words.
    * Rate limiting.


## Usage

### Translate a single word (GET `/translate/{language}/{word}`)

This endpoint translates a single word provided as a URL parameter with its language code.

```bash
curl -X 'GET' \
  'https://13.49.60.103.nip.io/translate/fr/bonjour' \
  -H 'accept: application/json'
```

Or go to https://13.49.60.103.nip.io/translate/fr/bonjour directly.

### Translate multiple words (POST `/translate`)

This endpoint accepts JSON data with a language code and the list of words to be translated.

```bash
curl -X 'POST' \
  'https://13.49.60.103.nip.io/translate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"language": "fr", "words": ["bonjour", "monde"]}'
```

### Get supported languages (GET `/languages`)

This endpoint lists all the languages supported for translation.

```bash
curl -X 'GET' \
  'https://13.49.60.103.nip.io/languages' \
  -H 'accept: application/json'
```
Or go to https://13.49.60.103.nip.io/languages directly.

