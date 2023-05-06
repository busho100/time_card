# Generated by Django 4.2 on 2023-04-29 07:49

from django.conf import settings
from django.db import migrations, models
from django.contrib.auth.models import User
from django.utils import timezone

def set_default_timestamp(apps, schema_editor):
    MonthlyAttendance = apps.get_model("time_card", "MonthlyAttendance")
    for ma in MonthlyAttendance.objects.all():
        ma.timestamp = timezone.now()
        ma.save()


class Migration(migrations.Migration):

    dependencies = [
        ('time_card', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='monthlyattendance',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_timestamp),
    ]

class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('time_card', '0001_initial'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='attendance',
            options={},
        ),
        migrations.AlterModelOptions(
            name='monthlyattendance',
            options={},
        ),
        migrations.AlterUniqueTogether(
            name='monthlyattendance',
            unique_together=set(),
        ),
        migrations.AddField(
            model_name='attendance',
            name='attendance_date',
            field=models.DateField(null=True),
        ),
        migrations.AddField(
            model_name='attendance',
            name='total_work_time',
            field=models.DurationField(blank=True, null=True),
        ),
        migrations.AlterUniqueTogether(
            name='attendance',
            unique_together={('user', 'attendance_date')},
        ),
        migrations.AddField(
            model_name='monthlyattendance',
            name='timestamp',
            field=models.DateTimeField(auto_now_add=True),
            preserve_default=False,
        ),
        migrations.RunPython(set_default_timestamp),
    ]
