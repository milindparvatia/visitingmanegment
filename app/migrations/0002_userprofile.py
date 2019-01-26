# Generated by Django 2.1.4 on 2019-01-24 09:00

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserProfile',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('mobile', models.CharField(max_length=20)),
                ('licenseplate', models.CharField(max_length=20)),
                ('about', models.CharField(max_length=50, null=True)),
                ('comment', models.CharField(max_length=100, null=True)),
                ('profile_pic', models.ImageField(blank=True, upload_to='profile_pic')),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='app.Map')),
                ('user', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]