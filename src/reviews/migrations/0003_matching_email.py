# Generated by Django 3.1.5 on 2021-01-24 06:43

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('reviews', '0002_matching'),
    ]

    operations = [
        migrations.AddField(
            model_name='matching',
            name='email',
            field=models.EmailField(default='None', max_length=254),
        ),
    ]
