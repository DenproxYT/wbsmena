from django.contrib.auth import get_user_model
from .models import SiteAnnouncement, UserNotification

User = get_user_model()


def broadcast_to_employees(title: str, message: str, created_by=None):
    announcement = SiteAnnouncement.objects.create(
        title=title,
        message=message,
        created_by=created_by,
    )
    users = User.objects.filter(is_active=True).exclude(
        role__in=('administrator', 'owner')
    )
    if not users.exists():
        users = User.objects.filter(is_active=True)
    UserNotification.objects.bulk_create([
        UserNotification(user=u, announcement=announcement) for u in users
    ], ignore_conflicts=True)
    return announcement


def broadcast_to_users(*, title: str, message: str, users, created_by=None):
    announcement = SiteAnnouncement.objects.create(
        title=title,
        message=message,
        created_by=created_by,
    )
    UserNotification.objects.bulk_create(
        [UserNotification(user=u, announcement=announcement) for u in users],
        ignore_conflicts=True,
    )
    return announcement
