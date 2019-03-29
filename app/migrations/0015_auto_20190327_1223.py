# Generated by Django 2.1.7 on 2019-03-27 12:23

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0014_auto_20190321_1747'),
    ]

    operations = [
        migrations.AlterField(
            model_name='user',
            name='user_type',
            field=models.CharField(choices=[('1', 'Employees'), ('2', 'Receptionist'), ('3', 'Admin')], default='', max_length=20),
        ),
    ]