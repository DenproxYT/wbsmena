"""
Оценивание попыток теста (разные типы вопросов).
"""
from __future__ import annotations

import re
from typing import Any, Dict, List, Optional, Tuple

from .models import TrainingAnswer, TrainingQuestion


def _answer_labels(question: TrainingQuestion, ids: List[int]) -> str:
    if not ids:
        return "—"
    by_id = {a.id: a.text for a in question.answers.all()}
    parts = [by_id.get(i, str(i)) for i in ids]
    return "; ".join(parts)


def _normalize_order_digits(s: str) -> List[int]:
    if not s:
        return []
    return [int(x) for x in re.findall(r"\d+", str(s))]


def grade_single(question: TrainingQuestion, raw: Any) -> Tuple[bool, str, Dict[str, Any]]:
    try:
        aid = int(raw)
    except (TypeError, ValueError):
        return False, "—", {"answer_id": raw}
    try:
        ans = question.answers.get(pk=aid)
    except TrainingAnswer.DoesNotExist:
        return False, str(raw), {"answer_id": aid}
    ok = bool(ans.is_correct)
    return ok, ans.text, {"answer_id": aid}


def grade_multiple(question: TrainingQuestion, raw: Any) -> Tuple[bool, str, Dict[str, Any]]:
    if raw is None:
        ids = []
    elif isinstance(raw, list):
        ids = []
        for x in raw:
            try:
                ids.append(int(x))
            except (TypeError, ValueError):
                continue
    else:
        try:
            ids = [int(raw)]
        except (TypeError, ValueError):
            ids = []
    correct_ids = sorted(a.id for a in question.answers.all() if a.is_correct)
    got = sorted(set(ids))
    ok = got == correct_ids
    label = _answer_labels(question, got)
    return ok, label, {"answer_ids": got}


def grade_ordering(question: TrainingQuestion, raw: Any) -> Tuple[bool, str, Dict[str, Any]]:
    if not isinstance(raw, list):
        return False, "—", {"ordered_ids": raw}
    ids = []
    for x in raw:
        try:
            ids.append(int(x))
        except (TypeError, ValueError):
            continue
    answers = list(question.answers.all())
    if len(ids) != len(answers) or set(ids) != {a.id for a in answers}:
        return False, _answer_labels(question, ids), {"ordered_ids": ids}

    canonical = sorted(answers, key=lambda a: (a.correct_sequence or 0, a.id))
    ok = ids == [a.id for a in canonical]
    return ok, _answer_labels(question, ids), {"ordered_ids": ids}


def grade_order_judgment(question: TrainingQuestion, raw: Any) -> Tuple[bool, str, Dict[str, Any]]:
    meta = question.meta or {}
    statements: List[str] = list(meta.get("statements") or [])
    sequence_valid = bool(meta.get("sequence_valid"))
    correct_order = list(meta.get("correct_order") or [])

    if not isinstance(raw, dict):
        return False, "—", {"raw": raw}

    judgment = (raw.get("judgment") or "").strip().lower()
    user_says_valid = judgment == "valid"
    user_says_invalid = judgment == "invalid"

    order_str = raw.get("order") or raw.get("correction") or ""

    admin_extra: Dict[str, Any] = {"judgment": judgment, "order_input": order_str}

    if sequence_valid:
        ok = user_says_valid and not user_says_invalid
        label = "Правильно" if user_says_valid else ("Неправильно" if user_says_invalid else "—")
        return ok, label, admin_extra

    # sequence shown is NOT valid — need "incorrect" + matching order
    if not user_says_invalid:
        label = "Правильно" if user_says_valid else "—"
        return False, label, admin_extra

    user_order = _normalize_order_digits(order_str)
    co = [int(x) for x in correct_order]
    ok = user_order == co
    label = f"Неправильно; порядок: {order_str or '—'}"
    admin_extra["parsed_order"] = user_order
    admin_extra["expected_order"] = co
    return ok, label, admin_extra


def grade_question(question: TrainingQuestion, raw: Any) -> Tuple[bool, str, Dict[str, Any]]:
    t = question.question_type
    if t == TrainingQuestion.QuestionType.SINGLE:
        return grade_single(question, raw)
    if t == TrainingQuestion.QuestionType.MULTIPLE:
        return grade_multiple(question, raw)
    if t == TrainingQuestion.QuestionType.ORDERING:
        return grade_ordering(question, raw)
    if t == TrainingQuestion.QuestionType.ORDER_JUDGMENT:
        return grade_order_judgment(question, raw)
    return grade_single(question, raw)


def grade_full_test(
    questions: List[TrainingQuestion], answers_payload: Dict[str, Any]
) -> Tuple[int, int, List[Dict[str, Any]]]:
    """
    Возвращает (score, max_score, breakdown_rows).
    """
    breakdown: List[Dict[str, Any]] = []
    score = 0
    max_score = len(questions)
    for q in questions:
        key = str(q.id)
        raw = answers_payload.get(key)
        if raw is None:
            raw = answers_payload.get(q.id)
        ok, label, extra = grade_question(q, raw)
        if ok:
            score += 1
        breakdown.append(
            {
                "question_id": q.id,
                "question_order": q.order,
                "question_type": q.question_type,
                "text": q.text[:500],
                "ok": ok,
                "user_answer_summary": label,
                "detail": extra,
            }
        )
    return score, max_score, breakdown


def build_trainee_review(breakdown: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """Без раскрытия правильного ответа: только подсветка ошибок."""
    out: List[Dict[str, Any]] = []
    for row in breakdown:
        item = {
            "question_id": row["question_id"],
            "ok": row["ok"],
            "your_answer": row.get("user_answer_summary") or "",
        }
        if not row["ok"]:
            item["wrong"] = True
        out.append(item)
    return out
