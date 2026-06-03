from django.db import models
from django.conf import settings


class SchedulePeriod(models.Model):
    """Период (месяц) для проставления смен."""
    year = models.PositiveIntegerField('Год')
    month = models.PositiveSmallIntegerField('Месяц')
    is_open = models.BooleanField(
        'Открыт для сотрудников',
        default=False,
        help_text='Разрешено ли сотрудникам проставлять смены',
    )
    updated_at = models.DateTimeField('Обновлено', auto_now=True)
    updated_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='schedule_period_updates',
        verbose_name='Кто изменил',
    )

    class Meta:
        unique_together = ('year', 'month')
        ordering = ['-year', '-month']
        verbose_name = 'период графика'
        verbose_name_plural = 'периоды графика'

    def __str__(self):
        return f'{self.month:02d}.{self.year}'


class HouseholdSupplyRequest(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='household_requests',
        verbose_name='Сотрудник',
    )
    pvz_address = models.CharField('ПВЗ', max_length=255)
    item_1 = models.CharField('Позиция 1', max_length=255, blank=True)
    item_2 = models.CharField('Позиция 2', max_length=255, blank=True)
    item_3 = models.CharField('Позиция 3', max_length=255, blank=True)
    item_4 = models.CharField('Позиция 4', max_length=255, blank=True)
    item_5 = models.CharField('Позиция 5', max_length=255, blank=True)
    created_at = models.DateTimeField('Создано', auto_now_add=True)

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'заявка на хоз.нужды'
        verbose_name_plural = 'заявки на хоз.нужды'

    def __str__(self):
        return f'{self.user} — {self.pvz_address}'


class Schedule(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='Сотрудник',
    )
    date = models.DateField('Дата')
    shifts = models.DecimalField('Смены', max_digits=4, decimal_places=2, default=0.0)
    comment = models.TextField('Комментарий', blank=True)
    pvz_address = models.CharField('ПВЗ', max_length=255)
    updated_at = models.DateTimeField('Обновлено', auto_now=True)

    class Meta:
        unique_together = ("user", "date")
        verbose_name = 'смена'
        verbose_name_plural = 'смены'

    def __str__(self):
        return f"{self.user} - {self.date}"
