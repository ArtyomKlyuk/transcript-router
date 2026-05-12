from datetime import UTC, datetime
from pathlib import Path

import pytest
import yaml

from transcript_router.models import Category, Classification, Transcription
from transcript_router.router import DEFAULT_CATEGORY_DIRS, Router


def test_write_places_file_into_category_folder(
    vault: Path, sample_transcription: Transcription, sample_classification: Classification
) -> None:
    router = Router(vault)
    path = router.write(sample_transcription, sample_classification)

    assert path.parent == vault / "20_Notes"
    assert path.suffix == ".md"


def test_filename_uses_slug_and_date(vault: Path, sample_transcription: Transcription) -> None:
    classification = Classification(
        category=Category.meeting,
        confidence=0.9,
        suggested_title="Встреча с поставщиком мебели",
        key_points=[],
        tags=[],
    )
    path = Router(vault).write(sample_transcription, classification)

    assert path.name == "vstrecha-s-postavshchikom-mebeli-20260512.md"


def test_frontmatter_contains_expected_keys(
    vault: Path, sample_transcription: Transcription, sample_classification: Classification
) -> None:
    path = Router(vault).write(sample_transcription, sample_classification)
    content = path.read_text(encoding="utf-8")

    head, _, body = content.partition("---\n")[2].partition("\n---\n")
    fm = yaml.safe_load(head)

    assert set(fm) == {"created", "category", "source", "tags"}
    assert fm["category"] == "note"
    assert fm["source"] == "mock_plaud"
    assert fm["tags"] == ["test", "demo"]
    assert "Тестовая транскрипция" in body


def test_all_default_categories_have_mapping() -> None:
    assert set(DEFAULT_CATEGORY_DIRS) == set(Category)


def test_apply_client_routing_rules_is_unimplemented(
    vault: Path, sample_transcription: Transcription
) -> None:
    with pytest.raises(NotImplementedError, match="per-engagement"):
        Router(vault).apply_client_routing_rules(sample_transcription, Category.note)


def test_untitled_when_slug_collapses_to_empty(vault: Path) -> None:
    classification = Classification(
        category=Category.other,
        confidence=0.5,
        suggested_title="...",
        key_points=[],
        tags=[],
    )
    transcription = Transcription(
        id="x",
        text="text",
        created_at=datetime(2026, 1, 2, tzinfo=UTC),
        source_metadata={},
    )
    path = Router(vault).write(transcription, classification)

    assert path.name == "untitled-20260102.md"
