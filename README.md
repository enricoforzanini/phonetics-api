# phonetics-api

The Phonetics API is a personal project designed to provide International Phonetic Alphabet (IPA) translations for words in multiple languages. The data used has been scraped from [wiktionary](https://www.wiktionary.org/) XML data dumps. Check the docs: [Swagger UI](http://13.49.60.103/docs) or [ReDoc](http://13.49.60.103/redoc).

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
  'http://13.49.60.103/translate/fr/bonjour' \
  -H 'accept: application/json'
```

Or go to http://13.49.60.103/translate/fr/bonjour directly.

### Translate multiple words (POST `/translate`)

This endpoint accepts JSON data with a language code and the list of words to be translated.

```bash
curl -X 'POST' \
  'http://13.49.60.103/translate' \
  -H 'accept: application/json' \
  -H 'Content-Type: application/json' \
  -d '{"language": "fr", "words": ["bonjour", "monde"]}'
```

### Get supported languages (GET `/languages`)

This endpoint lists all the languages supported for translation.

```bash
curl -X 'GET' \
  'http://13.49.60.103/languages' \
  -H 'accept: application/json'
```
Or go to http://13.49.60.103/languages directly.

