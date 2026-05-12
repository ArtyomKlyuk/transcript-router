from collections.abc import Mapping
from pathlib import Path
from types import MappingProxyType

import yaml
from slugify import slugify

from transcript_router.models import Category, Classification, Transcription

DEFAULT_CATEGORY_DIRS: Mapping[Category, str] = MappingProxyType(
    {
        Category.meeting: "10_Meetings",
        Category.note: "20_Notes",
        Category.instruction: "30_Instructions",
        Category.other: "40_Other",
    }
)


class Router:
    def __init__(
        self,
        vault_path: Path,
        category_dirs: Mapping[Category, str] = DEFAULT_CATEGORY_DIRS,
    ) -> None:
        self._vault_path = vault_path
        self._category_dirs = category_dirs

    def write(self, transcription: Transcription, classification: Classification) -> Path:
        folder = self._vault_path / self._category_dirs[classification.category]
        folder.mkdir(parents=True, exist_ok=True)

        date_part = transcription.created_at.strftime("%Y%m%d")
        slug = slugify(classification.suggested_title, max_length=80) or "untitled"
        path = folder / f"{slug}-{date_part}.md"

        path.write_text(_render(transcription, classification), encoding="utf-8")
        return path

    def apply_client_routing_rules(self, transcription: Transcription, category: Category) -> Path:
        raise NotImplementedError("client-specific routing rules configured per-engagement")


def _render(transcription: Transcription, classification: Classification) -> str:
    frontmatter = {
        "created": transcription.created_at.isoformat(),
        "category": classification.category.value,
        "source": transcription.source_metadata.get("source", "unknown"),
        "tags": classification.tags,
    }
    fm_text = yaml.safe_dump(frontmatter, allow_unicode=True, sort_keys=True).rstrip()

    body_parts = [f"# {classification.suggested_title}", "", transcription.text.strip()]
    if classification.key_points:
        body_parts += ["", "## Ключевые моменты", ""]
        body_parts += [f"- {point}" for point in classification.key_points]
    body = "\n".join(body_parts)

    return f"---\n{fm_text}\n---\n\n{body}\n"
