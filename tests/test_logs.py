import pytest
from loguru import logger
from _pytest.logging import LogCaptureFixture
from fastapi.testclient import TestClient
from app import main

@pytest.fixture # from https://loguru.readthedocs.io/en/stable/resources/migration.html#replacing-caplog-fixture-from-pytest-library
def caplog(caplog: LogCaptureFixture):
    handler_id = logger.add(
        caplog.handler,
        format="{message}",
        level=0,
        filter=lambda record: record["level"].no >= caplog.handler.level,
        enqueue=False,
    )
    yield caplog
    logger.remove(handler_id)

def test_translation_logging(caplog):
    client = TestClient(main.app)
    data = {
        "language": "fr",
        "words": ["inexistantwordinfrench"]
    }
    response = client.post("/translate", json=data)
    assert "No translation found for fr/inexistantwordinfrench" in caplog.text
