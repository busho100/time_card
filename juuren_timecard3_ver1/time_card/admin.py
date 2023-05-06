from django.contrib import admin
from .models import Attendance, MonthlyAttendance

# Register your models here.
admin.site.register(Attendance)
admin.site.register(MonthlyAttendance)