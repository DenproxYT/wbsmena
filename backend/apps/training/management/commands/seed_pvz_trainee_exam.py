from django.core.management.base import BaseCommand
from django.db import transaction

from apps.training.models import (
    TrainingAnswer,
    TrainingMaterial,
    TrainingQuestion,
    TrainingTest,
)
from apps.training.pvz_exam_data import EXAM_MATERIAL, EXAM_TEST, QUESTIONS


class Command(BaseCommand):
    help = "Создаёт материал и итоговый тест ПВЗ (30 вопросов). Повторный запуск пересоздаёт вопросы теста."

    @transaction.atomic
    def handle(self, *args, **options):
        m_defaults = {
            "module_title": EXAM_MATERIAL["module_title"],
            "description": EXAM_MATERIAL["description"],
            "order": EXAM_MATERIAL["order"],
            "content": EXAM_MATERIAL["content"],
        }
        material, created = TrainingMaterial.objects.get_or_create(
            title=EXAM_MATERIAL["title"],
            defaults=m_defaults,
        )
        if not created:
            TrainingMaterial.objects.filter(pk=material.pk).update(**m_defaults)

        test, _ = TrainingTest.objects.update_or_create(
            material=material,
            defaults={
                "title": EXAM_TEST["title"],
                "pass_threshold_percent": EXAM_TEST["pass_threshold_percent"],
                "require_all_other_materials_completed": EXAM_TEST[
                    "require_all_other_materials_completed"
                ],
                "reset_all_training_progress_on_fail": EXAM_TEST["reset_all_training_progress_on_fail"],
            },
        )

        TrainingQuestion.objects.filter(test=test).delete()

        type_map = {
            "single": TrainingQuestion.QuestionType.SINGLE,
            "multiple": TrainingQuestion.QuestionType.MULTIPLE,
            "ordering": TrainingQuestion.QuestionType.ORDERING,
            "order_judgment": TrainingQuestion.QuestionType.ORDER_JUDGMENT,
        }

        for spec in QUESTIONS:
            qtype = type_map[spec["type"]]
            meta = {}
            if qtype == TrainingQuestion.QuestionType.ORDER_JUDGMENT:
                meta = spec.get("meta") or {}

            q = TrainingQuestion.objects.create(
                test=test,
                text=spec["text"],
                order=spec["order"],
                question_type=qtype,
                meta=meta,
            )

            if qtype == TrainingQuestion.QuestionType.ORDER_JUDGMENT:
                continue

            if qtype == TrainingQuestion.QuestionType.ORDERING:
                for i, text in enumerate(spec["steps"], start=1):
                    TrainingAnswer.objects.create(
                        question=q,
                        text=text,
                        is_correct=False,
                        correct_sequence=i,
                    )
                continue

            for opt in spec.get("options") or []:
                TrainingAnswer.objects.create(
                    question=q,
                    text=opt["text"],
                    is_correct=bool(opt.get("correct")),
                    correct_sequence=0,
                )

        self.stdout.write(self.style.SUCCESS(f"Готово: материал id={material.id}, тест id={test.id}, вопросов: {len(QUESTIONS)}"))
