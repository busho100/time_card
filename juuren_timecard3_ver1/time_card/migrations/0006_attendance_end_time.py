# Generated by Django 4.2 on 2023-05-05 05:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('time_card', '0005_attendance_start_time'),
    ]

    operations = [
        migrations.AddField(
            model_name='attendance',
            name='end_time',
            field=models.DateTimeField(blank=True, null=True),
        ),
    ]