from datetime import UTC, datetime
from pathlib import Path

import pytest

from transcript_router.models import Category, Classification, Transcription


@pytest.fixture
def vault(tmp_path: Path) -> Path:
    for sub in ("00_Inbox", "10_Meetings", "20_Notes", "30_Instructions", "40_Other"):
        (tmp_path / sub).mkdir()
    return tmp_path


@pytest.fixture
def sample_transcription() -> Transcription:
    return Transcription(
        id="sample-1",
        text="Тестовая транскрипция для проверки маршрутизатора.",
        created_at=datetime(2026, 5, 12, 9, 30, tzinfo=UTC),
        source_metadata={"source": "mock_plaud"},
    )


@pytest.fixture
def sample_classification() -> Classification:
    return Classification(
        category=Category.note,
        confidence=0.82,
        suggested_title="Тестовая заметка",
        key_points=["один", "два"],
        tags=["test", "demo"],
    )
