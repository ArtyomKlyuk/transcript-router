import asyncio
from pathlib import Path

from transcript_router.classifier import Classifier
from transcript_router.logging import log
from transcript_router.models import Transcription
from transcript_router.router import Router
from transcript_router.sources import TranscriptionSource


async def run(source: TranscriptionSource, classifier: Classifier, router: Router) -> list[Path]:
    queue: asyncio.Queue[Transcription | None] = asyncio.Queue()
    written: list[Path] = []

    async def producer() -> None:
        async for item in source:
            await queue.put(item)
        await queue.put(None)

    async def consumer() -> None:
        while True:
            item = await queue.get()
            if item is None:
                return
            classification = await classifier.classify(item)
            path = router.write(item, classification)
            log.info("transcription.routed", transcription_id=item.id, path=str(path))
            written.append(path)

    await asyncio.gather(producer(), consumer())
    return written
