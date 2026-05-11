from django.contrib import admin

from .models import (
    TrainingAnswer,
    TrainingAttempt,
    TrainingMaterial,
    TrainingProgress,
    TrainingQuestion,
    TrainingSlide,
    TrainingTest,
)


@admin.register(TrainingMaterial)
class TrainingMaterialAdmin(admin.ModelAdmin):
    list_display = ("title", "module_title", "order")
    list_filter = ("module_title",)
    search_fields = ("title", "module_title")
    ordering = ("module_title", "order")


@admin.register(TrainingSlide)
class TrainingSlideAdmin(admin.ModelAdmin):
    list_display = ("material", "order", "image_url_short")
    list_filter = ("material",)
    ordering = ("material", "order")

    def image_url_short(self, obj):
        return (obj.image_url or "")[:60]


@admin.register(TrainingProgress)
class TrainingProgressAdmin(admin.ModelAdmin):
    list_display = ("user", "material", "completed_slides", "total_slides", "is_completed", "updated_at")
    list_filter = ("is_completed", "material")
    search_fields = ("user__username", "user__first_name", "user__last_name")


@admin.register(TrainingTest)
class TrainingTestAdmin(admin.ModelAdmin):
    list_display = (
        "material",
        "title",
        "pass_threshold_percent",
        "require_all_other_materials_completed",
        "reset_all_training_progress_on_fail",
    )


@admin.register(TrainingQuestion)
class TrainingQuestionAdmin(admin.ModelAdmin):
    list_display = ("short_text", "test", "order", "question_type")
    list_filter = ("test", "question_type")

    def short_text(self, obj):
        return (obj.text or "")[:80]

    short_text.short_description = "Текст"


@admin.register(TrainingAnswer)
class TrainingAnswerAdmin(admin.ModelAdmin):
    list_display = ("text", "question", "is_correct", "correct_sequence")
    list_filter = ("is_correct", "question")


@admin.register(TrainingAttempt)
class TrainingAttemptAdmin(admin.ModelAdmin):
    list_display = ("user", "material", "score", "max_score", "passed", "created_at")
    list_filter = ("passed", "material")
    search_fields = ("user__username", "user__first_name", "user__last_name")
    readonly_fields = ("responses", "breakdown")

