import random

from rest_framework import serializers

from .models import (
    TrainingAnswer,
    TrainingAttempt,
    TrainingMaterial,
    TrainingProgress,
    TrainingQuestion,
    TrainingSlide,
    TrainingTest,
)
from .test_access import test_availability


class TrainingSlideSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingSlide
        fields = ("id", "order", "image_url", "text")


class TrainingMaterialSerializer(serializers.ModelSerializer):
    slides = TrainingSlideSerializer(many=True, read_only=True)
    progress_percent = serializers.SerializerMethodField()
    attempts_used = serializers.SerializerMethodField()
    max_attempts = serializers.IntegerField(read_only=True, default=3)
    has_test = serializers.SerializerMethodField()
    pdf_url = serializers.SerializerMethodField()
    test_access_status = serializers.SerializerMethodField()
    test_access_message = serializers.SerializerMethodField()
    is_test_only = serializers.SerializerMethodField()
    is_completed = serializers.SerializerMethodField()
    completed_slides = serializers.SerializerMethodField()
    total_slides = serializers.SerializerMethodField()
    can_access_training_test = serializers.SerializerMethodField()

    class Meta:
        model = TrainingMaterial
        fields = (
            "id",
            "module_title",
            "title",
            "description",
            "content",
            "order",
            "slides",
            "pdf_url",
            "progress_percent",
            "is_completed",
            "completed_slides",
            "total_slides",
            "attempts_used",
            "max_attempts",
            "has_test",
            "test_access_status",
            "test_access_message",
            "is_test_only",
            "can_access_training_test",
        )

    def _get_progress(self, obj):
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return None
        try:
            return TrainingProgress.objects.get(user=user, material=obj)
        except TrainingProgress.DoesNotExist:
            return None

    def get_progress_percent(self, obj) -> int:
        prog = self._get_progress(obj)
        return prog.progress_percent if prog else 0

    def get_is_completed(self, obj) -> bool:
        prog = self._get_progress(obj)
        return bool(prog.is_completed) if prog else False

    def get_completed_slides(self, obj) -> int:
        prog = self._get_progress(obj)
        return prog.completed_slides if prog else 0

    def get_total_slides(self, obj) -> int:
        prog = self._get_progress(obj)
        return prog.total_slides if prog else 0

    def get_can_access_training_test(self, obj) -> bool:
        """Одинаково для всех материалов в ответе: только роль «intern»."""
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return False
        return getattr(user, "role", None) == "intern"

    def get_attempts_used(self, obj) -> int:
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return 0
        return TrainingAttempt.objects.filter(user=user, material=obj).count()

    def get_has_test(self, obj) -> bool:
        return hasattr(obj, "test")

    def get_pdf_url(self, obj) -> str:
        request = self.context.get("request")
        if getattr(obj, "pdf_file", None):
            url = obj.pdf_file.url
            return request.build_absolute_uri(url) if request else url
        content = (obj.content or "").strip()
        if content.startswith("PDF_URL:"):
            return content[len("PDF_URL:") :].strip()
        return ""

    def get_is_test_only(self, obj) -> bool:
        if not hasattr(obj, "test"):
            return False
        if self.get_pdf_url(obj):
            return False
        return not obj.slides.exists()

    def get_test_access_status(self, obj) -> str:
        if not hasattr(obj, "test"):
            return "none"
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return "none"
        _ok, st, _msg = test_availability(user, obj.test)
        return st

    def get_test_access_message(self, obj) -> str:
        if not hasattr(obj, "test"):
            return ""
        user = self.context.get("request").user if self.context.get("request") else None
        if not user or not user.is_authenticated:
            return ""
        ok, _st, msg = test_availability(user, obj.test)
        return "" if ok else (msg or "")


class TrainingAnswerSerializer(serializers.ModelSerializer):
    class Meta:
        model = TrainingAnswer
        fields = ("id", "text")


class TrainingQuestionSerializer(serializers.ModelSerializer):
    answers = serializers.SerializerMethodField()
    meta = serializers.SerializerMethodField()

    class Meta:
        model = TrainingQuestion
        fields = ("id", "text", "order", "question_type", "answers", "meta")

    def get_meta(self, obj: TrainingQuestion):
        if obj.question_type != TrainingQuestion.QuestionType.ORDER_JUDGMENT:
            return obj.meta or {}
        m = obj.meta or {}
        return {"statements": m.get("statements") or []}

    def get_answers(self, obj: TrainingQuestion):
        rows = list(obj.answers.all())
        if obj.question_type == TrainingQuestion.QuestionType.ORDERING:
            random.shuffle(rows)
        ser = TrainingAnswerSerializer(rows, many=True)
        return ser.data


class TrainingTestSerializer(serializers.ModelSerializer):
    questions = TrainingQuestionSerializer(many=True, read_only=True)

    class Meta:
        model = TrainingTest
        fields = (
            "id",
            "title",
            "pass_threshold_percent",
            "questions",
        )


class TrainingProgressSerializer(serializers.ModelSerializer):
    progress_percent = serializers.IntegerField(read_only=True)

    class Meta:
        model = TrainingProgress
        fields = (
            "id",
            "user",
            "material",
            "completed_slides",
            "total_slides",
            "is_completed",
            "updated_at",
            "progress_percent",
        )
        read_only_fields = ("user", "updated_at", "progress_percent")


class TrainingAttemptSerializer(serializers.ModelSerializer):
    percent = serializers.IntegerField(read_only=True)
    material_title = serializers.CharField(source="material.title", read_only=True)
    attempt_index = serializers.SerializerMethodField()

    class Meta:
        model = TrainingAttempt
        fields = (
            "id",
            "user",
            "material",
            "material_title",
            "score",
            "max_score",
            "passed",
            "created_at",
            "percent",
            "responses",
            "breakdown",
            "attempt_index",
        )
        read_only_fields = ("user", "created_at", "percent")

    def get_attempt_index(self, obj: TrainingAttempt) -> int:
        """Номер попытки по хронологии (1 — первая)."""
        qs = (
            TrainingAttempt.objects.filter(user=obj.user, material=obj.material)
            .order_by("created_at", "id")
            .values_list("id", flat=True)
        )
        ids = list(qs)
        try:
            return ids.index(obj.id) + 1
        except ValueError:
            return 0
