import pytest
from app import main
from fastapi.testclient import TestClient
from loguru import logger
from _pytest.logging import LogCaptureFixture

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
   client.get("/translate/fr/famille")
   assert "Translation found for fr/famille" in caplog.text
   client.get("/translate/fr/inexistantwordinfrench")
   assert "No translation found for fr/inexistantwordinfrench" in caplog.text
