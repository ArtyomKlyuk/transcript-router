from datetime import UTC, datetime
from typing import Any

import pytest

from transcript_router.classifier import Classifier, ClassifierError
from transcript_router.models import Category, Transcription
from transcript_router.sources import MockPlaudSource


def _make_transcription(text: str) -> Transcription:
    return Transcription(
        id="t",
        text=text,
        created_at=datetime(2026, 5, 12, tzinfo=UTC),
        source_metadata={"source": "test"},
    )


async def test_classifies_all_mock_fixtures() -> None:
    classifier = Classifier(client=None, model="stub")

    seen: set[Category] = set()
    async for transcription in MockPlaudSource():
        result = await classifier.classify(transcription)
        seen.add(result.category)
        assert 0.0 <= result.confidence <= 1.0
        assert result.suggested_title

    assert {Category.meeting, Category.note, Category.instruction} <= seen


async def test_supplier_branch_returns_meeting() -> None:
    classifier = Classifier(client=None, model="stub")
    result = await classifier.classify(_make_transcription("Встреча с поставщиком офисной мебели"))

    assert result.category is Category.meeting
    assert "supplier" in result.tags


async def test_unknown_text_falls_back_to_other() -> None:
    classifier = Classifier(client=None, model="stub")
    result = await classifier.classify(_make_transcription("случайная строка без ключевых слов"))

    assert result.category is Category.other


async def test_invalid_payload_raises_classifier_error(monkeypatch: pytest.MonkeyPatch) -> None:
    classifier = Classifier(client=None, model="stub")

    async def broken(_self: Classifier, _text: str) -> dict[str, Any]:
        return {"category": "not-a-real-category", "confidence": 2.0, "suggested_title": ""}

    monkeypatch.setattr(Classifier, "_call_llm", broken)

    with pytest.raises(ClassifierError):
        await classifier.classify(_make_transcription("anything"))
