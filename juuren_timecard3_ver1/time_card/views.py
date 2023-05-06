from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import render, get_object_or_404, redirect
from django.urls import reverse_lazy
from django.views import generic
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.db.models import Sum
from django.views.generic.base import TemplateView
from datetime import datetime
from .models import Attendance, MonthlyAttendance
from .forms import AttendanceForm, MonthlyAttendanceForm


@login_required
def home(request):
    user_id = request.user.id
    # 前回の出勤時刻をセッションから取得
    last_check_in = request.session.get('last_check_in')
    if request.method == 'POST':
        form = AttendanceForm(request.user, request.POST)
        if form.is_valid():
            attendance = form.save(commit=False)
            attendance.user_id = user_id
            attendance.attendance_date = attendance.check_in.date()
            # 前回の出勤時刻をセッションに保存
            request.session['last_check_in'] = attendance.check_in.strftime('%Y-%m-%d %H:%M:%S')
            attendance.save()
            return redirect('home')
    else:
        # 前回の出勤時刻があれば、フォームに初期値として設定
        initial_data = {}
        if last_check_in:
            initial_data['check_in'] = last_check_in
        form = AttendanceForm(request.user, initial=initial_data)
    context = {
        'form': form,
        'attendances': Attendance.objects.filter(user_id=user_id).order_by('-attendance_time'),
    }
    return render(request, 'time_card/home.html', context)


class AttendanceCreateView(LoginRequiredMixin, generic.CreateView):
    model = Attendance
    form_class = AttendanceForm
    success_url = reverse_lazy('attendance_list')
    template_name = 'attendance/attendance.html'

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super().form_valid(form)

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        kwargs['user'] = self.request.user
        return kwargs

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['attendances'] = Attendance.objects.filter(user=self.request.user).order_by('-attendance_date', '-check_in', '-check_out')
        return context

@login_required
def attendance(request):
    user = request.user
    last_logout_time = request.session.get('last_logout_time', None)
    last_attendance_time = request.session.get('last_attendance_time', None)
    check_in = request.session.get('check_in')

    if request.method == 'POST':
        form = AttendanceForm(request.user, request.POST)
        if form.is_valid():
            attendance_instance = form.save(commit=False)
            attendance_instance.user = request.user
            # attendance_instance.attendance_date = datetime.now().date()
            attendance.clock_in_time = request.session.get('clock_in_time')
            attendance_instance.save()
            messages.success(request, '打刻が完了しました')
            print(form.cleaned_data)
            
            if form.cleaned_data['attendance_type'] == 'check_in':
                request.session['last_attendance_time'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                request.session['check_in'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
            else:
                request.session['last_logout_time'] = datetime.now().strftime('%Y/%m/%d %H:%M:%S')
                request.session['check_in'] = None
            messages.success(request, '出勤・退勤の打刻を保存しました。')
            return redirect('time_card:attendance')
        else:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.error(request, f"{field}: {error}")
    else:
        # initial_values = {}
        # if check_in:
        #     initial_values['check_in'] = check_in
        # if last_attendance_time:
        #     initial_values['check_out'] = last_attendance_time
        # form = AttendanceForm(user, initial=initial_values)
        form = AttendanceForm(user)
    attendances = Attendance.objects.filter(user=user, attendance_date=datetime.now().date()).order_by('-check_in')
    context = {
        'form': form,
        'attendances': attendances,
    }
    return render(request, 'attendance.html', context)


@login_required
def monthly_attendance(request):
    user = request.user
    if request.method == 'POST':
        form = MonthlyAttendanceForm(user, request.POST)
        if form.is_valid():
            group = form.cleaned_data['group']
            year = form.cleaned_data['year']
            month = form.cleaned_data['month']
            start_date = datetime(year, month, 11)
            end_date = datetime(year, month % 12 + 1, 10)
            monthly_attendance, created = MonthlyAttendance.objects.get_or_create(
                user=user,
                group=group,
                year=year,
                month=month,
                defaults={
                    'is_start_of_day': True
                }
            )
            if not created:
                monthly_attendance.is_start_of_day = True
                monthly_attendance.save()
                Attendance.objects.filter(user=user, check_in__gte=start_date, check_in__lte=end_date).delete()
                request.session.pop('last_attendance_time', None)
            attendances = Attendance.objects.filter(user=user, check_in__gte=start_date, check_in__lte=end_date)
            total_work_time = attendances.aggregate(Sum('work_time'))
            context = {
                'form': form,
                'attendances': attendances,
                'total_work_time': total_work_time['work_time__sum'],
            }
            return render(request, 'monthly_attendance.html', context)


class ProfileView(LoginRequiredMixin, TemplateView):
    template_name = 'profile.html'

