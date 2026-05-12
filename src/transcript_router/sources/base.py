from collections.abc import AsyncIterator
from typing import Protocol, runtime_checkable

from transcript_router.models import Transcription


@runtime_checkable
class TranscriptionSource(Protocol):
    def __aiter__(self) -> AsyncIterator[Transcription]: ...
