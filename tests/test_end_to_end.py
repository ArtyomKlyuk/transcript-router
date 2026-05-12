from pathlib import Path

from transcript_router import pipeline
from transcript_router.classifier import Classifier
from transcript_router.router import Router
from transcript_router.sources import MockPlaudSource


async def test_end_to_end_writes_all_files(vault: Path) -> None:
    written = await pipeline.run(
        MockPlaudSource(),
        Classifier(client=None, model="stub"),
        Router(vault),
    )

    assert len(written) == 5
    assert all(p.exists() for p in written)
    assert all(p.parent.parent == vault for p in written)

    folders = {p.parent.name for p in written}
    assert "10_Meetings" in folders
    assert "20_Notes" in folders
    assert "30_Instructions" in folders
