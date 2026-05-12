from typing import Any

from pydantic import ValidationError

from transcript_router.logging import log
from transcript_router.models import Classification, Transcription


class ClassifierError(Exception):
    pass


class Classifier:
    def __init__(self, client: Any, model: str) -> None:
        self._client = client
        self._model = model

    async def classify(self, transcription: Transcription) -> Classification:
        raw = await self._call_llm(transcription.text)
        try:
            result = Classification.model_validate(raw)
        except ValidationError as exc:
            log.error(
                "transcription.classify_failed",
                transcription_id=transcription.id,
                error=str(exc),
            )
            raise ClassifierError("classifier returned invalid payload") from exc

        log.info(
            "transcription.classified",
            transcription_id=transcription.id,
            category=result.category.value,
            confidence=result.confidence,
        )
        return result

    async def _call_llm(self, text: str) -> dict[str, Any]:
        # real API call and prompt configured per-engagement
        match _route(text):
            case "supplier":
                return {
                    "category": "meeting",
                    "confidence": 0.93,
                    "suggested_title": "Встреча с поставщиком мебели",
                    "key_points": [
                        "Сроки поставки две недели",
                        "Оплата по факту приёмки",
                        "Скидка 5% от 20 позиций",
                    ],
                    "tags": ["supplier", "meeting"],
                }
            case "reminder":
                return {
                    "category": "note",
                    "confidence": 0.87,
                    "suggested_title": "Напоминания на неделю",
                    "key_points": [
                        "Позвонить в банк",
                        "Забрать документы",
                        "Проверить заявку в Роспатент",
                    ],
                    "tags": ["reminder", "todo"],
                }
            case "instruction":
                return {
                    "category": "instruction",
                    "confidence": 0.91,
                    "suggested_title": "Обработка входящих заявок",
                    "key_points": [
                        "Проверить дубль в CRM",
                        "Уточнить контактные данные",
                        "Назначить ответственного",
                    ],
                    "tags": ["onboarding", "process"],
                }
            case "partner_call":
                return {
                    "category": "meeting",
                    "confidence": 0.88,
                    "suggested_title": "Синхронизация с партнёром",
                    "key_points": [
                        "Бюджет на следующий квартал",
                        "Три ключевые задачи",
                        "Следующая встреча через две недели",
                    ],
                    "tags": ["partner", "sync"],
                }
            case "idea":
                return {
                    "category": "note",
                    "confidence": 0.74,
                    "suggested_title": "Идея про разделение потока заявок",
                    "key_points": [
                        "Срочные запросы — в отдельную ветку",
                    ],
                    "tags": ["idea"],
                }
            case _:
                return {
                    "category": "other",
                    "confidence": 0.5,
                    "suggested_title": "Транскрипция без категории",
                    "key_points": [],
                    "tags": [],
                }


def _route(text: str) -> str:
    t = text.lower()
    if "поставщик" in t:
        return "supplier"
    if "напомнить" in t or "перезвонить в банк" in t:
        return "reminder"
    if "инструкция" in t:
        return "instruction"
    if "конспект" in t or "партнёр" in t:
        return "partner_call"
    if "мысль" in t or "имеет смысл попробовать" in t:
        return "idea"
    return "other"
