# Generated by Django 2.1.5 on 2022-05-22 07:38

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('UserApp', '0002_auto_20220522_0725'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='username',
            field=models.CharField(max_length=12, null=True, unique=True),
        ),
    ]