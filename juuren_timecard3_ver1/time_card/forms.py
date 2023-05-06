from django import forms
from django.contrib.auth.models import Group
from .models import Attendance, MonthlyAttendance
import datetime


class AttendanceForm(forms.ModelForm):
    attendance_type = forms.ChoiceField(choices=(("IN", "出勤"), ("OUT", "退勤")), error_messages={'required': '出勤区分は必須です。'})

    class Meta:
        model = Attendance
        fields = ["attendance_type", "check_in", "check_out"]
        widgets = {
            'work_date': forms.DateInput(attrs={'type': 'date'}),
            'start_time': forms.TimeInput(attrs={'type': 'time'}),
            'end_time': forms.TimeInput(attrs={'type': 'time'}),
        }

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user

    def clean(self):
        cleaned_data = super().clean()
        attendance_type = cleaned_data.get('attendance_type')
        check_in = cleaned_data.get('check_in')
        check_out = cleaned_data.get('check_out')
        if check_in and check_out and check_out < check_in:
            raise forms.ValidationError('退勤時間は出勤時間よりも後に設定してください。')
        if not attendance_type:
            raise forms.ValidationError('出勤区分は必須です。')
        return cleaned_data

    def save(self, commit=True):
        attendance = super().save(commit=False)
        attendance.user = self.user
        attendance.attendance_date = attendance.check_in.date()
        attendance.save()
        return attendance


class MonthlyAttendanceForm(forms.ModelForm):
    group = forms.ModelChoiceField(queryset=Group.objects.all(), empty_label=None)

    class Meta:
        model = MonthlyAttendance
        fields = ['group', 'year', 'month']
        

    def __init__(self, user, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user = user
        self.fields['group'].queryset = user.groups.all()

    def clean(self):
        cleaned_data = super().clean()
        year = cleaned_data.get('year')
        month = cleaned_data.get('month')
        if year is not None and month is not None:
            start_date = f"{year}-{month:02d}-11"
            end_date = f"{year}-{month+1:02d}-10"
            start_date = datetime.datetime.strptime(start_date, '%Y-%m-%d').date()
            end_date = datetime.datetime.strptime(end_date, '%Y-%m-%d').date()
            if start_date > end_date:
                raise forms.ValidationError('開始日は終了日より前に設定してください。')
        return cleaned_data

    def save(self, commit=True):
        monthly_attendance = super().save(commit=False)
        monthly_attendance.user = self.user
        monthly_attendance.is_start_of_day = True
        monthly_attendance.save()
        return monthly_attendance