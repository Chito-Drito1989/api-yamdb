# Generated manually: код подтверждения не хранится в БД (токен через default_token_generator).

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0002_user_confirmation_code_alter_user_bio_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='user',
            name='confirmation_code',
        ),
    ]
