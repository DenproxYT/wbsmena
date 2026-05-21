from django.db import models
from django.contrib.auth.models import AbstractUser

class User(AbstractUser):
    phone_number = models.CharField('Телефон', max_length=15, unique=True)
    pvz_address = models.CharField('Адрес ПВЗ', max_length=255)
    is_intern = models.BooleanField('Стажёр', default=True)
    role_choices = [
        ('intern', 'Стажёр'),
        ('staff_manager', 'Штатный менеджер'),
        ('chief_manager', 'Главный менеджер'),
        ('administrator', 'Администратор'),
        ('owner', 'Владелец'),
    ]
    role = models.CharField('Роль', max_length=20, choices=role_choices, default='intern')
    must_change_credentials = models.BooleanField(
        'Требуется смена пароля при входе',
        default=False,
    )

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'

    def __str__(self):
        return self.get_full_name() or self.username

    def save(self, *args, **kwargs):
        # Признак стажёра должен зависеть только от роли.
        self.is_intern = self.role == "intern"
        super().save(*args, **kwargs)
