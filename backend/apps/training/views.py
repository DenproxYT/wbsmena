from django.contrib.auth import get_user_model
from rest_framework import generics, permissions, status
from rest_framework.response import Response
from rest_framework.views import APIView

from .grading import build_trainee_review, grade_full_test
from .models import (
    TrainingAttempt,
    TrainingMaterial,
    TrainingProgress,
    TrainingTest,
)
from .serializers import (
    TrainingAttemptSerializer,
    TrainingMaterialSerializer,
    TrainingProgressSerializer,
    TrainingTestSerializer,
)
from .test_access import reset_all_user_progress, test_availability

def is_training_admin(user):
    if not user or not user.is_authenticated:
        return False
    if user.is_staff or user.is_superuser:
        return True
    return getattr(user, 'role', None) in ('administrator', 'owner')


def is_training_intern(user) -> bool:
    """Итоговое тестирование доступно только пользователям со ролью «Стажёр»."""
    if not user or not user.is_authenticated:
        return False
    return getattr(user, 'role', None) == 'intern'


class TrainingListCreateView(generics.ListCreateAPIView):
    """
    Список учебных материалов с вложенными слайдами и прогрессом текущего пользователя.
    """

    queryset = TrainingMaterial.objects.prefetch_related(
        "slides",
        "test",
        "test__questions",
        "test__questions__answers",
    ).all()
    serializer_class = TrainingMaterialSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_context(self):
        ctx = super().get_serializer_context()
        ctx["request"] = self.request
        return ctx

    def perform_create(self, serializer):
        if not is_training_admin(self.request.user):
            from rest_framework.exceptions import PermissionDenied
            raise PermissionDenied("Добавлять материалы могут только администратор и владелец")
        serializer.save()


class TrainingProgressView(generics.ListCreateAPIView):
    """
    Создание/обновление прогресса по материалу и получение списка прогресса для текущего пользователя.
    """

    serializer_class = TrainingProgressSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        qs = TrainingProgress.objects.select_related("material", "user")
        # Админ может смотреть всех, обычный пользователь — только себя
        if not is_training_admin(user):
            qs = qs.filter(user=user)
        return qs

    def perform_create(self, serializer):
        user = self.request.user
        material = serializer.validated_data["material"]
        completed = serializer.validated_data.get("completed_slides", 0)
        total = serializer.validated_data.get("total_slides", 0)
        obj, _ = TrainingProgress.objects.update_or_create(
            user=user,
            material=material,
            defaults={
                "completed_slides": completed,
                "total_slides": total,
                "is_completed": serializer.validated_data.get("is_completed", False),
            },
        )
        self._instance = obj

    def create(self, request, *args, **kwargs):
        response = super().create(request, *args, **kwargs)
        # Пересериализуем фактический объект из update_or_create
        if hasattr(self, "_instance"):
            response.data = TrainingProgressSerializer(self._instance).data
        return response


class TrainingTestDetailView(APIView):
    """
    Получение теста по материалу (вопросы + варианты без признака правильности).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request, material_id: int):
        try:
            test = (
                TrainingTest.objects.prefetch_related("questions", "questions__answers")
                .get(material_id=material_id)
            )
        except TrainingTest.DoesNotExist:
            return Response({"detail": "Тест для этого материала не найден."}, status=status.HTTP_404_NOT_FOUND)

        user = request.user
        if not is_training_intern(user):
            return Response(
                {"detail": "Тестирование доступно только стажёрам."},
                status=status.HTTP_403_FORBIDDEN,
            )

        ok, st, msg = test_availability(user, test)
        attempts_used = TrainingAttempt.objects.filter(user=user, material=test.material).count()

        if st == "passed":
            last = (
                TrainingAttempt.objects.filter(user=user, material=test.material, passed=True)
                .order_by("-created_at")
                .first()
            )
            return Response(
                {
                    "already_passed": True,
                    "title": test.title,
                    "pass_threshold_percent": test.pass_threshold_percent,
                    "last_score": last.score if last else None,
                    "last_max_score": last.max_score if last else None,
                    "last_percent": last.percent if last else None,
                    "message": "Вы уже успешно прошли этот тест.",
                }
            )

        if not ok:
            return Response(
                {
                    "detail": msg,
                    "status": st,
                    "attempts_used": attempts_used,
                    "max_attempts": 3,
                },
                status=status.HTTP_403_FORBIDDEN,
            )

        serializer = TrainingTestSerializer(test)
        data = dict(serializer.data)
        data["attempts_used"] = attempts_used
        data["max_attempts"] = 3
        return Response(data)


class TrainingTestAttemptView(APIView):
    """
    Отправка ответов. Формат answers: см. документацию API (single / multiple / ordering / order_judgment).
    """

    permission_classes = [permissions.IsAuthenticated]

    MAX_ATTEMPTS = 3

    def post(self, request, material_id: int):
        user = request.user
        if not is_training_intern(user):
            return Response(
                {"detail": "Тестирование доступно только стажёрам."},
                status=status.HTTP_403_FORBIDDEN,
            )
        try:
            test = TrainingTest.objects.get(material_id=material_id)
        except TrainingTest.DoesNotExist:
            return Response({"detail": "Тест для этого материала не найден."}, status=status.HTTP_404_NOT_FOUND)

        if TrainingAttempt.objects.filter(user=user, material=test.material, passed=True).exists():
            return Response({"detail": "Тест уже успешно пройден."}, status=status.HTTP_400_BAD_REQUEST)

        attempts_count = TrainingAttempt.objects.filter(user=user, material=test.material).count()
        if attempts_count >= self.MAX_ATTEMPTS:
            return Response(
                {"detail": "Лимит в 3 попытки исчерпан. Обратитесь к администратору."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        ok, st, msg = test_availability(user, test)
        if not ok:
            return Response({"detail": msg, "status": st}, status=status.HTTP_403_FORBIDDEN)

        answers_payload = request.data.get("answers") or {}
        if not isinstance(answers_payload, dict):
            return Response({"detail": "Некорректный формат ответов."}, status=status.HTTP_400_BAD_REQUEST)

        questions = list(test.questions.prefetch_related("answers").order_by("order", "id"))
        score, max_score, breakdown = grade_full_test(questions, answers_payload)
        pct = int(round(100 * score / max_score)) if max_score else 0
        threshold = test.pass_threshold_percent or 90
        passed = pct >= threshold

        attempt = TrainingAttempt.objects.create(
            user=user,
            material=test.material,
            score=score,
            max_score=max_score,
            passed=passed,
            responses=answers_payload,
            breakdown=breakdown,
        )

        progress_reset = 0
        if not passed and test.reset_all_training_progress_on_fail:
            progress_reset = reset_all_user_progress(user)

        if passed:
            total_slides = max(test.material.slides.count(), 1)
            TrainingProgress.objects.update_or_create(
                user=user,
                material=test.material,
                defaults={
                    "completed_slides": total_slides,
                    "total_slides": total_slides,
                    "is_completed": True,
                },
            )

        data = TrainingAttemptSerializer(attempt).data
        data.pop("breakdown", None)
        data.pop("responses", None)
        data["max_attempts"] = self.MAX_ATTEMPTS
        data["attempts_used"] = attempts_count + 1
        data["pass_threshold_percent"] = threshold
        data["percent"] = pct
        data["review"] = build_trainee_review(breakdown)
        data["progress_reset"] = progress_reset
        return Response(data, status=status.HTTP_201_CREATED)


class TrainingStatsView(APIView):
    """
    Статистика по обучению сотрудников (для администратора/владельца).
    """

    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        if not is_training_admin(request.user):
            return Response({"detail": "Нет доступа"}, status=status.HTTP_403_FORBIDDEN)

        User = get_user_model()
        users = User.objects.filter(is_active=True).order_by("username")
        materials = list(TrainingMaterial.objects.all())
        total_materials = len(materials)

        stats = []
        for u in users:
            user_progress = TrainingProgress.objects.filter(user=u)
            completed_count = user_progress.filter(is_completed=True).count()
            percent = int(round((completed_count / total_materials) * 100)) if total_materials > 0 else 0

            attempts = TrainingAttempt.objects.filter(user=u).select_related("material")
            attempts_data = TrainingAttemptSerializer(attempts, many=True).data

            stats.append(
                {
                    "user_id": u.id,
                    "username": u.username,
                    "full_name": f"{u.first_name} {u.last_name}".strip() or u.username,
                    "completed_materials": completed_count,
                    "total_materials": total_materials,
                    "percent": percent,
                    "attempts": attempts_data,
                }
            )

        return Response(stats)
