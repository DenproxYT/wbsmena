from django.conf import settings
from django.db import models


class SiteAnnouncement(models.Model):
    """Сообщение от администратора (рассылка всем сотрудникам)."""
    title = models.CharField('Заголовок', max_length=200)
    message = models.TextField('Текст')
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name='announcements_created',
        verbose_name='Автор',
    )
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'рассылка'
        verbose_name_plural = 'рассылки'

    def __str__(self):
        return self.title


class UserNotification(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='notifications',
        verbose_name='Пользователь',
    )
    announcement = models.ForeignKey(
        SiteAnnouncement,
        on_delete=models.CASCADE,
        related_name='deliveries',
        verbose_name='Рассылка',
    )
    read_at = models.DateTimeField('Прочитано', null=True, blank=True)

    class Meta:
        ordering = ['-announcement__created_at']
        unique_together = [('user', 'announcement')]
        verbose_name = 'уведомление'
        verbose_name_plural = 'уведомления'

    @property
    def is_read(self):
        return self.read_at is not None


class Feedback(models.Model):
    CATEGORY_CHOICES = [
        ('bug', 'Баг'),
        ('wish', 'Пожелания'),
        ('question', 'Вопрос'),
        ('other', 'Другое'),
    ]
    STATUS_CHOICES = [
        ('new', 'Новое'),
        ('reviewed', 'Просмотрено'),
    ]

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='feedbacks',
        verbose_name='Пользователь',
    )
    category = models.CharField('Категория', max_length=20, choices=CATEGORY_CHOICES)
    comment = models.TextField('Комментарий')
    attachment = models.ImageField(
        'Вложение (фото)',
        upload_to='feedback/%Y/%m/',
        blank=True,
        null=True,
    )
    status = models.CharField('Статус', max_length=20, choices=STATUS_CHOICES, default='new')
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'обратная связь'
        verbose_name_plural = 'обратная связь'

    def __str__(self):
        return f'{self.get_category_display()} — {self.user.username}'
