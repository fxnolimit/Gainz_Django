# Generated by Django 2.2.4 on 2020-07-08 01:05

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0002_auto_20200707_1804'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exercise',
            name='workout',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='of_workout', to='app.Workout'),
        ),
        migrations.AlterField(
            model_name='workout',
            name='user',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='of_user', to=settings.AUTH_USER_MODEL),
        ),
    ]
