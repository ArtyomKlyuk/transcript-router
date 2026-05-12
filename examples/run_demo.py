from __future__ import annotations

import asyncio

from transcript_router import pipeline
from transcript_router.classifier import Classifier
from transcript_router.config import Settings
from transcript_router.logging import configure_logging, log
from transcript_router.router import Router
from transcript_router.sources import MockPlaudSource


async def main() -> None:
    settings = Settings()
    configure_logging(settings.log_level)

    source = MockPlaudSource()
    classifier = Classifier(client=None, model=settings.anthropic_model)
    router = Router(settings.vault_path)

    written = await pipeline.run(source, classifier, router)
    log.info("demo.finished", files=[str(p) for p in written])


if __name__ == "__main__":
    asyncio.run(main())
