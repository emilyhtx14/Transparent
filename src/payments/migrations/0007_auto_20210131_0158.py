# Generated by Django 3.1.5 on 2021-01-31 01:58

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('payments', '0006_bookupload'),
    ]

    operations = [
        migrations.AlterField(
            model_name='bookupload',
            name='picture',
            field=models.ImageField(upload_to='img/%y'),
        ),
    ]
