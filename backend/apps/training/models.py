from django.conf import settings
from django.db import models


class TrainingMaterial(models.Model):
    """
    Учебный материал (урок).

    module_title  – группа материалов, например «Как работать с программой WB PVZ».
    title         – конкретная инструкция, например «Инструкция по приемке товара».
    description   – текстовое описание/подводка.
    content       – legacy‑поле, можно использовать под разметку или заметки.
    """

    module_title = models.CharField(
        max_length=255,
        default="Как работать с программой WB PVZ",
        help_text="Группа материалов (например, название курса)",
    )
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    content = models.TextField(blank=True)
    pdf_file = models.FileField(upload_to="training/pdfs/", blank=True, null=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("module_title", "order", "id")

    def __str__(self):
        return f"{self.module_title} / {self.title}"


class TrainingSlide(models.Model):
    """
    Отдельный шаг инструкции (слайд): картинка + пояснение.
    """

    material = models.ForeignKey(
        TrainingMaterial,
        related_name="slides",
        on_delete=models.CASCADE,
    )
    image_url = models.CharField(
        max_length=500,
        blank=True,
        help_text="URL картинки (обычно из /static/)",
    )
    text = models.TextField(blank=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"{self.material.title} – шаг {self.order or self.id}"


class TrainingProgress(models.Model):
    """
    Прогресс пользователя по конкретному материалу.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    material = models.ForeignKey(TrainingMaterial, on_delete=models.CASCADE)
    completed_slides = models.PositiveIntegerField(default=0)
    total_slides = models.PositiveIntegerField(default=0)
    is_completed = models.BooleanField(default=False)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ("user", "material")

    @property
    def progress_percent(self) -> int:
        if self.total_slides <= 0:
            return 0
        return int(round(min(100, (self.completed_slides / self.total_slides) * 100)))


class TrainingTest(models.Model):
    """
    Тест к материалу.
    """

    material = models.OneToOneField(
        TrainingMaterial,
        related_name="test",
        on_delete=models.CASCADE,
    )
    title = models.CharField(max_length=255, blank=True)
    pass_threshold_percent = models.PositiveIntegerField(
        default=90,
        help_text="Минимальный процент верных ответов для успешной сдачи (например, 90).",
    )
    require_all_other_materials_completed = models.BooleanField(
        default=False,
        help_text="Если включено: тест доступен только после завершения всех остальных материалов в каталоге (кроме материала с этим тестом).",
    )
    reset_all_training_progress_on_fail = models.BooleanField(
        default=False,
        help_text="При неуспешной попытке удалить весь прогресс обучения пользователя (кроме самой попытки).",
    )

    def __str__(self):
        return self.title or f"Тест для «{self.material.title}»"


class TrainingQuestion(models.Model):
    class QuestionType(models.TextChoices):
        SINGLE = "single", "Один ответ"
        MULTIPLE = "multiple", "Несколько ответов"
        ORDERING = "ordering", "Установить порядок"
        ORDER_JUDGMENT = "order_judgment", "Проверка порядка (верно/неверно)"

    test = models.ForeignKey(
        TrainingTest,
        related_name="questions",
        on_delete=models.CASCADE,
    )
    text = models.TextField()
    order = models.PositiveIntegerField(default=0)
    question_type = models.CharField(
        max_length=32,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
    )
    meta = models.JSONField(
        blank=True,
        default=dict,
        help_text="Для order_judgment: statements, sequence_valid, correct_order (список номеров шагов).",
    )

    class Meta:
        ordering = ("order", "id")

    def __str__(self):
        return f"Вопрос {self.order or self.id} ({self.test})"


class TrainingAnswer(models.Model):
    question = models.ForeignKey(
        TrainingQuestion,
        related_name="answers",
        on_delete=models.CASCADE,
    )
    text = models.CharField(max_length=500)
    is_correct = models.BooleanField(default=False)
    correct_sequence = models.PositiveSmallIntegerField(
        default=0,
        help_text="Для типа «ordering»: правильный порядок шага (1…n). Для остальных — 0.",
    )

    def __str__(self):
        return self.text[:80]


class TrainingAttempt(models.Model):
    """
    Попытка прохождения теста по материалу.
    """

    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    material = models.ForeignKey(TrainingMaterial, on_delete=models.CASCADE)
    score = models.PositiveIntegerField()
    max_score = models.PositiveIntegerField()
    passed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    responses = models.JSONField(default=dict, blank=True)
    breakdown = models.JSONField(
        default=list,
        blank=True,
        help_text="По вопросам: ok, тип, как ответил стажёр (для администратора).",
    )

    class Meta:
        ordering = ("-created_at",)

    @property
    def percent(self) -> int:
        if self.max_score <= 0:
            return 0
        return int(round(min(100, (self.score / self.max_score) * 100)))
