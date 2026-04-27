from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='steamprofile',
            name='project_role',
            field=models.CharField(
                choices=[
                    ('player', 'Игрок'),
                    ('paid_admin', 'Покупная админка'),
                    ('sponsor', 'Спонсор'),
                    ('trainee', 'Стажёр'),
                    ('moderator', 'Модератор'),
                    ('senior_moderator', 'Старший модератор'),
                    ('administrator', 'Администратор'),
                    ('senior_administrator', 'Старший администратор'),
                    ('curator', 'Куратор'),
                    ('developer', 'Разработчик'),
                ],
                db_index=True,
                default='player',
                max_length=32,
                verbose_name='Роль проекта',
            ),
        ),
        migrations.AddField(
            model_name='steamprofile',
            name='balance_rub',
            field=models.DecimalField(
                decimal_places=2,
                default=0,
                max_digits=10,
                verbose_name='Баланс, ₽',
            ),
        ),
    ]