# Generated by Django 2.1.7 on 2019-03-21 17:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0013_auto_20190317_1110'),
    ]

    operations = [
        migrations.AlterField(
            model_name='visitor',
            name='email',
            field=models.EmailField(max_length=255),
        ),
    ]
