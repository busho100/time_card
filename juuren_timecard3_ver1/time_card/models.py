from django.db import migrations,models
from django.contrib.auth.models import User, Group
from django.utils import timezone
from datetime import timedelta

class TimeCard(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    login_id = models.CharField(max_length=50, unique=True)
    clock_in_time = models.DateTimeField(blank=True, null=True)
    clock_out_time = models.DateTimeField(blank=True, null=True)

class Attendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    attendance_date = models.DateField(null=True)
    attendance_time = models.DateTimeField(null=True) 
    check_in = models.DateTimeField(null=True, blank=True)
    check_out = models.DateTimeField(null=True, blank=True)
    total_work_time = models.DurationField(null=True, blank=True)

    class Meta:
        unique_together = ("user", "attendance_date")

    def save(self, *args, **kwargs):
        if self.check_in and self.check_out:
            self.total_work_time = self.check_out - self.check_in
        else:
            self.total_work_time = None
        super().save(*args, **kwargs)


class MonthlyAttendance(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    group = models.ForeignKey(Group, on_delete=models.CASCADE)
    year = models.IntegerField()
    month = models.IntegerField()
    total_work_time = models.IntegerField(default=0)
    timestamp = models.DateTimeField(auto_now_add=True)
    is_start_of_day = models.BooleanField(default=False)

    class Meta:
        ordering = ['-timestamp']

    @classmethod
    def create_monthly_attendance(cls, user):
        group = user.groups.first()
        if not group:
            return None
        now = timezone.now()
        year_month = (now.replace(day=1) - timezone.timedelta(days=11)).date()
        if now.day < 11:
            year_month = (now.replace(day=1) - timezone.timedelta(days=11)).date()
        else:
            year_month = (now.replace(day=1) + timezone.timedelta(days=20)).date()
        monthly_attendance, created = cls.objects.get_or_create(user=user, group=group, year_month=year_month)
        if not created:
            return None
        return monthly_attendance


class User(models.Model):
    # 必要に応じて、他のフィールドを追加してもよい。
    last_check_in = models.DateTimeField(null=True, blank=True)

    @property
    def end_of_day(self):
        next_day = self.timestamp + timezone.timedelta(days=1)
        end_of_day = timezone.datetime.combine(next_day.date(), timezone.datetime.min.time(), tzinfo=timezone.utc)
        return end_of_day

    @property
    def start_of_day(self):
        start_of_day = timezone.datetime.combine(self.timestamp.date(), timezone.datetime.min.time(), tzinfo=timezone.utc)
        return start_of_day

    @property
    def work_time(self):
        if not self.is_start_of_day:
            return None
        end_of_day = self.end_of_day
        next_attendance = self.user.monthlyattendance_set.filter(timestamp__gte=end_of_day, is_start_of_day=True).order_by('timestamp').first()
        if next_attendance is None:
            return end_of_day - self.start_of_day
        return next_attendance.timestamp - self.start_of_day
    

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