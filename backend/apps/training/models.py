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
        'Модуль / курс',
        max_length=255,
        default="Как работать с программой WB PVZ",
        help_text="Группа материалов (например, название курса)",
    )
    title = models.CharField('Название', max_length=255)
    description = models.TextField('Описание', blank=True)
    content = models.TextField('Содержание (текст)', blank=True)
    pdf_file = models.FileField('PDF-файл', upload_to="training/pdfs/", blank=True, null=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ("module_title", "order", "id")
        verbose_name = 'учебный материал'
        verbose_name_plural = 'учебные материалы'

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
        verbose_name='Материал',
    )
    image_url = models.CharField(
        'URL изображения',
        max_length=500,
        blank=True,
        help_text="URL картинки (обычно из /static/)",
    )
    text = models.TextField('Текст слайда', blank=True)
    order = models.PositiveIntegerField('Порядок', default=0)

    class Meta:
        ordering = ("order", "id")
        verbose_name = 'слайд'
        verbose_name_plural = 'слайды'

    def __str__(self):
        return f"{self.material.title} – шаг {self.order or self.id}"


class TrainingProgress(models.Model):
    """
    Прогресс пользователя по конкретному материалу.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    material = models.ForeignKey(
        TrainingMaterial,
        on_delete=models.CASCADE,
        verbose_name='Материал',
    )
    completed_slides = models.PositiveIntegerField('Пройдено слайдов', default=0)
    total_slides = models.PositiveIntegerField('Всего слайдов', default=0)
    is_completed = models.BooleanField('Завершено', default=False)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        unique_together = ("user", "material")
        verbose_name = 'прогресс обучения'
        verbose_name_plural = 'прогресс обучения'

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
        verbose_name='Материал',
    )
    title = models.CharField('Название теста', max_length=255, blank=True)
    pass_threshold_percent = models.PositiveIntegerField(
        'Порог сдачи (%)',
        default=90,
        help_text="Минимальный процент верных ответов для успешной сдачи (например, 90).",
    )
    require_all_other_materials_completed = models.BooleanField(
        'Сначала пройти все материалы',
        default=False,
        help_text="Если включено: тест доступен только после завершения всех остальных материалов в каталоге (кроме материала с этим тестом).",
    )
    reset_all_training_progress_on_fail = models.BooleanField(
        'Сбросить прогресс при провале',
        default=False,
        help_text="При неуспешной попытке удалить весь прогресс обучения пользователя (кроме самой попытки).",
    )

    class Meta:
        verbose_name = 'тест'
        verbose_name_plural = 'тесты'

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
        verbose_name='Тест',
    )
    text = models.TextField('Вопрос')
    order = models.PositiveIntegerField('Порядок', default=0)
    question_type = models.CharField(
        'Тип вопроса',
        max_length=32,
        choices=QuestionType.choices,
        default=QuestionType.SINGLE,
    )
    meta = models.JSONField(
        'Доп. данные (JSON)',
        blank=True,
        default=dict,
        help_text="Для order_judgment: statements, sequence_valid, correct_order (список номеров шагов).",
    )

    class Meta:
        ordering = ("order", "id")
        verbose_name = 'вопрос'
        verbose_name_plural = 'вопросы'

    def __str__(self):
        return f"Вопрос {self.order or self.id} ({self.test})"


class TrainingAnswer(models.Model):
    question = models.ForeignKey(
        TrainingQuestion,
        related_name="answers",
        on_delete=models.CASCADE,
        verbose_name='Вопрос',
    )
    text = models.CharField('Ответ', max_length=500)
    is_correct = models.BooleanField('Верный', default=False)
    correct_sequence = models.PositiveSmallIntegerField(
        'Порядок (для sorting)',
        default=0,
        help_text="Для типа «ordering»: правильный порядок шага (1…n). Для остальных — 0.",
    )

    class Meta:
        verbose_name = 'вариант ответа'
        verbose_name_plural = 'варианты ответов'

    def __str__(self):
        return self.text[:80]


class TrainingAttempt(models.Model):
    """
    Попытка прохождения теста по материалу.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    material = models.ForeignKey(
        TrainingMaterial,
        on_delete=models.CASCADE,
        verbose_name='Материал',
    )
    score = models.PositiveIntegerField('Баллы')
    max_score = models.PositiveIntegerField('Максимум баллов')
    passed = models.BooleanField('Сдан', default=False)
    created_at = models.DateTimeField('Дата попытки', auto_now_add=True)
    responses = models.JSONField('Ответы', default=dict, blank=True)
    breakdown = models.JSONField(
        'Разбор по вопросам',
        default=list,
        blank=True,
        help_text="По вопросам: ok, тип, как ответил стажёр (для администратора).",
    )

    class Meta:
        ordering = ("-created_at",)
        verbose_name = 'попытка теста'
        verbose_name_plural = 'попытки тестов'

    @property
    def percent(self) -> int:
        if self.max_score <= 0:
            return 0
        return int(round(min(100, (self.score / self.max_score) * 100)))
