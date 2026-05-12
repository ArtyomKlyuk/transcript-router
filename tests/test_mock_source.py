from transcript_router.models import Transcription
from transcript_router.sources import MockPlaudSource, TranscriptionSource


async def test_mock_source_yields_five_transcriptions() -> None:
    source = MockPlaudSource()
    items = [item async for item in source]

    assert len(items) == 5
    assert all(isinstance(item, Transcription) for item in items)
    assert len({item.id for item in items}) == 5


async def test_mock_source_satisfies_protocol() -> None:
    assert isinstance(MockPlaudSource(), TranscriptionSource)


async def test_mock_source_attaches_source_metadata() -> None:
    items = [item async for item in MockPlaudSource()]
    assert all(item.source_metadata["source"] == "mock_plaud" for item in items)
