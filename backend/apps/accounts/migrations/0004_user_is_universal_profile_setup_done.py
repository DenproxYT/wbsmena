from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0003_alter_user_options_alter_user_is_intern_and_more'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='is_universal',
            field=models.BooleanField(default=False, verbose_name='Универсал (работает на всех ПВЗ)'),
        ),
        migrations.AddField(
            model_name='user',
            name='profile_setup_done',
            field=models.BooleanField(default=False, verbose_name='ПВЗ и роль заданы при первом входе'),
        ),
    ]
