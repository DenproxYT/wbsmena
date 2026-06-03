from django.contrib.auth import get_user_model
from django.db.models import Q

from .models import SiteAnnouncement, UserNotification
from .realtime import publish_users

User = get_user_model()


def _default_employee_queryset():
    qs = User.objects.filter(is_active=True).exclude(
        role__in=('administrator', 'owner')
    )
    if not qs.exists():
        qs = User.objects.filter(is_active=True)
    return qs


def resolve_recipient_users(pvz_addresses=None, user_ids=None):
    """Получатели: все сотрудники, выбранные ПВЗ и/или конкретные люди."""
    pvz_addresses = [p.strip() for p in (pvz_addresses or []) if p and str(p).strip()]
    user_ids = [int(uid) for uid in (user_ids or []) if uid]

    if not pvz_addresses and not user_ids:
        return list(_default_employee_queryset())

    q = Q()
    if pvz_addresses:
        q |= Q(pvz_address__in=pvz_addresses)
    if user_ids:
        q |= Q(pk__in=user_ids)
    return list(
        User.objects.filter(is_active=True).filter(q).distinct()
    )


def deliver_announcement(announcement, users):
    deliveries = [
        UserNotification(user=u, announcement=announcement) for u in users
    ]
    if deliveries:
        UserNotification.objects.bulk_create(deliveries, ignore_conflicts=True)
        publish_users(
            [u.id for u in users],
            'notification',
            {'announcement_id': announcement.id},
        )
    return deliveries


def broadcast_to_employees(title: str, message: str, created_by=None, pvz_addresses=None, user_ids=None):
    announcement = SiteAnnouncement.objects.create(
        title=title,
        message=message,
        created_by=created_by,
    )
    users = resolve_recipient_users(pvz_addresses=pvz_addresses, user_ids=user_ids)
    deliver_announcement(announcement, users)
    return announcement, users


def broadcast_to_users(*, title: str, message: str, users, created_by=None):
    """Уведомление выбранным пользователям (например, при изменении смены)."""
    announcement = SiteAnnouncement.objects.create(
        title=title,
        message=message,
        created_by=created_by,
    )
    user_list = list(users)
    deliver_announcement(announcement, user_list)
    return announcement
