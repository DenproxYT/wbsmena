from rest_framework import permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import generics
from django.contrib.auth import get_user_model
from django.utils import timezone

from apps.accounts.views import is_accounts_admin
from .models import SiteAnnouncement, UserNotification, Feedback
from .serializers import (
    UserNotificationSerializer,
    AnnouncementCreateSerializer,
    FeedbackSerializer,
    FeedbackCreateSerializer,
)

User = get_user_model()


class NotificationListView(generics.ListAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = UserNotificationSerializer

    def get_queryset(self):
        return UserNotification.objects.filter(
            user=self.request.user
        ).select_related('announcement')


class NotificationUnreadCountView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        count = UserNotification.objects.filter(
            user=request.user, read_at__isnull=True
        ).count()
        return Response({'count': count})


class NotificationMarkReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, pk):
        try:
            n = UserNotification.objects.get(pk=pk, user=request.user)
        except UserNotification.DoesNotExist:
            return Response({'detail': 'Не найдено'}, status=status.HTTP_404_NOT_FOUND)
        if not n.read_at:
            n.read_at = timezone.now()
            n.save(update_fields=['read_at'])
        return Response(UserNotificationSerializer(n).data)


class NotificationMarkAllReadView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        UserNotification.objects.filter(
            user=request.user, read_at__isnull=True
        ).update(read_at=timezone.now())
        return Response({'detail': 'ok'})


class AnnouncementBroadcastView(APIView):
    """Администратор отправляет уведомление всем активным сотрудникам."""
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        if not is_accounts_admin(request.user):
            return Response({'detail': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)
        ser = AnnouncementCreateSerializer(data=request.data)
        ser.is_valid(raise_exception=True)
        announcement = SiteAnnouncement.objects.create(
            title=ser.validated_data['title'],
            message=ser.validated_data['message'],
            created_by=request.user,
        )
        users = User.objects.filter(is_active=True).exclude(
            role__in=('administrator', 'owner')
        )
        if not users.exists():
            users = User.objects.filter(is_active=True)
        deliveries = [
            UserNotification(user=u, announcement=announcement)
            for u in users
        ]
        UserNotification.objects.bulk_create(deliveries, ignore_conflicts=True)
        return Response({
            'id': announcement.id,
            'recipients': len(deliveries),
        }, status=status.HTTP_201_CREATED)


class FeedbackListCreateView(generics.ListCreateAPIView):
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return FeedbackCreateSerializer
        return FeedbackSerializer

    def get_queryset(self):
        if is_accounts_admin(self.request.user):
            return Feedback.objects.select_related('user').all()
        return Feedback.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class FeedbackDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = FeedbackSerializer

    def get_queryset(self):
        if is_accounts_admin(self.request.user):
            return Feedback.objects.all()
        return Feedback.objects.filter(user=self.request.user)

    def patch(self, request, *args, **kwargs):
        if not is_accounts_admin(request.user):
            return Response({'detail': 'Нет доступа'}, status=status.HTTP_403_FORBIDDEN)
        instance = self.get_object()
        if request.data.get('status') == 'reviewed':
            instance.status = 'reviewed'
            instance.save(update_fields=['status'])
        return Response(FeedbackSerializer(instance).data)
