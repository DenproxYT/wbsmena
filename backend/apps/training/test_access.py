from __future__ import annotations

from typing import Literal, Tuple

from .models import TrainingAttempt, TrainingMaterial, TrainingProgress, TrainingTest

Status = Literal["available", "locked", "exhausted", "passed"]


def test_availability(user, test: TrainingTest) -> Tuple[bool, Status, str]:
    """
    Можно ли начать/продолжить тест (новая попытка).
    """
    if TrainingAttempt.objects.filter(user=user, material=test.material, passed=True).exists():
        return False, "passed", "Тест уже успешно пройден."

    used = TrainingAttempt.objects.filter(user=user, material=test.material).count()
    if used >= 3:
        return False, "exhausted", "Исчерпаны 3 попытки. Обратитесь к администратору."

    if test.require_all_other_materials_completed:
        others = TrainingMaterial.objects.exclude(pk=test.material_id)
        for m in others:
            prog = TrainingProgress.objects.filter(user=user, material=m).first()
            if not prog or not prog.is_completed:
                return (
                    False,
                    "locked",
                    f"Сначала завершите обучающий материал: «{m.title}».",
                )

    return True, "available", ""


def reset_all_user_progress(user) -> int:
    """Удаляет весь прогресс обучения пользователя. Возвращает число удалённых записей."""
    qs = TrainingProgress.objects.filter(user=user)
    n = qs.count()
    qs.delete()
    return n
