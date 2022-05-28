# Generated by Django 2.1.5 on 2022-05-25 16:36

from django.db import migrations, models
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0011_notification'),
    ]

    operations = [
        migrations.AddField(
            model_name='notification',
            name='noti_time',
            field=models.DateTimeField(auto_now_add=True, default=django.utils.timezone.now),
            preserve_default=False,
        ),
    ]
