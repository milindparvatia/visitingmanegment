# Generated by Django 2.1.7 on 2019-03-12 07:21

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0004_user_user_location'),
    ]

    operations = [
        migrations.AddField(
            model_name='meeting',
            name='timer',
            field=models.CharField(choices=[('5', '5 min'), ('10', '10 min'), ('0', 'let them in')], default='', max_length=15),
        ),
    ]
